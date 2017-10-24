#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 14:25:47 2017

@author: Cool Kid
"""
import sqlite3
from pathlib import Path
import pprint
##Query for Exercise 5.1


filepath=Path("/Files")
filename="northwind.db"

def decode(text: bytes):
    encodings = ["utf-8", "latin1", "utf-16", "utf-32", "unicode"]
    for encoding in encodings:
        try:
            return text.decode(encoding)
        except (AttributeError, UnicodeDecodeError) as e:
            pass
    try:
        return str(text)
    except (AttributeError, UnicodeDecodeError) as e:
        raise ValueError("This is the end of the world")

# (AttributeError, UnicodeDecodeError) as e

datapath=Path(filepath,filename)
conn=sqlite3.connect(str(datapath))
conn.text_factory = bytes
c=conn.cursor()

c.execute('''SELECT Orders.CustomerID, Orders.OrderID, "Order Details".ProductID, Products.ProductName From Orders
        INNER JOIN "Order Details"
        ON "Order Details".OrderID=Orders.OrderID
        INNER JOIN Products
        ON "Order Details".ProductID = Products.ProductID
        Where Orders.CustomerID=="ALFKI"''')


#Print formatted column titles
columns=[print("{0:20}".format(i[0]),end="") for i in c.description]
print()
#Print formatted results
for item in c.fetchall():
    [print("{0:20}".format(decode(i)),end="") for i in item]
    print()

c.close()


##Query for Exercise 5.2

filepath=Path("/Files")
filename="northwind.db"

datapath=Path(filepath,filename)
conn=sqlite3.connect(str(datapath))
conn.text_factory = bytes
c=conn.cursor()

c.execute('''SELECT Orders.CustomerID, Orders.OrderID, "Order Details".ProductID, Products.CategoryID, Products.ProductName From Orders
            INNER JOIN
              (SELECT OrderID, Count(CategoryID) as article_count FROM "Order Details"
                INNER JOIN Products ON "Order Details".ProductID = Products.ProductID
            GROUP BY OrderID HAVING Count(CategoryID)>1) as temp1
              ON temp1.OrderID=Orders.OrderID
            INNER JOIN "Order Details"
              ON "Order Details".OrderID=Orders.OrderID
            INNER JOIN Products
              ON "Order Details".ProductID = Products.ProductID
            Where Orders.CustomerID=="ALFKI"''')

#Print formatted column titles
[print("{0:20}".format(i[0]),end="") for i in c.description]
print()
#Print formatted results
for item in c.fetchall():
    [print("{0:20}".format(decode(i)), end="") for i in item]
    print()

c.close()

##Query for Exercise 5.3

filepath=Path("/Files")
filename="northwind.db"

datapath=Path(filepath,filename)
conn=sqlite3.connect(str(datapath))
conn.text_factory = bytes
c=conn.cursor()

# Begin the query with the standard fields we want to keep
# Create a field called sum that calculates the total of each group
# Create a field that concatenates all products into one field
# Inner join the table Orders with "Order-details" matching on OrderID
# Inner join these results on the table products matching on ProductID
# Limit the results to those having "ALFKI" as CustomerID
# Group all results by EmployeeID
c.execute('''SELECT Orders.CustomerID, EmployeeID,
              Sum((Quantity*"Order Details".UnitPrice*(1-Discount))) as Total_Amount,
               group_concat(Products.ProductName,", ") as Products FROM Orders
            INNER JOIN "Order Details"
              ON Orders.OrderID = "Order Details".OrderID
            INNER JOIN Products
              ON "Order Details".ProductID = Products.ProductID
            WHERE CustomerID=="ALFKI"
            GROUP BY EmployeeID''')

#Print formatted column titles
[print("{0:20}".format(i[0]),end="") for i in c.description]
print()
#Print formatted results
for item in c.fetchall():
    [print("{0:20}".format(decode(i)), end="") for i in item]
    print()

c.close()
