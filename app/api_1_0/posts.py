from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Post, Permission,Product,Custom_collection
from . import api
from .decorators import permission_required
from .errors import forbidden
import shopify
import requests
import json
import os


@api.route('/products/')
def get_products():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    products = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_products', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_products', page=page+1, _external=True)
    return jsonify({
        'page': 1,
        'total': 1,
        'records': 2,
        'rows':  [product.to_json() for product in products],
    })


@api.route('/productsnotrows/')
def get_products_not_rows():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    products = pagination.items
    return jsonify({
        'product':  [product.to_json() for product in products],
    })


@api.route('/products/<int:id>')
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_json())


@api.route('/products/', methods=['POST'])
#permission_required(Permission.WRITE_ARTICLES)
def new_product():
    product = Product.from_json(request.json)
    db.session.add(product)
    print product.id
    db.session.commit()
    return jsonify(product.to_json()), 201, \
        {'Location': url_for('api.get_product', id=product.id, _external=True)}

@api.route('/products/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_product(id):
    product = Product.query.get_or_404(id)
    db.session.add(product)
    return jsonify(product.to_json())



@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'page': 1,
        'total': 1,
        'records': 2,
        'rows':  [post.to_json() for post in posts],
    })
    #return jsonify({
    #    'posts': [post.to_json() for post in posts],
    #    'prev': prev,
    #    'next': next,
    #    'count': pagination.total
    #})


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

def load_fixture(name, format='json'):
        with open(os.path.dirname(__file__)+'/fixtures/%s.%s' % (name, format), 'rb') as f:
            return f.read()

@api.route('/postShopifyProduct/')
def postShopifyProduct():
    shop_url = "https://3cf6a1e0b9b04c04092cb8ace60937f6:8224d17b2bce753a61537a0d2f44ec29@neil-test-shop.myshopify.com/admin"
    shopify.ShopifyResource.set_site(shop_url)
    shop = shopify.Shop.current
    new_product = shopify.Product()
    new_product.title = "neilprod"
    new_product.product_type = "carfromellis"
    new_product.vendor = "cadillac"
    success = new_product.save()

    pid = new_product.id
    headers = {'content-type': 'application/json'}
    url = shop_url+ '/products.json'

    #TODO: this load fixture is for pulling in a sample json file - need to emulate this
    #data=load_fixture('product')
    products = Product.query.all()

    for product in products:
        data = json.dumps ({'product':  product.to_json()})
        whatcomeback = requests.post(url,data, headers=headers)
        print whatcomeback
    return data



@api.route('/custom_collections/', methods=['POST'])
#permission_required(Permission.WRITE_ARTICLES)
def new_custom_collection():
    custom_collection = Custom_collection.from_json(request.json)
    db.session.add(custom_collection)
    db.session.commit()
    return jsonify(custom_collection.to_json())


@api.route('/posts/', methods=['POST'])
#permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id, _external=True)}

# TODO: Add a timestamp for today when adding
# TODO: check if pagination is needed for shopify or if I can remove pagination from here
# TODO: ValueError: View function did not return a response - Added a return which is not being used
@api.route('/poststoshopify/')
def poststoshopify():
    data = json.dumps({\
      "price": "199.00",\
      "position": 2,\
      "created_at": "2011-10-20T14:05:13-04:00",\
      "title": "Red",\
      "requires_shipping": True,\
      "updated_at": "2011-10-20T14:05:13-04:00",\
      "inventory_policy": "continue",\
      "compare_at_price": 1,\
      "inventory_quantity": 20,\
      "inventory_management": "shopify",\
      "taxable": True,\
      "id": 49148385,\
      "grams": 200,\
      "sku": "IPOD2008RED",\
      "option1": "Red",\
      "option2": "Green",\
      "fulfillment_service": "manual",\
      "option3": "Blue"\
    })
    headers = {'content-type': 'application/json'}
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    products = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_products', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_products', page=page+1, _external=True)
    shop_url = "https://3cf6a1e0b9b04c04092cb8ace60937f6:8224d17b2bce753a61537a0d2f44ec29@neil-test-shop.myshopify.com/admin"
    shopify.ShopifyResource.set_site(shop_url)
    shop = shopify.Shop.current
    for product in products:
        new_product = shopify.Product()
        #new_product.product_type = "carfromellis"
        new_product.vendor = "cadillac"
        success = new_product.save()

        #TODO: PUT variants = product.variants into for statement
        variants = product.variants
        count = 0
        for variant in variants:
            url = "https://3cf6a1e0b9b04c04092cb8ace60937f6:8224d17b2bce753a61537a0d2f44ec29@neil-test-shop.myshopify.com/admin/products/"+str(new_product.id) +"/variants"
            r = requests.post(url,data, headers=headers)
            v = shopify.Variant()
            v.product_id = new_product.id
            new_product.add_variant(v)
            v.save()
            success = new_product.save()
            new_product.variants[count].price = 8 + count
            new_product.variants[count].sku = variant.sku
            new_product.variants[count].barcode = variant.barcode
            #TODO: find out why title is not getting copied over - do more fields and see if it's only title
            new_product.variants[count].title = variant.title
            #count+=1

        success = new_product.save()
        print success
    return jsonify(product.to_json()), 201, \
        {'Location': url_for('api.get_product', id=product.id, _external=True)}

@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())
