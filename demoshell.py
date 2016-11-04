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

import demo_init
import json
try:
    import readline
except:
    pass

db = demo_init.get_db()

while True:
    try:
        sql_text = raw_input("Argo> ")
    except EOFError:
        print ""
        break
    try:
        for item in db.execute_sql(sql_text):
            print json.dumps(item)
        print "DONE"
    except Exception, e:
        print "ERROR: " + str(e)
