# Archimedes

This project reads the CALiveAPICreator repos to parse rules into objects. This can help understand how to migrate to [Api Logic Server Docs](https://apilogicserver.github.io/Docs/) (ALS)

## Install
```
python3 install venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Run
Modify the basepath to point to the LAC source repository and project
```
python3 filereader.py
```

## Skip Sections and Files
This version skips the following files
```
"api.json", "topics", "sorts","issues.json", "apioptions.json","filters", "timers", "exportoptions.json", ".DS_Store"
```

## Rules
The code will attempt to define a function and rule in Api Logic Server format. It will also try to convert JavaScript to Python - formatting will need to be done manually
```
=========================
       rules 
=========================
def fn_formula_amount(row: models.LineItem, old_row: models.LineItem, logic_row: LogicRow):
     if row.qty_ordered <= 6
        return row.product_price * row.qty_ordered
    else:
        return row.product_price * row.qty_ordered * 0.8


'''
     Title: Discounted price*qty
     Name: formula_amount
     Entity: LineItem
     Comments: Reactive Logic is expressed in JavaScript
     RuleType: formula
'''
     Rule.formula(derive=models.LineItem.amount calling=fn_formula_amount)

```


## Data Sources
The datasource will generate a sample table, columns, keys, and foreign keys. Note: views and procedures not shown in this version.
```
=========================
       data_sources 
=========================
------------------------------------------------------------
Database: MySQL 
  URL:jdbc:derby:directory:/Users/user1/mysql/Demo 
  User: DEMO Schema: DEMO
------------------------------------------------------------

create table product (
   product_number BIGINT not null AUTO_INCREMENT
   ,name VARCHAR(50) not null 
   ,price DECIMAL(19,4) not null 
   ,icon BLOB  
   ,full_image BLOB  
)

# PRIMARY KEY('product_number')

ALTER TABLE ADD CONSTRAINT fk_lineitem_purchaseorder FOREIGN KEY LineItem(order_number) REFERENCES PurchaseOrder(order_number)

```

## Security
List of users and roles (note views and procedures not listed in this version)
```
=========================
       security 
=========================
Role: API User TablePermission: N
Role: API Documentation TablePermission: A
Role: Sales Rep TablePermission: N
Role: API Owner TablePermission: A
User: demo Roles: ['API Owner']
User: TB Roles: ['API Owner']
User: admin Roles: ['API Owner']
```

## Resources
The resource list is user defined endpoints.  Some are nested documents shown as D - directory and F - File. 
```
=========================
       RESOURCES 
=========================
| -- D v1
| ----- D Customers
| ----- F Customers.json Entity: customer  Attrs: (name,balance,credit_limit)) 
| -------- D Orders
| -------- F Orders.json Entity: PurchaseOrder Join: ("customer_name" = [name]) Attrs: (order_number,amount_total,paid,notes)) 
| ----------- D LineItems
| ----------- F LineItems.json Entity: LineItem Join: ("order_number" = [order_number]) Attrs: (product_number,order_number,qty_ordered,product_price,amount)) 
| -------------- D Product
| -------------- F Product.json Entity: product Join: ("product_number" = [product_number]) Attrs: (name,price,product_number)) 
| ----- D Products
| ----- F Products.json Entity: product  Attrs: (name,price)) 
```
### safrs.JSON example:
```
curl -X 'GET' \
  'http://localhost:5656/api/Customer/ALFKI/?include=OrderList%2COrderList.OrderDetailList%2COrderList.OrderDetailList.Product&fields%5BCustomer%5D=Id%2CCompanyName%2CContactName%2CContactTitle%2CAddress%2CCity%2CRegion%2CPostalCode%2CCountry%2CPhone%2CFax%2CBalance%2CCreditLimit%2COrderCount%2CUnpaidOrderCount%2CClient_id' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/vnd.api+json'


include=OrderList,OrderList.OrderDetailList,OrderList.OrderDetailList.Product
```