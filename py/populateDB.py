from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import sessionmaker
import os,json
from initDB import Paper, Venue
from initDB import initDB, cleanStart
from initDB import Base
import argparse
import sqlalchemy as db
from sqlalchemy.sql import exists   
from sqlalchemy.sql import select
from sqlalchemy import and_, or_, not_



def getConfName(conf):
    if conf=='fse':
        return [x.lower() for x in ['ESEC / SIGSOFT FSE','ESEC/SIGSOFT FSE','SIGSOFT FSE']]
    if conf=='saner':
        return [x.lower() for x in ['SANER','CSMR-WCRE']]
    return [conf.lower()]

def getJournalName(abvr):
    j= {     
'SPE':'Softw. Pract. Exp.',
'REJ': 'Requir. Eng.',
'ESE' :'Empir. Softw. Eng.'  ,
'SOSYM'  :  'Softw. Syst. Model.',
'SQJ' :'Softw. Qual. J.',
'ISSE' :'Innov. Syst. Softw. Eng.',
'IJSEKE' :'Int. J. Softw. Eng. Knowl. Eng.',
'NOTES': 'ACM SIGSOFT Softw. Eng. Notes',
'JSS' :'J. Syst. Softw.',
'SPE' :'Softw. Pract. Exp.',
'STVR':'Softw. Test. Verification Reliab.',
'ASEJ':'Autom. Softw. Eng.',
'TSE':'IEEE Trans. Software Eng.',
'TOSEM' :'ACM Trans. Softw. Eng. Methodol.' ,
 'SW':'IEEE Softw.'   ,
 'IST' :'Inf. Softw. Technol.',
'SMR':  'J. Softw. Evol. Process.'
       }
    
    return j[abvr]





conferences = ['ASE', 'ESEM', 'FASE', 'FSE', 'GPCE', 'ICPC', 'ICSE', 'ICSM', 'ICSME', 'ICST',
'ISSTA', 'MODELS', 'MSR', 'RE', 'SANER', 'SCAM', 'SSBSE', 'WCRE']


#conferences = ['issta','icst','ssbse','esem','re','mdls']
#journals=['tosem','jss','esem','tse','j-ase']
journals=['ASEJ', 'ESE', 'IJSEKE', 'ISSE', 'IST', 'JSS', 'REJ', 'NOTES',
 'SMR', 'SOSYM', 'SPE', 'SQJ', 'STVR', 'SW', 'TOSEM', 'TSE']

# Conference impact computed for the entire period 2000-2013
# http://shine.icomp.ufam.edu.br/index.php


Cname = {
    'ICSE':'International Conference on Software Engineering', 
    'ICSM':'IEEE International Conference on Software Maintenance', 
    'WCRE':'Working Conference on Reverse Engineering',
    'MSR':'Working Conference on Mining Software Repositories',
    'ICSME':'International Conference on Software Maintenance and Evolution',
    'ASE':'IEEE/ACM International Conference on Automated Software Engineering',
    'SCAM':'International Working Conference on Source Code Analysis & Manipulation',
    'ICPC':'IEEE International Conference on Program Comprehension',
    'FSE':'ACM SIGSOFT Symposium on the Foundations of Software Engineering',
    'SANER':'IEEE International Conference on Software Analysis, Evolution and Reengineering',
    'FASE':  'Fundamental Approaches to Software Engineering',
    'GPCE': 'Generative Programming and Component Engineering',
    'ISSTA': 'International Symposium on Software Testing and Analysis',
    'ICST': 'IEEE International Conference on Software Testing, Verification and Validation',
    'SSBSE': 'International Symposium on Search Based Software Engineering' ,
    'ESEM': 'International Symposium on Empirical Software Engineering and Measurement',
    'RE': 'IEEE International Requirements Engineering Conference',
    'MODELS': 'International Conference On Model Driven Engineering Languages And Systems'

}
Jname={
    
'SOSYM' :'Software and System Modeling',
'REJ' :'Requirements Engineering Journal' ,
'ESE' :'Empirical Software Engineering',
'SQJ' :'Software Quality Journal' ,
'IST': 'Information and Software Technology' ,
'ISSE': 'Innovations in Systems and Software Engineering' ,
'IJSEKE': 'International Journal of Software Engineering and Knowledge Engineering', 
'NOTES': 'ACM SIGSOFT Software Engineering Notes' ,
'SPE' :'Software: Practice and Experience' ,
'STVR': 'Software Testing, Verification and Reliability',
'TSE': 'IEEE - Transactions on Software Engineering',
'TOSEM': 'ACM - Transactions on Software Engineering Methodology',
'ESE':'Springer - Empirical Software Engineering' ,
'JSS':'Elsevier - Journal of Systems and Software',
'ASEJ':'Automated Software Engineering',
'SW': 'IEEE Software'   , 
'SMR': 'Journal of Software: Evolution and Process'

   
}    

