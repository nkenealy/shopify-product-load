from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Post, Permission, Product, Variant
from . import api
from .decorators import permission_required


@api.route('/variants/')
def get_variants():
    page = request.args.get('page', 1, type=int)
    pagination = Vriant.query.order_by(Variant.timestamp.desc()).paginate(
    # TODO: need to get new static variables for FLASKY_VARIANTS_PER_PAGE and FLASKY_PRODUCTS_PER_PAGE
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    variants = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_variants', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_variants', page=page+1, _external=True)
    return jsonify({
        'products': [variant.to_json() for variant in variants],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api.route('/variants/', methods=['POST'])
#permission_required(Permission.WRITE_ARTICLES)
def new_variant():
    variant = Variant.from_json(request.json)
    print variant
    db.session.add(variant)
    db.session.commit()
    return jsonify(variant.to_json()), 201, \
        {'Location': url_for('api.get_variant', id=variant.id, _external=True)}


@api.route('/variants/<int:id>')
def get_variant(id):
    variant = Variant.query.get_or_404(id)
    return jsonify(variant.to_json())


@api.route('/products/<int:id>/variants/')
def get_product_variants(id):
    product = Product.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = product.variants.order_by(Variant.timestamp.asc()).paginate(
    #TODO: replace static
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    variants = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_variants', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_variants', page=page+1, _external=True)
    return jsonify({
        'products': [variant.to_json() for variant in variants],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/products/variants/', methods=['POST'])
#TODO: put permission back on and make it product or variant specific
#@permission_required(Permission.COMMENT)
def new_product_variant():
    product = Product.query.filter_by(pos_product_id=4104).first()
    variant = Variant.from_json(request.json)
    #product = Product.query.get_or_404(id)
    #product = Product.query('select * from products where pos_product_id = variant.pos_product_id')
    #variant.product = product
    variant.barcode = product.pos_product_id
    db.session.add(variant)
    db.session.commit()
    return jsonify(variant.to_json()), 201, \
        {'Location': url_for('api.get_variant', id=variant.id,
                             _external=True)}
