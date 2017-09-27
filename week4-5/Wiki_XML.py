#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 14:25:47 2017

@author: Laurent Vermue (lauve@dtu.dk)
"""
import xml.etree.ElementTree as ET
import time
import re
from bz2file import BZ2File
import sqlite3
from psutil import virtual_memory

# Possibility to take memory into account(Machine optimization)
mem = virtual_memory()
mem.available

# Defining filepaths
filepath="/Users/lousy12/"
filename="enwiki-20170820-pages-articles-multistream.xml.bz2"
database_name="Articles.db"


# Creating or connecting to the database
conn = sqlite3.connect(filepath+database_name)
c = conn.cursor()
# Create table
c.execute('''CREATE TABLE IF NOT EXISTS Articles
             (Ident INTEGER PRIMARY KEY, Article VARCHAR(10))''')

# Opening the BZ2-File
file=BZ2File(filepath+filename)

#Setting some pretext for the tags of the xml file
pretext="{http://www.mediawiki.org/xml/export-0.10/}"
#Creating the dictionary
index={}
#Creating a iterable parse object with ElementTree
context = ET.iterparse(file, events=('end',))

#Counting time
start=time.time()   
i=0 
for event, elem in context:
    if elem.tag == pretext+"page":
        text=elem[-1].find(pretext+'text').text.replace('\n', '').lower()
        c.executemany("INSERT INTO Articles(Article) VALUES (?)",[(text,)])
        # Check the last row_id
        article_position=c.lastrowid
        for word in set(re.split('\W+',text)):
            if word in index.keys():
                index[word].append(article_position)
            else:
                index[word]=[article_position]
        i+=1
    if i==10000:
        break
    elem.clear

end=time.time()
print("Finished in time: {:.2f}s".format(end-start))

conn.commit()
c.close()

'''
def search(substr):
    result = []
    for key in dictionary:
        if substr in key:
            result.append((key, dictionary[key]))   
    return result
set(sum([index[k] for k in index if "a" in k],[]))
set.intersection(set1,set2,set3)
'''
