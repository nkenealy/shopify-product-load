from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import requests, json

Base = automap_base()

# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine('mssql+pyodbc://devel:n3wmediam3d@NEIL-DESKTOP/FRESH?driver=SQL Server; Trusted_Connection=Yes', echo=True)

# reflect the tables
Base.prepare(engine, reflect=True)

# mapped classes are now created with names by default
# matching that of the table name.

session = Session(engine)
headers = {'content-type': 'application/json'}

Category = Base.classes.Category
Item = Base.classes.Item
for instance in session.query(Item).order_by(Item.ID): 
    for category in session.query(Category).filter(Category.ID==instance.CategoryID):
        print category.Name
    data = json.dumps({'title': instance.Description,\
                       'product_type': "Cult Products",\
                       'tags': category.Name,\
                       'pos_product_id': instance.ID })
    github_url = "https://nkellis.herokuapp.com/api/v1.0/products/"
    print data
    r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
    print r.json
    github_url = "https://nkellis.herokuapp.com/api/v1.0/products/variants/"
    data = json.dumps({'pos_product_id':instance.ID,\
                       'sku':instance.ItemLookupCode,\
                       'price':str(instance.Price),\
                       'inventory_quantity':instance.Quantity,\
                       'inventory_policy':"continue",\
                       'inventory_management':"shopify",\
                       'fulfillment_service':"manual",\
                       'grams':instance.Weight,\
                       'title':instance.Description})
    print data
    r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
    print r.json
    github_url = "https://nkellis.herokuapp.com/api/v1.0/products/images/"
    data = json.dumps({'pos_product_id':instance.ID,\
                       'src':"https://cdn.shopify.com/s/files/1/0557/9717/files/%s?67" % (instance.PictureName)})
    print data
    r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
    print r.json
    #Select SupplierName from supplier where Supplier.ID=instance.ID    
