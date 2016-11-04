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
import dbms_postgres
import argodb

# Set to false to use Argo/3, true to use Argo/1.
USE_ARGO_1 = False

def get_db():
    # Edit the line below with your own configuration options.
    conn = psycopg2.connect("user='postgres' password='postgres' dbname='argo'")
    dbms = dbms_postgres.PostgresDBMS(conn)
    return argodb.ArgoDB(dbms, USE_ARGO_1)