pparser = argparse.ArgumentParser()
pparser.add_argument('--input', required=True, help='input file')
pparser.add_argument('--db', required=True, help='database name')
args = pparser.parse_args()
dbname=args.db
inputfile=args.input

engine = create_engine('postgresql://zeinabak:spirals@localhost:5432/'+dbname)
if database_exists(engine.url):
    print('database exists')
    conn = engine.connect()
    
else:
    engine = create_engine('postgresql://zeinabak:spirals@localhost:5432/')
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("create database "+dbname+";")
    initDB(engine)
    


#engine = create_engine('mysql://root@localhost/conferences?charset=utf8')

# Reset the database (drop all tables)
#cleanStart(engine)

# Create the table structure
#initDB(engine)


# Create an engine and get the metadata
#Base = declarative_base(engine)
metadata = Base.metadata

# Create a session for this conference
Session = sessionmaker(engine)
session = Session()


print('Loading papers:')
file = open(inputfile, 'r')
reader = file.readlines()
count=0


for conferenceAcro in conferences:
    Pcount=0
    # Create a new conference object
    qvenue = session.query(Venue).filter(Venue.acronym == conferenceAcro.upper()).first()
    cAcro=conferenceAcro.lower()
    if not qvenue:
        venue = Venue(conferenceAcro.upper(),Cname[conferenceAcro.upper()],'conference')
        session.add(venue)
    else:
        venue=qvenue

    for row in reader:
        # Deconstruct each row of papers table
        publication=json.loads(row)
        if ("author" in publication.keys()) & ("booktitle" in publication.keys()):
            

            if publication['booktitle'].lower() in getConfName(cAcro):   
                try:
                    if cAcro in ['iscm','icst']:
                        if not str('/'+cAcro+'/') in publication['crossref'][0]:
                            continue
                    year = int(publication['year'])
                    author_names = publication['author']
                    title = publication['title']
                    try:
                        pages = publication['pages']
                    except:
                        pages = None     
                    try:
                        ee = publication['ee']
                    except:
                        ee = None
                    try:
                        url = publication['url']
                    except:
                        url = None
                    crossref=publication['crossref']
                    genre=publication['genre']
                    try:
                        doi=ee[0].replace("https://doi.org/", "", 1)
                        doi=doi.replace("http://doi.ieeecomputersociety.org/", "", 1)
                        #doi=doi.replace("/", "\\", 2)
                    except:
                        doi = None

                    paperExists=session.query(Paper).filter(and_(Paper.title == title, Paper.venue_id == venue.id, Paper.year == year)).first()

                    if not paperExists:
                        paper = Paper(venue,author_names, year, title, pages,None, ee,crossref,None,url,genre,doi)
                                    
                        session.add(paper)
                    Pcount=Pcount+1
                except Exception as e:
                    print('1',e)
                
    print(conferenceAcro.upper(), Pcount) 
    
    
    
    
    
    
    
    
  #================================================  
    
    

for journalAcro in journals:
    Pcount=0
    count=count+1
    # Create a new journal object
    qvenue = session.query(Venue).filter(Venue.acronym == journalAcro.upper()).first()

    if not qvenue:
        venue = Venue(journalAcro.upper(), Jname[journalAcro.upper()],'journal')
        session.add(venue)
    else:
        venue=qvenue
        
    for row in reader:
        # Deconstruct each row of articl table
        publication=json.loads(row)
        if ("journal" in publication.keys()) :
            #if publication['journal']==journal:
            if publication['journal']== getJournalName(journalAcro.upper()):
                try:
                    year = int(publication['year'])
                    try:
                        author_names = publication['author']
                    except:
                        author_names = None

                    title = publication['title']
                    try:
                        pages = publication['pages']
                    except:
                        pages = None     
                    try:
                        ee = publication['ee']
                    except:
                        ee = None
                    try:
                        url = publication['url']
                    except:
                        url = None
                    volume=publication['volume']
                    genre=publication['genre']
                    try:
                        doi=ee[0].replace("https://doi.org/", "", 1)
                        doi=doi.replace("http://doi.ieeecomputersociety.org/", "", 1)
                        #doi=doi.replace("/", "\\", 2)
                    except:
                        doi = None

                    paperExists=session.query(Paper).filter(and_(Paper.title == title, Paper.venue_id == venue.id, Paper.year == year)).first()
                        
                    if not paperExists:
                        paper = Paper(venue,author_names, year, title, pages, None,ee,None,volume,url,genre,doi)
                        session.add(paper)
                        #Pcount=Pcount+1
                        #break
                    Pcount=Pcount+1
                except Exception as e:
                    print('2',e)
    print(journalAcro.upper(), Pcount) 



try:
    session.commit()
except Exception as e:
    print('except2',e)
    session.rollback()
    
conn.close()

print( 'Finished loading data')




    
