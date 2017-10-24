#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 14:25:47 2017

@author: Cool Kid
"""

import pymongo
import pprint
from pymongo import MongoClient
client=MongoClient()
db=client.Northwind

##Query for Exercise 5.1
query=db.orders.aggregate([
    {"$match":{"CustomerID":"ALFKI"}},
    {"$lookup":{"from": "order-details",
                "localField": "OrderID",
                "foreignField": "OrderID",
                "as": "Order-details"}},
    {"$unwind": {
                "path": "$Order-details",
                "preserveNullAndEmptyArrays":True}},
    {"$lookup":{"from": "products",
                "localField": "Order-details.ProductID",
                "foreignField": "ProductID",
                "as": "Order-details.Product-details"}},
    {"$group":{
                "_id":"$OrderID",
                "OrderID":{"$first":"$OrderID"},
                "CustomerID":{"$first":"$CustomerID"},
                "Products":{"$push":"$Order-details"}}},
    {"$project":{
                "_id":0,
                "CustomerID": 1,
                "OrderID": 1,
                "Products.Product-details.ProductID": 1,
                "Products.Product-details.ProductName": 1}}
    ])

for item in query:
    pprint.pprint(item)


#Query for Exercise 5.2

a=[i['OrderID'] for i in db["orders"].find({"CustomerID": "ALFKI"})]
b=[i["_id"] for i in db["order-details"].aggregate([
    {"$match":{"OrderID":{"$in":a}}},
    {"$group":{"_id":"$OrderID", "amount_of_diff_products":{"$sum":1}}},
    {"$match":{"amount_of_diff_products":{"$gte":2}}}])]


query=db.orders.aggregate([
    {"$match":{"OrderID":{"$in":b}}},
    {"$lookup":{"from": "order-details",
                "localField": "OrderID",
                "foreignField": "OrderID",
                "as": "Order-details"}},
    {"$unwind": {
                "path": "$Order-details",
                "preserveNullAndEmptyArrays":True}},
    {"$lookup":{"from": "products",
                "localField": "Order-details.ProductID",
                "foreignField": "ProductID",
                "as": "Order-details.Product-details"}},
    {"$group":{
                "_id":"$OrderID",
                "OrderID":{"$first":"$OrderID"},
                "CustomerID":{"$first":"$CustomerID"},
                "Products":{"$push":"$Order-details"}}},
    {"$project": {
                "_id": 0,
                "CustomerID": 1,
                "OrderID": 1,
                "Products.Product-details.ProductID": 1,
                "Products.Product-details.ProductName": 1}}
    ])

for item in query:
    pprint.pprint(item)

##Query for Exercise 5.3

query=db.orders.aggregate([
    {"$match":{"CustomerID":"ALFKI"}},
    {"$lookup":{"from": "order-details",
                "localField": "OrderID",
                "foreignField": "OrderID",
                "as": "Order-details"}},
    {"$unwind": {
                "path": "$Order-details",
                "preserveNullAndEmptyArrays":True}},
    {"$lookup":{"from": "products",
                "localField": "Order-details.ProductID",
                "foreignField": "ProductID",
                "as": "Order-details.Product-details"}},
    {"$group":{
                "_id":{"CustomerID":"$CustomerID", "EmployeeID":"$EmployeeID"},
                "total_Amount":{"$sum":\
                {"$multiply":["$Order-details.Quantity","$Order-details.UnitPrice",
                              {"$subtract":[1,"$Order-details.Discount"]}]}},
                "CustomerID":{"$first":"$CustomerID"},
                'EmployeeID':{"$first":'$EmployeeID'},
                "Products":{"$push":"$Order-details.Product-details.ProductName"}}},
    {"$project":{
                "_id":0}}
    ])

for item in query:
    pprint.pprint(item)