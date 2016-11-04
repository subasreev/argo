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

class Deleter(object):
    def __init__(self, collection_name):
        self.collection_name = collection_name
    # Returns list of statements to execute.
    def get_sql(self, use_im, use_argo1):
        if use_argo1:
            if use_im:
                return ["DELETE FROM argo_" + self.collection_name
                        + "_data WHERE objid IN (SELECT objid FROM argo_im)"]
            else:
                return ["DELETE FROM argo_" + self.collection_name + "_data"]
        else:
            if use_im:
                return ["DELETE FROM argo_" + self.collection_name
                            + "_str WHERE objid IN (SELECT objid FROM argo_im)",
                        "DELETE FROM argo_" + self.collection_name
                            + "_num WHERE objid IN (SELECT objid FROM argo_im)",
                        "DELETE FROM argo_" + self.collection_name
                            + "_bool WHERE objid IN (SELECT objid FROM argo_im)"]
            else:
                return ["DELETE FROM argo_" + self.collection_name + "_str",
                        "DELETE FROM argo_" + self.collection_name + "_num",
                        "DELETE FROM argo_" + self.collection_name + "_bool"]
