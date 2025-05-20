from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Category, CategoryAttribute
from app import db

categories_ns = Namespace('categories', description='categories related operations')

user_model = categories_ns.model('User_dashboard', {
    'id': fields.Integer,
    'email': fields.String,
})

# Category output model
category_model = categories_ns.model('Category', {
    'id': fields.Integer,
    'name': fields.String,
})

attribute_input = categories_ns.model('AttributeInput', {
    'name': fields.String(required=True, description='Attribute name'),
    'data_type': fields.String(required=True, description='Data type (e.g., string, integer, date)')
})

category_with_attributes_input = categories_ns.model('CategoryWithAttributesInput', {
    'name': fields.String(required=True, description='Category name'),
    'attributes': fields.List(fields.Nested(attribute_input), required=True)
})

@categories_ns.route('')
class CategoryListResource(Resource):

    @categories_ns.marshal_list_with(category_model)
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        categories = Category.query.filter_by(owner_id=user_id).all()
        return categories
    
    @categories_ns.expect(category_with_attributes_input)
    @categories_ns.marshal_with(category_model, code=201)
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = categories_ns.payload

        name = data.get('name')
        attributes = data.get('attributes', [])

        # Check for duplicates
        if Category.query.filter_by(name=name, owner_id=user_id).first():
            categories_ns.abort(400, 'Category with this name already exists.')

        # Create category
        new_category = Category(name=name, owner_id=user_id)
        db.session.add(new_category)
        db.session.flush()  # get ID before commit

        # Add attributes
        for attr in attributes:
            attr_name = attr['name']
            data_type = attr['data_type']
            new_attr = CategoryAttribute(name=attr_name, attribute_type=data_type, category=new_category)
            db.session.add(new_attr)

        db.session.commit()
        return new_category, 201