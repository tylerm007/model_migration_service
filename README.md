# Archimedes

This project reads the CALiveAPICreator repos to parse rules into objects. This can help understand how to migrate to [Api Logic Server Docs](https://apilogicserver.github.io/Docs/) (ALS)

## Install
```
git clone https://github.com/tylerm007/fileReader.git
cd fileReader
python3 install venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Run
point to you LAC repository home and  and select the project name from the list of 'apis'. The optional sections will only print the directory named.
```
$python3 reposreader.py --help
Generate a report of an existing CA Live API Creator Repository

options:
  -h, --help         show this help message and exit
  --repos REPOS      Full path to /User/guest/caliveapicreator.repository
  --project PROJECT  The name of the LAC project (teamspaces/api) default: demo
  --section SECTION  The api directory name to process [rules, resources, functions, etc.] default: all
  --version          print the version number and exit


python3 reposreader.py  --project demo --repos caliveapicreator.repository --section all

MAC EXAMPLE:
python3 reposreader.py demo /Users/user1/CALiveAPICreator.repository rules
```

## Skip Sections and Files
This version skips the following files
```
"api.json","issues.json", "apioptions.json", "exportoptions.json", ".DS_Store"
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
Database: Derby 
  URL:jdbc:derby:directory:/Users/user1/derby/Demo 
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
User: user1 Roles: ['API Owner']
User: admin Roles: ['API Owner']
```

## Resources
The resource list is user defined endpoints.  Some are nested documents shown as D - directory and F - File. 
```
=========================
       RESOURCES 
=========================
| --- D Customers
| --- F Customers.json Entity: customer  Attrs: (name,balance,credit_limit) 
| ------ D Orders
| ------ F Orders.json Entity: PurchaseOrder Join: ("customer_name" = [name]) Attrs: (order_number,amount_total,paid,notes)
| --------- D LineItems
| --------- F LineItems.json Entity: LineItem Join: ("order_number" = [order_number]) Attrs: (product_number,order_number,qty_ordered ,product_price,amount)
| ------------ D Product
| ------------ F Product.json Entity: product Join: ("product_number" = [product_number]) Attrs: (name,price,product_number)
```
### safrs.JSON API example:
```
curl -X 'GET' \
  'http://localhost:5656/api/Customer/ALFKI/?include=OrderList%2COrderList.OrderDetailList%2COrderList.OrderDetailList.Product&fields%5BCustomer%5D=Id%2CCompanyName%2CContactName%2CContactTitle%2CAddress%2CCity%2CRegion%2CPostalCode%2CCountry%2CPhone%2CFax%2CBalance%2CCreditLimit%2COrderCount%2CUnpaidOrderCount%2CClient_id' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/vnd.api+json'

Note: entities following relationships
include=OrderList,OrderList.OrderDetailList,OrderList.OrderDetailList.Product
```

### Resources are linked and nested - this becomes the basis for new endpoints (root)
```
    @app.route('/customers')
    def customers():
        root = Resource(models.Customer,"Customers")
        Resource.alias(root,models.Customer.Name, "Name")
        Resource.alias(root,models.Customer.Balance, "Balance")
        Resource.alias(root,models.Customer.CreditLimit, "CreditLimit")
        Resource.calling(root, myGetFunction)

        Orders_1 = Resource(models.PurchaseOrder,"Orders")
        Resource.alias(Orders_1,models.PurchaseOrder.OrderNumber, "OrderNumber")
        Resource.alias(Orders_1,models.PurchaseOrder.TotalAmount, "TotalAmount")
        Resource.alias(Orders_1,models.PurchaseOrder.Paid, "Paid")
        Resource.alias(Orders_1,models.PurchaseOrder.Notes, "Notes")
        Resource.join(root, Orders_1, models.PurchaseOrder.customer_name)

        LineItems_2 = Resource(models.LineItem,"LineItems")
        Resource.alias(LineItems_2,models.LineItem.ProductNumber, "ProductNumber")
        Resource.alias(LineItems_2,models.LineItem.OrderNumber, "OrderNumber")
        Resource.alias(LineItems_2,models.LineItem.Quantity, "Quantity")
        Resource.alias(LineItems_2,models.LineItem.Price, "Price")
        Resource.alias(LineItems_2,models.LineItem.Amount, "Amount")
        Resource.join(Orders_1, LineItems_2, models.LineItem.order_number)

        Product_3 = Resource(models.Product,"Product")
        Resource.alias(Product_3,models.Product.Name, "Name")
        Resource.alias(Product_3,models.Product.Price, "Price")
        Resource.alias(Product_3,models.Product.ProductId, "ProductId")
        Resource.joinParent(LineItems_2, Product_3, models.LineItem.product_number)

        key = request.args.get(root.parentKey)
        limit = request.args.get("page_limit")
        offset = request.args.get("page_offset")
        result = Resource.execute(root, key, limit, offset)
        return jsonify({"success": True, f"{root.name}": result})

    def myGetFunction(row: any):
       row["myVirtualAttribute"] = "foo"

curl -X 'GET' \
  'http://localhost:5656/api/Customers?Name=ALFKI/
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/vnd.api+json'

```