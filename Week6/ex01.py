import sqlite3

# Establish connection
conn = sqlite3.connect('../../data/northwind.db')

# avoid issues with special characters
conn.text_factory = bytes

# create cursor object
c = conn.cursor()

customer = 'ALFKI'
print("Orders by {}".format(customer))

# Get all orders by the customer
c.execute('''CREATE TABLE IF NOT EXISTS new_table as
             SELECT a.OrderID, a.CustomerID, b.ProductID, c.ProductName, c.CategoryID 
             FROM Orders as a 
             LEFT JOIN 'Order Details' as b 
             ON a.OrderID = b.OrderId 
             LEFT JOIN Products as c 
             ON b.ProductId = c.ProductID 
             WHERE a.CustomerID = "{0}"'''.format(customer))

c.execute('''SELECT * FROM new_table''')
orders = c.fetchall()

# Printing
column_names = c.description
for name in column_names:
    print("{0:30}".format(name[0]), end="")

print()
for row in orders:
    for elem in row:
        print("{0:30.30}".format(str(elem)), end="")
    print()

# Orders by customer containing at least two differecnt product types
print("Orders by {} containing at least 2 different product types".format(customer))
print("We assume that product type is indicated by CategoryID")

c.execute('''SELECT OrderID, count(OrderID) as n_distinct_categories 
             FROM (SELECT distinct OrderID, CategoryID FROM new_table)
             GROUP BY OrderID
             HAVING n_distinct_categories > 1''')

# Printing
column_names = c.description
for name in column_names:
    print("{0:10}".format(name[0]), end="")
print()

orders = c.fetchall()
for row in orders:
    print(row)
