from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden
import shopify



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


@api.route('/posts/', methods=['POST'])
#permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id, _external=True)}

# TODO: check if pagination is needed for shopify or if I can remove pagination from here
# TODO: ValueError: View function did not return a response - Added a return which is not being used
@api.route('/poststoshopify/')
def poststoshopify():
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
    shop_url = "https://3cf6a1e0b9b04c04092cb8ace60937f6:8224d17b2bce753a61537a0d2f44ec29@neil-test-shop.myshopify.com/admin"
    shopify.ShopifyResource.set_site(shop_url)
    shop = shopify.Shop.current
    for post in posts:
        new_product = shopify.Product()
        new_product.title = post.productName
        new_product.product_type = "carfromellis"
        new_product.vendor = "cadillac"
        success = new_product.save()
    return success

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
