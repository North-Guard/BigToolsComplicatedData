#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 14:25:47 2017

@author: Cool Kid
"""
import xml.etree.ElementTree as ET
import time
import re

import pickle
from pathlib import Path

import os
from bz2file import BZ2File
import sqlite3
from psutil import virtual_memory
from datetime import datetime

# Settings
batch_size = 1000

# Possibility to take memory into account (Machine optimization)
mem = virtual_memory()
print("Memory on machine: {:,} B".format(mem.available))

# Defining filepaths
filepath = Path("/")
filename = "enwiki-20170820-pages-articles-multistream.xml.bz2"
database_name = "Articles.db"
output_dir = Path("/")

##########
# Database

# Creating or connecting to the database
database_path = Path(output_dir, database_name)  # Path(filepath, database_name)
print("Connecting to {}".format(database_path))

conn = sqlite3.connect(str(database_path))#
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS Articles
             (Ident INTEGER PRIMARY KEY, Article VARCHAR(10))''')

max_lines = None

##########
# Data access

# Opening the BZ2-File
file_path = Path(filepath, filename)
print("Opening {}".format(file_path))
file = BZ2File(str(file_path))


##########
# Data processing

# Setting some pretext for the tags of the xml file
pretext = "{http://www.mediawiki.org/xml/export-0.10/}"

# Creating the dictionary
print("Create vocabulary set")
vocabulary = set()

#Creating indexes for the article positions
cat_article_line=[]
a_article_line=[]

# Creating a iterable parse object with ElementTree
context = ET.iterparse(file, events=('end',))

# Go through file, line-by-line
start = time.time()
i = 0
batch = []
# c.execute("PRAGMA synchronous = OFF")
for event, elem in context:

    # Check if a page was found and is an actual page
    if elem.tag == pretext + "page" and elem[1].text=="0" and not elem[-1].find(pretext + 'text').text[0]=="#":
        i += 1

        # Otherwise get data
        try:
            # Get text and process to one-line, lower-case
            text = elem[-1].find(pretext + 'text').text.replace('\n', ' ').lower()

            # Check for Cat Article
            if elem[0].text == "Cat":
                cat_article_line.append(i)

            # Check for Articles beginning with A
            elif elem[0].text[0] =="A":
                a_article_line.append(i)

            #Adding articles up in batches to reduce write read operations
            batch.append((i, text))

            # update vocabulary
            c_words = set(re.split('[\W]+', text))
            vocabulary.update(c_words)

            # Clear stuff
            elem.clear()

            # Also eliminate now-empty references from the root node to <Title>
            if hasattr(elem, "getprevious"):
                while elem.getprevious() is not None:
                    del elem.getparent()[0]

            # Check for batch-insertion
            if len(batch) >= batch_size:
                # Batch insertion
                insert_command = "INSERT INTO Articles (Ident, Article) VALUES (?, ?)"
                c.executemany(insert_command, batch)
                conn.commit()

                # Reset batch
                batch = []

        except AttributeError:
            pass

        if i % 1000 == 0:
            print("{}: {} / {}".format(datetime.now(),
                                       i,
                                       4576000))
        if i % 10000 == 0:
            #print("Vocabulary size: {}".format(len(dict)))
            time_now = time.time()
            # Simple linear time estimation
            delta = ((time_now - start) / (i / 4576000)) * (1 - (i / 4576000))
            print("Until now there were {:d} articles processed".format(i))
            print("Estimated time left: {:d} hours {:d} minutes {:.0f} seconds\n". \
                  format(int(delta / (60 * 60)), int((delta % (60 * 60))/60), delta % 60))

            print("\tCommitting. ")
            #conn.commit()

# c.execute("PRAGMA synchronous = FULL")
end = time.time()
print("Finished in time: {:.2f}s".format(end - start))

conn.commit()
c.close()

print("Storing vocabulary.")
pickle.dump(vocabulary, Path(output_dir, "vocabulary.p").open("wb"))

print("Storing cat list.")
pickle.dump(cat_article_line, Path(output_dir, "cat_list.p").open("wb"))

print("Storing A articles.")
pickle.dump(a_article_line, Path(output_dir, "a_articles.p").open("wb"))

print("Done.")
