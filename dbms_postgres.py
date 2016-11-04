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

import psycopg2

class PostgresDBMS(object):
    def __init__(self, connection):
        self.connection = connection
        self.qmark_style = False
    def collection_exists(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM pg_class WHERE relname = %s",
                       ("argo_" + name + "_seq",))
        if cursor.fetchone()[0] == 0:
            cursor.close()
            return False
        else:
            cursor.close()
            return True
    def init_collection(self, name, use_argo1 = False):
        cursor = self.connection.cursor()
        cursor.execute("CREATE SEQUENCE argo_" + name + "_seq")
        if use_argo1:
            cursor.execute("""
                CREATE TABLE argo_""" + name + """_data(
                    objid BIGINT NOT NULL,
                    keystr TEXT NOT NULL,
                    valstr TEXT NULL,
                    valnum DOUBLE PRECISION NULL,
                    valbool BOOLEAN NULL
                )""")
        else:
            cursor.execute("""
                CREATE TABLE argo_""" + name + """_str(
                    objid BIGINT NOT NULL,
                    keystr TEXT NOT NULL,
                    valstr TEXT NOT NULL
                )""")
            cursor.execute("""
                CREATE TABLE argo_""" + name + """_num(
                    objid BIGINT NOT NULL,
                    keystr TEXT NOT NULL,
                    valnum DOUBLE PRECISION NOT NULL
                )""")
            cursor.execute("""
                CREATE TABLE argo_""" + name + """_bool(
                    objid BIGINT NOT NULL,
                    keystr TEXT NOT NULL,
                    valbool BOOLEAN NOT NULL
                )""")
        self.connection.commit()
        cursor.close()
    def init_indexes(self, name, use_argo1 = False):
        cursor = self.connection.cursor()
        if use_argo1:
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_objid ON argo_""" + name + """_data (objid)""")
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_key ON argo_""" + name + """_data (keystr)""")
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_valstr ON argo_""" + name + """_data (valstr)""")
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_valnum ON argo_""" + name + """_data (valnum)""")
        else:
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_str_objid ON argo_""" + name + """_str (objid)""")
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_str_key ON argo_""" + name + """_str (keystr)""")
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_str_val ON argo_""" + name + """_str (valstr)""")

            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_num_objid ON argo_""" + name + """_num (objid)""")
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_num_key ON argo_""" + name + """_num (keystr)""")
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_num_val ON argo_""" + name + """_num (valnum)""")

            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_bool_objid ON argo_""" + name + """_bool (objid)""")
            cursor.execute("""CREATE INDEX argo_""" + name
                           + """_idx_bool_key ON argo_""" + name + """_bool (keystr)""")
        self.connection.commit()
        cursor.close()
    def get_new_id(self, collectionName):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT nextval(%s)""", ("argo_" + collectionName + "_seq",))
        new_id = cursor.fetchone()[0]
        self.connection.commit()
        cursor.close()
        return new_id
