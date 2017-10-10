#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 14:25:47 2017

@author: Cool Kid
"""
import xml.etree.ElementTree as ET
import time
import re
import math

import pickle
from pathlib import Path

import os
from bz2file import BZ2File
import sqlite3
from psutil import virtual_memory
from datetime import datetime
import json

# Settings
batch_size = 1000

# Possibility to take memory into account (Machine optimization)
mem = virtual_memory()
print("Memory on machine: {:,} B".format(mem.available))

# Defining filepaths
filepath = Path("/")
database_name = "Articles.db"
vocabulary_name = "vocabulary.p"
output_dir = Path("/")

##########
# Database

# Creating or connecting to the database
database_path = Path(output_dir, database_name)  # Path(filepath, database_name)
print("Connecting to {}".format(database_path))

conn = sqlite3.connect(str(database_path))  #
c = conn.cursor()

##########
# Data access
print("Loading vocabulary")
vocabulary = pickle.load(Path(filepath, vocabulary_name).open("rb"))

##########
# Data processing
wordcount = len(vocabulary)
# Split words if there are too many(5Mio. each)
# By this we build the indexing step wise to not crash the memory of the computer
splitnumber = math.ceil(wordcount / 5e6)
start = time.time()

# Create wordnumber for the SQL-Database-Index
wordnumber = 0
print("Starting process")
for i in range(splitnumber):

    batch = []
    # Get next wordbatch from the vocabulary
    wordbatch = list(vocabulary)[int(i * 5e6):int((i + 1) * 5e6)]

    # Create new dict
    wordindex = dict((word, set()) for word in wordbatch)
    #SQL Query to iterate over all articles
    sql_command="SELECT * FROM Articles"
    c.execute(sql_command)

    #Iterating over the entire SQL-Database
    for row in c:
        # Iterating over all words found in one article
        for word in set(re.split('\W+', row[1])):
            # Check if string is empty
            if not not word:
                try:
                    wordindex[word].add(row[0])
                except:
                    pass

    # make a list that can be given to SQL-Database
    for keyword in wordindex.keys():
        # Indexing of words start with 1
        wordnumber += 1
        batch.append([wordnumber, keyword, json.dumps(list(wordindex[keyword]))])

    # Batch insertion of the Word Database
    insert_command = "INSERT INTO Words (Ident, Word, Article_list) VALUES (?, ?, ?)"
    c.executemany(insert_command, batch)
    conn.commit()

    # Reset batch
    batch = []

    # Print progress
    print("Round {} of {}".format((i+1),splitnumber))
    #print("Vocabulary size: {}".format(len(dict)))
    time_now = time.time()
    # Simple linear time estimation
    delta = ((time_now - start) / ((i+1) / splitnumber)) * (1 - ((i+1) / splitnumber))
    print('Estimated time left: {:d} hours {:d} minutes {:.0f} seconds\n'. \
         format(int(delta / (60 * 60)), int((delta % (60 * 60))/60), delta % 60))

end = time.time()
print('Finished in time: {:.2f}s'.format(end - start))

conn.commit()
c.close()

print("Done.")