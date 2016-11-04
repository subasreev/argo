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

import collection
import sql_parser

class ArgoDB(object):
    def __init__(self, dbms, use_argo1):
        self.dbms = dbms
        self.use_argo1 = use_argo1
    def get_collection(self, collection_name):
        if self.dbms.collection_exists(collection_name):
            if self.use_argo1:
                return collection.SingleTableCollection(self, collection_name, False)
            else:
                return collection.ThreeTableCollection(self, collection_name, False)
        else:
            if self.use_argo1:
                return collection.SingleTableCollection(self, collection_name, True)
            else:
                return collection.ThreeTableCollection(self, collection_name, True)
    def execute_sql(self, sql_text):
        query = sql_parser.parser.parse(sql_text) #, debug=1)
        if not self.dbms.collection_exists(query.collection_name):
            if self.use_argo1:
                collection.SingleTableCollection(self, query.collection_name, True)
            else:
                collection.ThreeTableCollection(self, query.collection_name, True)
        return query.execute(self)
