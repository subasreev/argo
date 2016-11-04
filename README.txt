Argo Alpha 1
Copyright (c) 2011-2013 by Craig Chasseur (AKA Timothy Craig Chasseur, Jr.)

This software is covered by the GPLv3 license. See COPYING for details.


This software provides a minimal interactive Argo/SQL shell packed by a
PostgreSQL database. It depends on Python 2.6 or 2.7 and the Python packages
PLY (Python Lexx-Yacc) and Psycopg2 (a Python driver for connecting to
PostgreSQL databases). Before running Argo, you should create a database named
"argo" in your PostgreSQL installation. You should also edit the file
demo_init.py to set any connection parameters you need to connect to your
PostgreSQL server.

Run demoshell.py to launch the Argo/SQL shell. Commands are of the form:

INSERT INTO collection_name OBJECT { ... };
SELECT ... FROM collection_name WHERE ... ;
DELETE FROM collection_name WHERE ...;

For more information on supported Argo/SQL statements and implementation
details, see the paper "Enabling JSON Document Stores in Relational Systems"
by Chasseur, Li, and Patel.
