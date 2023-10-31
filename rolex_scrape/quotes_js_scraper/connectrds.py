
import psycopg2
import boto3
import pandas as pd
import sqlalchemy as sa

ENDPOINT="rds-endpoint"
PORT="5432"
USER="postgres"
REGION="us-east-2a"
DBNAME="postgres"

#gets the credentials from .aws/credentials
session = boto3.Session(profile_name='default')
client = session.client('rds',region_name='us-east-2a')

token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)

try:
    conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password='postgres', sslrootcert="SSLCERTIFICATE")
    conn.autocommit = True
    cur = conn.cursor()

    engine = sa.create_engine('postgresql://postgres:postgres@wcc-db.c6fuq7pku230.us-east-2.rds.amazonaws.com:5432/postgres')

    #set up connection to push data from pandas to postgres
    df = pd.read_json('../Data/rolex_test_scrape.json')
    
    #rename image_urls column to image_url
    df.rename(columns={'image_urls':'image_url'},inplace=True)
    df.to_sql('rolex',engine,if_exists='replace',dtype=sa.types.JSON)
   

    #check that data is in table
    # sql3 = """select * from rolex Limit 10"""
    # cur.execute(sql3)
    # query_results = cur.fetchall()
    # print(query_results)

except Exception as e:
        print('There was an error: {}'.format(e))

                