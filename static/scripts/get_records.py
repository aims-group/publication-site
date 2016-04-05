#!/bin/python
import MySQLdb as mdb
from db_settings import *

con= mdb.Connection(db=DB, host=DB_HOST, user=DB_USER,passwd=DB_PASSWORD)

with con:
    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("SELECT publication_id FROM publication;")
    rows = cur.fetchall()

    for row in rows:
        
        print 'PUBLICATION_ID ' + str(row["publication_id"])

        cur1 = con.cursor(mdb.cursors.DictCursor)
        cur1.execute("SELECT a.attribute_value as av FROM attribute AS a JOIN publication_has_attribute AS pha WHERE pha.attribute_id = a.attribute_id AND attribute_key = 'doi' AND publication_id = " + str(row["publication_id"]) + ";")
        doi = cur1.fetchone()
        try:
            print doi['av']
        except:
            print 'none'

        cur2 = con.cursor(mdb.cursors.DictCursor)
        cur2.execute("SELECT attribute.display_name as dn FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'experiment' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(row["publication_id"]) + ";")
        experiments = cur2.fetchall()
        print '--EXPERIMENTS--'
        for experiment in experiments:
            print experiment['dn']

        cur3 = con.cursor(mdb.cursors.DictCursor)
        cur3.execute("SELECT attribute.display_name as dn FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'model' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(row["publication_id"]) + ";")
        models = cur3.fetchall()
        print '--MODELS--'
        for model in models:
            print model['dn']

        cur4 = con.cursor(mdb.cursors.DictCursor)
        cur4.execute("SELECT attribute.display_name as dn FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'ensebmle' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(row["publication_id"]) + ";")
        ensebmles = cur4.fetchall()
        print '--ENSEBMLE--'
        for ensebmle in ensebmles:
            print ensebmle['dn']

        cur5 = con.cursor(mdb.cursors.DictCursor)
        cur5.execute("SELECT attribute.display_name as dn FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'variable' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(row["publication_id"]) + ";")
        variables = cur5.fetchall()
        print '--VARIABLES--'
        for variable in variables:
            print variable['dn']

        cur6 = con.cursor(mdb.cursors.DictCursor)
        cur6.execute("SELECT attribute.display_name as dn FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'keyword' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(row["publication_id"]) + ";")
        keywords = cur6.fetchall()
        print '--KEYWORDS--'
        for keyword in keywords:
            print keyword['dn']

        print ""
