import subprocess  
import os.path
from os import path
from sqlalchemy import create_engine
import ast
import argparse
from globalFucntions import config

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
#get database parameter
params = config()
#use PyPaperBot to download papers  https://github.com/ZeinabAk/PyPaperBot
program_name = "PyPaperBot" 
command = [program_name] 
engine =  create_engine('postgresql://'+params['user']+':'+params['password']+'@'+params['host']+':5432/'+params['database'])
conn = engine.connect()
count=0
tcount=0

conferences=conn.execute("SELECT * FROM venues"+ConditionVenue+";")
for conf in conferences:  
    pdfpath = dbPaths+'/pdf/'+conf['acronym']
    if not path.exists(pdfpath):
        os.mkdir(pdfpath)   
    result_set=conn.execute("SELECT id,doi, ee FROM papers WHERE venue_id="+str(conf['id'])+ConditionYear+";")

    for paper in result_set: 
        tcount=tcount+1
        try:
            doi=paper['ee'][0].replace("https://doi.org/", "", 1)
            doi=doi.replace("http://doi.ieeecomputersociety.org/", "", 1)
            filename=doi
            if not path.exists(os.path.join(pdfpath, doi.replace("/", "\\")+'.pdf')):
                count=count+1
                arguments = ["--doi="+filename,"--dwn-dir="+pdfpath, "--scihub-mirror=https://sci-hub.se"] 
                command.extend(arguments) 
                #output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0] 
        except Exception as e:
            count=count+1
            pass

print('Number of papers that are not downloaded:',count,'out of', tcount)