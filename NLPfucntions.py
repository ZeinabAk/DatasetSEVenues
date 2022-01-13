import nltk
from nltk.corpus import wordnet
import json,os
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from PyPDF2 import PdfFileReader
porter = PorterStemmer()
lancaster=LancasterStemmer()
import xml.etree.ElementTree as ET
from nltk import word_tokenize
# loading in all the essentials for data manipulation
import pandas as pd
import numpy as np
#load inthe NTLK stopwords to remove articles, preposition and other words that are not actionable
from nltk.corpus import stopwords
# This allows to create individual objects from a bog of words
from nltk.tokenize import word_tokenize
# Lemmatizer helps to reduce words to the base form
from nltk.stem import WordNetLemmatizer
# Ngrams allows to group words in common pairs or trigrams..etc
from nltk import ngrams
# We can use counter to count the objects
from collections import Counter
# This is our visual library
import seaborn as sns
import matplotlib.pyplot as plt
import ast, re
import spacy
from spacy.matcher import Matcher
from collections import Counter
import psycopg2
from configparser import ConfigParser
# load english language model
nlp = spacy.load('en_core_web_sm',disable=['ner','textcat'])



def config(filename='py/database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db



def loadNltk():
    nltk.download('stopwords')
    nltk.download('wordnet')  
    nltk.download('averaged_perceptron_tagger')


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)
def word_frequency(sentence,paper_id):
    # creates tokens, creates lower class, removes numbers and lemmatizes the words
    new_tokens = word_tokenize(sentence)
    new_tokens = [t.lower() for t in new_tokens]
    new_tokens =[t for t in new_tokens if t not in stopwords.words('english')]
    new_tokens = [t for t in new_tokens if t.isalpha()]
    #lemmatizer = WordNetLemmatizer()
   # new_tokens =[lemmatizer.lemmatize(t,get_wordnet_pos(t)) for t in new_tokens]
    #counts the words, pairs and trigrams
    dictC={}
    dictC[1] = Counter(new_tokens)
    dictC[2]= Counter(ngrams(new_tokens,2))
    dictC[3]= Counter(ngrams(new_tokens,3))
    dictC[4]= Counter(ngrams(new_tokens,4))
    dictC[5]= Counter(ngrams(new_tokens,5))
    ngramList=[]
    for item in dictC:
        for key in dictC[item].keys():
            if item==1:
                ngramList.append((paper_id,key,item,dictC[item][key]))
            else:
                ngramList.append((paper_id,' '.join(key),item,dictC[item][key]))
      
    return ngramList



def bulkInsert(records,connection):
    try:
        cursor = connection.cursor()
        sql_insert_query = """ INSERT INTO ngrams (paper_id, ngram, ngram_count,term_freq) 
                           VALUES (%s,%s,%s,%s) """ 
        # executemany() to insert multiple rows
        result = cursor.executemany(sql_insert_query, records)
        connection.commit()
        #print(cursor.rowcount, "Record inserted successfully into mobile table")

    except (Exception, psycopg2.Error) as error:
        print("Failed inserting record into ngram table {}".format(error))

    finally:
        cursor.close()


def returntext(my_string):
    my_string=re.sub("[A-Z a-z]+\\. ", '', my_string)
    my_string=re.sub("[IVXLCDM]+\\. ", '', my_string)
    my_string=re.sub(r'\b\d+((?:\.\d*)?)*\s+', '', my_string)
    my_string=re.sub("[1-9]+\\. ", '', my_string)
    
    return my_string.strip().lower()



    
def getPages(filename,pdfpath):
    fname=os.path.join(pdfpath,filename+".pdf")
    try:
        with open(fname, "rb") as pdf_file:
            pdf_reader = PdfFileReader(pdf_file)
            if pdf_reader.numPages>2:
                return True
            return False
        return False
    except Exception as e:
        print(fname,e)     
    
def getNPages(filename,pdfpath):
    fname=os.path.join(pdfpath,filename+".pdf")
    try:
        with open(fname, "rb") as pdf_file:
            pdf_reader = PdfFileReader(pdf_file)
            return pdf_reader.numPages
    except Exception as e:
        print(fname,e)    
                
                
def cermineText(path, paper):
    #load the data
    contents = open(os.path.join(path, paper+'.cermxml')).read()
    root = ET.fromstring(contents)
    # remove the list of references
    keeper_data = ['back']
    for instance in root:
        if  instance.tag in keeper_data:
            root.remove(instance)
    xmlstr = ET.tostring(root, encoding="unicode")
    # remove reference tags in the text
    paragraph=re.sub('<[^>]*xref[^>]*>', '', xmlstr)
    paragraph=paragraph.replace("\n", "")
    # string to xml
    root = ET.fromstring(paragraph)
    # get the abstract text
    
    extractedText=''
    try:
        abstract = root.findall('.//abstract')[0].find('.//p')
        extractedText=extractedText+str(abstract.text) +" "
    except:
        #print('no abstract')
        pass

    for instance in root:
        if  instance.tag in ['front']:
            root.remove(instance)

    #parent_map = {c:p for p in root.iter( ) for c in p}
    #print(parent_map)
    try:
        for sec in root.find('.//sec/..'):
            for text1 in sec.iter('p'):
                extractedText=extractedText+str(text1.text)+''
    except:
        pass
    return extractedText   



def updateTable(paperId, length, cursor):
    try:
        sql_update_query = """Update papers set length = %s where id = %s"""
        cursor.execute(sql_update_query, (length, paperId))
        connection.commit()
        count = cursor.rowcount

    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
