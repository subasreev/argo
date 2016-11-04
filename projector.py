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


# Projector Interface: objects shall have properties:
#     - collection_name: The name of the collection to project from.
# And methods:
#     - get_argo1_sql(use_im): Generate full SQL query text for Argo/1
#     - get_argo3_sql(use_im): Generate full SQL query text for Argo/3
#     - get_argo1_params(): Get query parameters for Argo/1
#     - get_argo3_params(): Get query parameters for Argo/3

class StarProjector(object):
    def __init__(self, collection_name):
        self.collection_name = collection_name
    def get_argo1_sql(self, use_im):
        if use_im:
            return ("SELECT * FROM argo_" + self.collection_name
                    + "_data WHERE objid IN (SELECT objid FROM argo_im) ORDER BY objid")
        else:
            return "SELECT * FROM argo_" + self.collection_name + "_data ORDER BY objid"
    def get_argo3_sql(self, use_im):
        if use_im:
            return ("((SELECT objid, keystr, valstr, CAST (NULL AS DOUBLE PRECISION), "
                        + "CAST (NULL AS BOOLEAN) FROM argo_" + self.collection_name
                        + "_str WHERE objid IN (SELECT objid FROM argo_im)) "
                    + "UNION (SELECT objid, keystr, CAST (NULL AS TEXT), valnum, "
                        + "CAST (NULL AS BOOLEAN) FROM argo_" + self.collection_name
                        + "_num WHERE objid IN (SELECT objid FROM argo_im)) "
                    + "UNION (SELECT objid, keystr, CAST (NULL AS TEXT), "
                        + "CAST (NULL AS DOUBLE PRECISION), valbool FROM argo_"
                        + self.collection_name
                        + "_bool WHERE objid IN (SELECT objid FROM argo_im))) "
                    + "ORDER BY objid")
        else:
            return ("((SELECT objid, keystr, valstr, CAST (NULL AS DOUBLE PRECISION), "
                        + "CAST (NULL AS BOOLEAN) FROM argo_" + self.collection_name + "_str) "
                    + "UNION (SELECT objid, keystr, CAST (NULL AS TEXT), valnum, "
                        + "CAST (NULL AS BOOLEAN) FROM argo_" + self.collection_name + "_num) "
                    + "UNION (SELECT objid, keystr, CAST (NULL AS TEXT), "
                        + "CAST (NULL AS DOUBLE PRECISION), valbool FROM argo_"
                        + self.collection_name + "_bool)) "
                    + "ORDER BY objid")
    def get_argo1_params(self):
        return []
    def get_argo3_params(self):
        return []

class ListProjector(object):
    def __init__(self, collection_name):
        self.collection = collection_name
        self.keys = []
    def add_key(self, key):
        self.keys.append(key)
    def get_argo1_sql(self, use_im):
        if len(self.keys) > 0:
            suffix = self.get_per_table_sql_suffix(use_im)
            return ("SELECT * FROM argo_" + self.collection_name + "_data" + suffix
                    + " ORDER BY objid")
        else:
            helper = StarProjector(self.collection_name)
            return helper.get_argo1_sql(use_im)
    def get_argo3_sql(self, use_im):
        if len(self.keys) > 0:
            suffix = self.get_per_table_sql_suffix(use_im)
            return ("((SELECT objid, keystr, valstr, CAST (NULL AS DOUBLE PRECISION), "
                        + "CAST (NULL AS BOOLEAN) FROM argo_" + self.collection_name + "_str"
                        + suffix + ") "
                    + " UNION (SELECT objid, keystr, CAST (NULL AS TEXT), valnum, "
                        + "CAST (NULL AS BOOLEAN) FROM argo_" + self.collection_name + "_num"
                        + suffix + ") "
                    + " UNION (SELECT objid, keystr, CAST (NULL AS TEXT), "
                        + "CAST (NULL AS DOUBLE PRECISION), valbool FROM argo_"
                        + self.collection_name + "_bool" + suffix + ")) "
                    + "ORDER BY objid")
        else:
            helper = StarProjector(self.collection_name)
            return helper.get_argo1_sql(use_im)
    def get_per_table_sql_suffix(self, use_im):
        if use_im:
            suffix = " WHERE objid IN (SELECT objid FROM argo_im) AND ("
        else:
            suffix = " WHERE ("
        for idx, key in enumerate(self.keys):
            suffix += "keystr = %s OR keystr LIKE %s OR keystr LIKE %s"
            if (idx != len(self.keys) - 1):
                suffix += " OR "
        suffix += ")"
        return suffix
    def get_argo1_params(self):
        params = []
        for key in self.keys:
            params.append(key)
            params.append(key + ".%")
            params.append(key + "[%")
        return params
    def get_argo3_params(self):
        params = self.get_argo1_params()
        return params + params + params
