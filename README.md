
======
The Microsoft Dynamics Retail Management System (RMS) is used by  small and midsize retailers to automates POS processes and store operations and, provide centralized control
for multi-store retailers. The product data for RMS is stored on MS SQL Server. The Ellis project reads the product data from the local database at the retail outlet and uploads
it to a PostgreSQL database residing on Heroku. This provides a web based Product Management System for the retailer to mark which products are to be sent to the Shopify shopping cart.
The Ellis Product Management system is written in python and uses the Flask framework to manage the products and send a message to Shopify REST API in json.

PostgreSQL database on Heroku
https://postgres.heroku.com/databases/nkellis-heroku-postgresql-violet

Example of json POST
https://nkellis.herokuapp.com/api/v1.0/postShopifyProduct/
https://nkellis.herokuapp.com/api/v1.0/productsnotrows/

Shopify Front end
http://neil-test-shop.myshopify.com/collections/all

Shopify Admin Python Packages used
https://neil-test-shop.myshopify.com/admin/products

This is the project on github
https://github.com/nkenealy/shopify-product-load

<h1>Python Packages used</h1>
* Flask-Bootstrap==3.0.3.1
* Flask-HTTPAuth==2.2.0
* Flask-Migrate==1.1.0 
* Flask-PageDown==0.1.4
* Flask-SQLAlchemy==1.0
* Flask-Script==0.6.6
* Jinja2==2.7.1
* Mako==0.9.1
* Markdown==2.3.1
* MarkupSafe==0.18
* SQLAlchemy==0.8.4
* WTForms==1.0.5
* alembic==0.6.2
* bleach==1.4.0
* blinker==1.3
* html5lib==1.0b3
* six==1.4.1
* ShopifyAPI==1.0.1
* requests==2.1.0



