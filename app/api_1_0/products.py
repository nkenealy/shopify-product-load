from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden
import shopify

@api.route('/products/')
def get_products():
    page = request.args.get('page', 1, type=int)
    pagination = product.query.paginate(
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


@api.route('/products/<int:id>')
def get_product(id):
    product = product.query.get_or_404(id)
    return jsonify(product.to_json())


@api.route('/products/', methods=['POST'])
#permission_required(Permission.WRITE_ARTICLES)
def new_product():
    product = product.from_json(request.json)
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_json()), 201, \
        {'Location': url_for('api.get_product', id=product.id, _external=True)}

@api.route('/products/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_product(id):
    product = product.query.get_or_404(id)
    db.session.add(product)
    return jsonify(product.to_json())
