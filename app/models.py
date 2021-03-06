from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    productName = db.Column(db.Text)
    SKU = db.Column(db.Text)
    price = db.Column(db.Integer)
    sales = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    # TODO: add more fields in here as needed in shopify and add same in to_json and from_json
    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'productName': self.productName,
            'SKU': self.SKU,
            'price': self.price,
            'sales': self.sales,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count(),
            'variants': [comment.to_json() for comment in self.comments]
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        post_id = json_post.get('post_id')
        body = json_post.get('body')
        productName = json_post.get('productName')
        SKU = json_post.get('SKU')
        price = json_post.get('price')
        sales = json_post.get('sales')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body,productName=productName,SKU=SKU,price=price,sales=sales)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer,primary_key=True)
    pos_product_id = db.Column(db.Integer)
    title = db.Column(db.Text)
    product_type= db.Column(db.Text)
    handle= db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body_html= db.Column(db.Text)
    template_suffix = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tags = db.Column(db.Text)
    vendor = db.Column(db.Text)
    published_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    variants = db.relationship('Variant', backref='product', lazy='dynamic')
    images = db.relationship('Image', backref='product', lazy='dynamic')

    def to_json(self):
        json_product = {
            'id': self.id,
            'pos_product_id' : self.pos_product_id,
            'title' : self.title,
            'product_type' : self.product_type,
            'handle' : self.handle,
            'created_at' : str(self.created_at),
            'body_html' : self.body_html,
            'template_suffix' : self.template_suffix,
            'updated_at' : str(self.updated_at),
            'tags' : self.tags,
            'vendor' : self.vendor,
            'published_at' : str(self.published_at),
            'author_id' : self.author_id,
            'variants': [variant.to_json() for variant in self.variants],
            'images': [image.to_json() for image in self.images]
        }
        return json_product

    @staticmethod
    def from_json(json_product):
        title = json_product.get('title')
        pos_product_id = json_product.get('pos_product_id')
        product_type = json_product.get('product_type')
        handle = json_product.get('handle')
        created_at = json_product.get('created_at')
        body_html = json_product.get('body_html')
        template_suffix = json_product.get('template_suffix')
        updated_at = json_product.get('updated_at')
        tags = json_product.get('tags')
        vendor = json_product.get('vendor')
        published_at = json_product.get('published_at')
        author_id = json_product.get('author_id')
        return Product(title=title,pos_product_id=pos_product_id,product_type=product_type,handle=handle,created_at=created_at,body_html=body_html,template_suffix=template_suffix,\
                       updated_at=updated_at,tags=tags,vendor=vendor,published_at=published_at,author_id=author_id)


