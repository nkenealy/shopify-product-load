#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import psycopg2
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import shopify

app = Flask(__name__, static_url_path = "")
auth = HTTPBasicAuth()

Base = declarative_base()

class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Use default=func.now() to set the default hiring time
    # of an Employee to be the current time when an
    # Employee record was created
    date_created_on = Column(DateTime, default=func.now())
    department_id = Column(Integer, ForeignKey('department.id'))
    # Use cascade='delete,all' to propagate the deletion of a Department onto its Employees
    department = relationship(
        Department,
        backref=backref('items',
                         uselist=True,
                         cascade='delete,all'))


engine = create_engine("postgres://nyolwgiojmkzgp:fS8xP6Hu578fci_Jv_CbvCJTFA@ec2-54-204-47-70.compute-1.amazonaws.com:5432/dddrjtr01quafc")

from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
s = session()

shop_url = "https://3cf6a1e0b9b04c04092cb8ace60937f6:8224d17b2bce753a61537a0d2f44ec29@neil-test-shop.myshopify.com/admin"
shopify.ShopifyResource.set_site(shop_url)
shop = shopify.Shop.current
for instance in s.query(Item):
    new_product = shopify.Product()
    new_product.title = instance.name
    new_product.product_type = "fakecar"
    new_product.vendor = "Bssdarton"
    success = new_product.save()




