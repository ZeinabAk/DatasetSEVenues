from sqlalchemy import Column, ForeignKey, Table, Index
from sqlalchemy import Integer, String, Boolean,TIMESTAMP,ARRAY,TEXT
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint
Base = declarative_base()
metadata = Base.metadata


class Venue(Base):
    __tablename__ = 'venues'
    id = Column(Integer, primary_key=True)
    acronym = Column(String(20), nullable=False)
    name = Column(String(200))
    type = Column(String(20))
    UniqueConstraint(acronym, name='uix_1')
    def __init__(self, acronym, name, vtype):
        self.acronym = acronym
        self.name = name
        self.type = vtype
        
    def __repr__(self):
        return "<Venue('%s')>" % (self.acronym)
    
    
class Paper(Base):
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey('venues.id'),index=True)
    authors=Column(ARRAY(String(506)))
    year = Column(Integer)
    title = Column(TEXT)
    pages = Column(ARRAY(String(10)))
    length=Column(Integer)
    ee=Column(ARRAY(String(500)))
    volume=Column(ARRAY(String(100)))
    crossref=Column(ARRAY(String(500)))
    url=Column(ARRAY(String(500)))
    genre=Column(String(100))
    doi=Column(TEXT)
    UniqueConstraint(title, venue_id, doi, name='uix_2')

    '''One to many Venues<->Paper'''
    venue = relationship("Venue", backref=backref('papers', order_by=id))
    def __init__(self, venue,author_names, year, title, pages, length, ee,crossref,volume,url,genre,doi):
        self.venue = venue
        self.authors=author_names
        self.year = year
        self.title = title
        self.pages = pages
        self.length = length
        self.ee=ee
        self.crossref=crossref
        self.volume=volume
        self.url=url
        self.genre=genre
        self.doi=doi
    
    Index('index_venue',venue_id)
    def __repr__(self):
        return "<Paper('%s, %d, %s')>" % (self.venue, self.year, self.title)

class NGram(Base):
    __tablename__ = 'ngrams'
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey('papers.id'),index=True)
    ngram=Column(TEXT)
    ngram_count = Column(Integer)
    term_freq = Column(Integer)
    

    '''One to many ngrams<->Paper'''
    paper = relationship("Paper", backref=backref('ngrams', order_by=id))
    def __init__(self, paper,ngram, ngram_count, term_freq):
        self.paper = paper
        self.ngram=ngram
        self.ngram_count=ngram_count
        self.term_freq = term_freq
    Index('index_paper', paper_id)
    def __repr__(self):
        return "<Ngram('%s, %d, %s')>" % (self.paper)       
    
def initDB(engine):
    metadata.create_all(engine) 
    print ('Database structure created')
       
    
def cleanStart(engine):
    meta = MetaData(bind=engine)

    '''Reflect: get the tables currently in the database''' 
    meta.reflect(engine)
    '''Drop all tables (fresh start)'''
    meta.drop_all(engine)
    print( 'Database structure reset')
