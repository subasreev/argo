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

import sys
import sql_parser

class IncompatibleType(Exception):
    def __str__(self):
        return "Attempted to insert an object whose type is not JSON-compatible"

class Collection(object):
    def __init__(self, db, collection_name):
        self.db = db
        self.name = collection_name
    def insert(self, obj):
        if isinstance(obj, dict):
            connection = self.db.dbms.connection
            cursor = connection.cursor()
            try:
                objid = self.db.dbms.get_new_id(self.name)
                self.insert_object_helper(cursor, objid, "", obj)
                cursor.close()
                connection.commit()
            except IncompatibleType:
                cursor.close()
                connection.rollback()
                raise
        else:
            raise IncompatibleType()
    def select(self, sql_text):
        query = sql_parser.parser.parse(sql_text)
        if query.collection_name != self.name:
            print >> sys.stderr, ("WARNING: Collection name in SELECT statement different "
                                  + "from name of collection select() was called on")
        return query.execute(self.db)
    def insert_object_helper(self, cursor, objid, keyprefix, obj):
        if isinstance(obj, basestring):
            self.insert_string_value(cursor, objid, keyprefix, obj)
        elif isinstance(obj, bool):
            if obj:
                self.insert_bool_value(cursor, objid, keyprefix, True)
            else:
                self.insert_bool_value(cursor, objid, keyprefix, False)
        elif isinstance(obj, int) or isinstance(obj, long) or isinstance(obj, float):
            self.insert_number_value(cursor, objid, keyprefix, obj)
        elif isinstance(obj, list):
            for (idx, list_item) in enumerate(obj):
                self.insert_object_helper(cursor,
                                          objid,
                                          keyprefix + "[" + str(idx) + "]",
                                          list_item)
        elif isinstance(obj, dict):
            if len(keyprefix) > 0:
                prekey = keyprefix + "."
            else:
                prekey = ""
            for (subkey, subval) in obj.iteritems():
                self.insert_object_helper(cursor, objid, prekey + subkey, subval)
        else:
            raise IncompatibleType()

class SingleTableCollection(Collection):
    def __init__(self, db, collection_name, create = False):
        super(SingleTableCollection, self).__init__(db, collection_name)
        if create:
            self.db.dbms.init_collection(self.name, True)
            self.db.dbms.init_indexes(self.name, True)
    def insert_string_value(self, cursor, objid, key, value):
        if self.db.dbms.qmark_style:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_data (objid, keystr, valstr) VALUES (?, ?, ?)",
                           (objid, key, value))
        else:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_data (objid, keystr, valstr) VALUES (%s, %s, %s)",
                           (objid, key, value))
    def insert_number_value(self, cursor, objid, key, value):
        if self.db.dbms.qmark_style:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_data (objid, keystr, valnum) VALUES (?, ?, ?)",
                           (objid, key, value))
        else:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_data (objid, keystr, valnum) VALUES (%s, %s, %s)",
                           (objid, key, value))
    def insert_bool_value(self, cursor, objid, key, value):
        if self.db.dbms.qmark_style:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_data (objid, keystr, valbool) VALUES (?, ?, ?)",
                           (objid, key, value))
        else:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_data (objid, keystr, valbool) VALUES (%s, %s, %s)",
                           (objid, key, value))

class ThreeTableCollection(Collection):
    def __init__(self, db, collection_name, create = False):
        super(ThreeTableCollection, self).__init__(db, collection_name)
        if create:
            self.db.dbms.init_collection(self.name, False)
            self.db.dbms.init_indexes(self.name, False)
    def insert_string_value(self, cursor, objid, key, value):
        if self.db.dbms.qmark_style:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_str (objid, keystr, valstr) VALUES (?, ?, ?)",
                           (objid, key, value))
        else:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_str (objid, keystr, valstr) VALUES (%s, %s, %s)",
                           (objid, key, value))
    def insert_number_value(self, cursor, objid, key, value):
        if self.db.dbms.qmark_style:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_num (objid, keystr, valnum) VALUES (?, ?, ?)",
                           (objid, key, value))
        else:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_num (objid, keystr, valnum) VALUES (%s, %s, %s)",
                           (objid, key, value))
    def insert_bool_value(self, cursor, objid, key, value):
        if self.db.dbms.qmark_style:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_bool (objid, keystr, valbool) VALUES (?, ?, ?)",
                           (objid, key, value))
        else:
            cursor.execute("INSERT INTO argo_"
                               + self.name + "_bool (objid, keystr, valbool) VALUES (%s, %s, %s)",
                           (objid, key, value))
