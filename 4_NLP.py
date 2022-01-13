from os import path
import ast, re
import random 
import psycopg2
from NLPfucntions import *
#loadNltk()

import argparse
from NLPfucntions import config

pparser = argparse.ArgumentParser()
pparser.add_argument('--dir', required=True, help='directory')
pparser.add_argument('--venue', required=False, help='venue name')
pparser.add_argument('--year', required=False, help='specify year')
pparser.add_argument('--Maxyear', required=False, help='specify upper limit year')
pparser.add_argument('--Minyear', required=False, help='specify lower limit year')
args = pparser.parse_args()
dbPaths=args.dir
venue=args.venue
year=args.year
Maxyear=args.Maxyear
Minyear=args.Minyear
#get database parameter
params = config()
if not venue is None:
    ConditionVenue=" where acronym='"+str(venue)+"'"
else:
    ConditionVenue=''
if not year is None:
    ConditionYear=" and year='"+str(year)+"'"
else:
    ConditionYear=''
if not Maxyear is None:
    ConditionYear+=" and year<='"+str(Maxyear)+"'"
if not Minyear is None:
    ConditionYear+=" and year>='"+str(Minyear)+"'" 
try:
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM venues"+ConditionVenue+";")
    confs=cursor.fetchall()
    total=0
    for conf in confs:
        count=0
        ngramList=[]
        confName=conf[1] 
        CTpath=dbPaths+'/cermineText/'+confName 
        #if confName!=venue:
            #continue
        query="SELECT id, doi,title FROM papers l WHERE venue_id="+ str(conf[0])+" and NOT EXISTS (SELECT  paper_id FROM ngrams WHERE  paper_id = l.id)"+ConditionYear+";"
        cursor.execute(query)
        paper_records = cursor.fetchall()
        rem=len(paper_records)
        total=total+rem
        print(confName,'remaining',rem)
        for paper in paper_records:
            try:
                filename=paper[1].replace("/", "\\", 2)
                fname=os.path.join(CTpath,filename+".txt")
                if (path.exists(fname)) :
                    try:
                        with open(fname) as f: 
                            contents = f.read()
                            ngramList=word_frequency(contents,paper[0])
                            bulkInsert(ngramList,connection)
                            count=count+1
                            if count%10==0:
                                print(count, 'out of', rem)
                    except Exception as e:
                        print('1',e)
                        pass
            except Exception as e:
                pass
        
    print(total,'remaining papers')
except (Exception, psycopg2.Error) as error:
    print("Error while fetching data from PostgreSQL", error)
finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        #print("PostgreSQL connection is closed")
