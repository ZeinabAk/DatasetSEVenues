import subprocess  
import os
from os import path
from sqlalchemy import create_engine
import shutil
from NLPfucntions import *
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

engine =  create_engine('postgresql://'+params['user']+':'+params['password']+'@'+params['host']+':5432/'+params['database'])
conn = engine.connect()


count=0
conferences=conn.execute("SELECT * FROM venues"+ConditionVenue+";")
for conf in conferences:  
    Cpath = dbPaths+'/cermineXML/'+conf['acronym']
    pdfpath=dbPaths+'/pdf/'+conf['acronym']
    if not path.exists(Cpath):
        os.mkdir(Cpath)
    result_set=conn.execute("SELECT id, title, ee, year, doi FROM papers WHERE venue_id="+str(conf['id'])+ConditionYear+";")
    for paper in result_set: 
        try:
            if paper['doi']!=None:
                doi=paper['ee'][0].replace("https://doi.org/", "", 1)
                doi=doi.replace("http://doi.ieeecomputersociety.org/", "", 1).replace("/", "\\", 2)
                filename=doi
                if (not path.exists(os.path.join(Cpath,filename+".cermxml"))) & (not path.exists(os.path.join(Cpath,filename+".pdf"))):  
                    try:
                        filename=filename+'.pdf'
                        count=count+1
                        shutil.copy(os.path.join(pdfpath,str(filename)), Cpath)
                    except Exception as e:   
                        #count=count+1
                        pass
            else:
                count=count+1
        except Exception as e:
            count=count+1 
            print(e)
                
print('number of not found pdfs:',count)



print('Running Cermine')
conferences=conn.execute("SELECT * FROM venues;")
for conf in conferences:  
    Cpath = dbPaths+'/cermineXML/'+conf['acronym']
    #print(conf['acronym'])
    drun="-cp cermine.jar pl.edu.icm.cermine.ContentExtractor -path " +Cpath
    #subprocess.call(['java'] + drun.split())
    
    
    
    
#delete processed pdf files from conf
conferences=conn.execute("SELECT * FROM venues;")
count=0
tcount=0
for conf in conferences:  
    dbPath = dbPaths+'/cermineXML/'+conf['acronym']
    for fname in os.listdir(dbPath):
        if fname.endswith('.cermxml'):
            fname=fname.replace("/", "\\", 2)
            fname=fname.replace(".cermxml", '.pdf', 1)
            if os.path.exists(os.path.join(dbPath,fname)):
                os.remove(os.path.join(dbPath,fname))
        if fname.endswith('.images'):
            shutil.rmtree(os.path.join(dbPath,fname))
    for fname in os.listdir(dbPath):
        if fname.endswith('.pdf'):
            count=count+1
            
    if count>0:
        tcount=count+tcount
        #print(dbPath, count)
    count=0  
    
print("The conf pdf files that was not parsed by Cermine:", tcount)    