#!/usr/bin/env python2

#   Copyright (c) 2011-2013, Craig Chasseur.
#
#   This file is part of Argo.
#
#   Argo is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Argo is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Argo.  If not, see <http://www.gnu.org/licenses/>.

import deleter

class InsertQuery(object):
    def __init__(self, collection_name, json_object):
        self.collection_name = collection_name
        self.json_object = json_object
    def execute(self, db):
        db.get_collection(self.collection_name).insert(self.json_object)
        return []

class CopyQuery(object):
    def __init__(self, collection_name, json_file):
        self.collection_name = collection_name
        self.json_file = json_file
    def execute(self, db):
        db.get_collection(self.collection_name).copy(self.json_file)
        print "copied ", self.collection_name, " ", self.json_file
        return []

class DeleteQuery(object):
    def __init__(self, collection_name, predicate = None):
        self.collection_name = collection_name
        self.deleter = deleter.Deleter(self.collection_name)
        self.predicate = predicate
        if self.predicate:
            self.predicate.set_collection_name(self.collection_name)
    def execute(self, db):
        connection = db.dbms.connection
        cursor = connection.cursor()
        if (self.predicate):
            cursor.execute("DROP TABLE IF EXISTS argo_im")
            if db.use_argo1:
                cursor.execute("CREATE TEMPORARY TABLE argo_im AS "
                                   + self.predicate.get_argo1_sql(),
                               self.predicate.params)
            else:
                cursor.execute("CREATE TEMPORARY TABLE argo_im AS "
                                   + self.predicate.get_argo3_sql(),
                               self.predicate.params)
            delete_statements = self.deleter.get_sql(True, db.use_argo1)
        else:
            delete_statements = self.deleter.get_sql(False, db.use_argo1)
        for statement in delete_statements:
            cursor.execute(statement)
        connection.commit()
        cursor.close()
        return []

class SelectQuery(object):
    def __init__(self, collection_name, projector, predicate = None):
        self.collection_name = collection_name
        self.projector = projector
        self.predicate = predicate
        self.projector.collection_name = self.collection_name
        if self.predicate:
            self.predicate.set_collection_name(self.collection_name)
    def execute(self, db):
        cursor = db.dbms.connection.cursor()
        if self.predicate:
            cursor.execute("DROP TABLE IF EXISTS argo_im")
            if db.use_argo1:
                cursor.execute("CREATE TEMPORARY TABLE argo_im AS "
                                   + self.predicate.get_argo1_sql(),
                               self.predicate.params)
                cursor.execute(self.projector.get_argo1_sql(True),
                               self.projector.get_argo1_params())
            else:
                cursor.execute("CREATE TEMPORARY TABLE argo_im AS "
                                   + self.predicate.get_argo3_sql(),
                               self.predicate.params)
                cursor.execute(self.projector.get_argo3_sql(True),
                               self.projector.get_argo3_params())
        else:
            if db.use_argo1:
                cursor.execute(self.projector.get_argo1_sql(False),
                               self.projector.get_argo1_params())
            else:
                cursor.execute(self.projector.get_argo3_sql(False),
                               self.projector.get_argo3_params())
        someresults = False
        valtuple = cursor.fetchone()
        if valtuple:
            someresults = True
            current_flatmap = {}
            current_objid = valtuple[0]
        while valtuple:
            if valtuple[0] != current_objid:
                current_objid = valtuple[0]
                yield self.reconstitute(current_flatmap)
                current_flatmap = {}
            if valtuple[2] != None:
                current_flatmap[valtuple[1]] = valtuple[2]
            elif valtuple[3] != None:
                current_flatmap[valtuple[1]] = valtuple[3]
            elif valtuple[4] != None:
                current_flatmap[valtuple[1]] = valtuple[4]
            valtuple = cursor.fetchone()
        if someresults:
            yield self.reconstitute(current_flatmap)
        cursor.close()
    def reconstitute(self, flatmap):
        reconmap = {}
        for k, v in flatmap.iteritems():
            self.reconstitute_kv(reconmap, k, v)
        return reconmap
    def reconstitute_kv(self, reconmap, key, value):
        dot_pos = key.find(".")
        bracket_pos = key.find("[")
        if (dot_pos == -1) and (bracket_pos == -1):
            reconmap[key] = value
        elif dot_pos >= 0:
            if bracket_pos >= 0:
                if dot_pos < bracket_pos:
                    prekey, postkey = key.split(".", 1)
                    if not reconmap.has_key(prekey):
                        reconmap[prekey] = {}
                    self.reconstitute_kv(reconmap[prekey], postkey, value)
                else:
                    prekey, postfrag = key.split("[", 1)
                    idxstr, postkey = postfrag.split("]", 1)
                    if not reconmap.has_key(prekey):
                        reconmap[prekey] = []
                    self.reconstitute_list(reconmap[prekey], int(idxstr), postkey, value)
            else:
                prekey, postkey = key.split(".", 1)
                if not reconmap.has_key(prekey):
                    reconmap[prekey] = {}
                self.reconstitute_kv(reconmap[prekey], postkey, value)
        else:
            prekey, postfrag = key.split("[", 1)
            idxstr, postkey = postfrag.split("]", 1)
            if not reconmap.has_key(prekey):
                reconmap[prekey] = []
            self.reconstitute_list(reconmap[prekey], int(idxstr), postkey, value)
    def reconstitute_list(self, reconlist, idx, key, value):
        while not (idx < len(reconlist)):
            reconlist.append(None)
        if len(key) == 0:
            reconlist[idx] = value
        elif key[0] == '.':
            if reconlist[idx] == None:
                reconlist[idx] = {}
            self.reconstitute_kv(reconlist[idx], key[1:], value)
        else:
            idxstr, postkey = key[1:].split("]", 1)
            if reconlist[idx] == None:
                reconlist[idx] = []
            self.reconstitute_list(reconlist[idx], int(idxstr), postkey, value)