class Variant(db.Model):
    __tablename__ = 'variants'
    id = db.Column(db.Integer, primary_key=True)
    pos_product_id = db.Column(db.Integer)
    position = db.Column(db.Integer)
    price = db.Column(db.Text)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    created_at = db.Column(db.DateTime)
    requires_shipping = db.Column(db.Boolean)
    title = db.Column(db.Text)
    inventory_quantity = db.Column(db.Integer)
    compare_at_price = db.Column(db.Text)
    inventory_policy = db.Column(db.Text)
    updated_at = db.Column(db.DateTime)
    inventory_management = db.Column(db.Text)
    taxable = db.Column(db.Boolean)
    grams = db.Column(db.Integer)
    sku = db.Column(db.Text)
    option1 = db.Column(db.Text)
    fulfillment_service = db.Column(db.Text)
    option2 = db.Column(db.Text)
    option3 = db.Column(db.Text)


    def to_json(self):
        json_variant = {
            'id': self.id,
            'pos_product_id': self.pos_product_id,
            'position': self.position,
            'price': str(self.price),
            'product_id': self.product_id,
            'created_at': str(self.created_at),
            'requires_shipping': self.requires_shipping,
            'title': self.title,
            'inventory_quantity': self.inventory_quantity,
            'compare_at_price': self.compare_at_price,
            'inventory_policy': self.inventory_policy,
            'updated_at': str(self.updated_at),
            'inventory_management': self.inventory_management,
            'taxable': self.taxable,
            'grams': self.grams,
            'sku': self.sku,
            'option1': self.option1,
            'fulfillment_service': self.fulfillment_service,
            'option2': self.option2,
            'option3': self.option3,
        }
        return json_variant

    @staticmethod
    def from_json(json_variant):
        id= json_variant.get('id')
        pos_product_id= json_variant.get('pos_product_id')
        position = json_variant.get('position')
        price = str(json_variant.get('price'))
        product_id = json_variant.get('product_id')

        created_at= json_variant.get('created_at')
        requires_shipping = json_variant.get('requires_shipping')
        title = json_variant.get('title')
        inventory_quantity = json_variant.get('inventory_quantity')

        compare_at_price= json_variant.get('compare_at_price')
        inventory_policy = json_variant.get('inventory_policy')
        updated_at = json_variant.get('updated_at')
        inventory_management = json_variant.get('inventory_management')

        taxable= json_variant.get('taxable')
        grams = json_variant.get('grams')
        sku = json_variant.get('sku')
        option1 = json_variant.get('option1')

        fulfillment_service= json_variant.get('fulfillment_service')
        option2 = json_variant.get('option2')
        option3 = json_variant.get('option3')

        return Variant(id=id,pos_product_id=pos_product_id,position=position,price=price,product_id=product_id,created_at=created_at,requires_shipping=requires_shipping,title=title,\
               inventory_quantity=inventory_quantity,compare_at_price=compare_at_price,inventory_policy=inventory_policy,updated_at=updated_at,inventory_management=inventory_management,\
               taxable=taxable,grams=grams,sku=sku,option1=option1,fulfillment_service=fulfillment_service,option2=option2,option3=option3)


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    pos_product_id = db.Column(db.Integer)
    position = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    src = db.Column(db.Text)

    def to_json(self):
        json_image = {
            'id': self.id,
            'position': self.position,
            'pos_product_id': self.pos_product_id,
            'product_id': self.product_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'src': str(self.src),
        }
        return json_image

    @staticmethod
    def from_json(json_image):
        id = json_image.get('id')
        pos_product_id= json_image.get('pos_product_id')
        position = json_image.get('position')
        product_id = json_image.get('product_id')
        created_at= json_image.get('created_at')
        updated_at = json_image.get('updated_at')
        src = json_image.get('src')
        return Image(id=id,pos_product_id=pos_product_id,position=position,product_id=product_id,created_at=created_at,updated_at=updated_at,src=src)

class Custom_collection(db.Model):
    __tablename__ = 'custom_collections'
    id = db.Column(db.Integer, primary_key=True)
    pos_dept_id = db.Column(db.Integer)
    title = db.Column(db.Text)

    def to_json(self):
        json_custom_collection = {
            #'id': self.id,
            'title': self.title,
            #'pos_dept_id': self.pos_dept_id,
        }
        return json_custom_collection

    @staticmethod
    def from_json(json_custom_collection):
        id = json_custom_collection.get('id')
        pos_dept_id = json_custom_collection.get('pos_dept_id')
        title = json_custom_collection.get('title')
        return Custom_collection(id=id,pos_dept_id=pos_dept_id,title=title)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    barcode = db.Column(db.Text)
    sku = db.Column(db.Text)
    title = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
         # TODO: check if this is needed anywhere and refactor without it here and elsewhere
           # 'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'barcode': self.barcode,
            'sku': self.sku,
            'title': self.title,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
          # TODO: check if this is needed anywhere and refactor without it here and elsewhere
          #  'author': url_for('api.get_user', id=self.author_id,
          #                    _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        barcode = json_comment.get('barcode')
        sku = json_comment.get('sku')
        title = json_comment.get('title')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body,barcode=barcode,sku=sku,title=title)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)
