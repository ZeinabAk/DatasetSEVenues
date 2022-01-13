import subprocess  
import os
from os import path
from sqlalchemy import create_engine
import shutil
from globalFucntions import *
import argparse


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
#use PyPaperBot to download papers  https://github.com/ZeinabAk/PyPaperBot
program_name = "PyPaperBot" 
command = [program_name] 
engine =  create_engine('postgresql://'+params['user']+':'+params['password']+'@'+params['host']+':5432/'+params['database'])
conn = engine.connect()

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
    
    
count=0
Tcount=0
confs=conn.execute("SELECT * FROM venues"+ConditionVenue+";")
for conf in confs:
    Cpath=dbPaths+'/cermineXML/'+conf['acronym']
    CTpath=dbPaths+'/cermineText/'+conf['acronym']
    pdfpath=dbPaths+'/pdf/'+conf['acronym']
    if not path.exists(CTpath):
        os.makedirs(CTpath)
        
    result_set=conn.execute("SELECT id, title, ee, year, doi FROM papers WHERE venue_id="+str(conf['id'])+ConditionYear+";")
    for paper in result_set: 
        try:
            doi=paper['ee'][0].replace("https://doi.org/", "", 1)
            doi=doi.replace("http://doi.ieeecomputersociety.org/", "", 1).replace("/", "\\", 2)
            fname=doi
            if not path.exists(os.path.join(Cpath,fname+".cermxml")): 
                continue
            Tcount=Tcount+1 
            try:
                if not path.exists(os.path.join(CTpath,fname+".txt")): 
                    try:
                        paragraph=cermineText(Cpath,fname)
                        if (paragraph!=None) &  (len(paragraph)>300):
                            with open(os.path.join(CTpath,fname+".txt"), 'w') as f:
                                f.write(paragraph) 
                        else:
                            count=count+1
                    except Exception as e:
                        print('1',e)
                        count=count+1
                        pass
            except Exception as e:
                print('2',e)
                count=count+1
                pass
        except Exception as e:
            print('3',e)
            pass  
                    
print(count,'papers out of',Tcount,'can\'t be extracted')