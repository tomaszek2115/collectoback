from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=True)

    categories = db.relationship('Category', backref='owner', lazy=True)
    items = db.relationship('Item', backref='owner', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_category_owner'), nullable=False)

    attributes = db.relationship('CategoryAttribute', backref='category', cascade='all, delete', lazy=True)
    items = db.relationship('Item', backref='category', cascade='all, delete', lazy=True)

class CategoryAttribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', name='fk_categoryattribute_category'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    attribute_type = db.Column(db.String(20), nullable=False)  # 'string', 'number', 'date', etc.

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', name='fk_item_category'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_item_owner'), nullable=False)

    values = db.relationship('ItemAttributeValue', backref='item', cascade='all, delete', lazy=True)

class ItemAttributeValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', name='fk_itemattributevalue_item'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('category_attribute.id', name='fk_itemattributevalue_field'), nullable=False)
    value = db.Column(db.String(255), nullable=False)  # cast in app logic

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')
    followed = db.relationship('User', foreign_keys=[followed_id], backref='followers')