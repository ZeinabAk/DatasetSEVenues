# DatasetSEVenues


---

### Contents

This is a database of papers for software engineering conferences. It contains more than twenty years of history for each of the following conferences:

- **JSS**, Elsevier - Journal of Systems and Software
- **SW**, IEEE Software
- **ICSE**, International Conference on Software Engineering
- **IST**, Information and Software Technology
- **TSE**, IEEE - Transactions on Software Engineering
- **NOTES**, ACM SIGSOFT Software Engineering Notes
- **ASE**, IEEE/ACM International Conference on Automated Software Engineering
- **SPE**, Software: Practice and Experience
- **FSE**, ACM SIGSOFT Symposium on the Foundations of Software Engineering
- **ICSM**, IEEE International Conference on Software Maintenance
- **IJSEKE**, International Journal of Software Engineering and Knowledge Engineering
- **RE**, IEEE International Requirements Engineering Conference
- **ESE**, Springer - Empirical Software Engineering
- **SOSYM**, Software and System Modeling
- **MSR**, Working Conference on Mining Software Repositories
- **ESEM**, International Symposium on Empirical Software Engineering and Measurement
- **WCRE**, Working Conference on Reverse Engineering
- **ISSTA**, International Symposium on Software Testing and Analysis
- **ICSME**, International Conference on Software Maintenance and Evolution
- **ICPC**, IEEE International Conference on Program Comprehension
- **SMR**, Journal of Software: Evolution and Process
- **SQJ**, Software Quality Journal
- **TOSEM**, ACM - Transactions on Software Engineering Methodology
- **MODELS**, International Conference On Model Driven Engineering Languages And Systems
- **ASEJ**, Automated Software Engineering
- **REJ**, Requirements Engineering Journal
- **SCAM**, International Working Conference on Source Code Analysis & Manipulation
- **ISSE**, Innovations in Systems and Software Engineering
- **GPCE**, Generative Programming and Component Engineering
- **FASE**, Fundamental Approaches to Software Engineering
- **SSBSE**, International Symposium on Search Based Software Engineering







The data is stored in a PostgreSQL database (see the [PostgreSQL Dump](https://github.com/ZeinabAk/ConferencesData/blob/main/db/conferences.sql.gz)) with the following schema:




<img align="center" width="60%" src="https://github.com/ZeinabAk/DatasetSEVenues/blob/main/db/schema.png">




Alternatively, the database can be recreated from CSV files using Python and the SQLAlchemy Object Relational Mapper using the scripts included (more details below).

### Data

- Papers and authors: the [DBLP](http://www.dblp.org/db/) data dump. We used the data in [dblp-2021-11-02.xml](https://dblp.org/xml/release/) file.


## Using the database

### Directly

Most simply, you can import the [SQL dump](https://github.com/ZeinabAk/ConferencesData/blob/main/db/conferences.sql.gz) into your database management system and start querying.

### Via Python

Alternatively, you can take a look at how the database was created using PostgreSQL, Python and SQLAlchemy, and use these mechanisms also for querying. This will allow you to easily extend the database or update its schema.

#### Dependencies and installation instructions 
If you take this path, make sure you have Python and a PostgreSQL server installed before attempting anything.
Follow the follwoing steps  (tested on our OS 11.3 machine with Python 3.7.7):

- Install SQLAlchemy: `easy_install SQLAlchemy`
- Tweek `database.ini` for your particular PostgreSQL user and password (the script assumes user *root* with empty password)

#### Python scripts

- `initDB.py`: declares the database schema using Python classes (will be automatically mapped to tables by SQLAlchemy).
- `populateDB.py`: reads data about the papers for each conference and loads it into the database.
- `1_downloadPdf.py`: download the pdf of the papers using [PyPaperBot](https://github.com/ZeinabAk/PyPaperBot).
- `2_Cermine.py`: Extract the text from the Pdf files into xml files the pdf.
- `3_XmlToText.py`: Transform the XML files into text files.
- `4_Ngrams.py`: Generate n-grams and update the database.

## How to use

Python files arguments:

| Arguments          | Description                                   | Type
| ------------------ | ----------------------------------------------|-----
| \-\-dir            | Directory path in which to save the result    | (str)
| \-\-venue          | The venue you aim to download                 | (str, optional)
| \-\-year           | year of publication, defaults to None         | (int, optional)
| \-\-Maxyear        | maximum year of publication, defaults to None | (int, optional)
| \-\-Minyear        | minimum year of publication, defaults to None | (int, optional)

