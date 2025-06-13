from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Item, Category, CategoryAttribute, ItemAttributeValue
from app import db

items_ns = Namespace('items', description='item related operations')

attribute_value_model = items_ns.model('AttributeValue', {
    'attribute_name': fields.String,
    'value': fields.String,
    'field_id': fields.Integer 
})

item_model = items_ns.model('Item', {
    'id': fields.Integer,
    'category_id': fields.Integer,
    'values': fields.List(fields.Nested(attribute_value_model))
})

item_value_input = items_ns.model('ItemValueInput', {
    'field_id': fields.Integer(required=True, description='Attribute ID'),
    'value': fields.String(required=True, description='Value for the attribute')
})

item_create_input = items_ns.model('ItemCreateInput', {
    'category_id': fields.Integer(required=True, description='Category ID for the item'),
    'values': fields.List(fields.Nested(item_value_input), required=True)
})

@items_ns.route('/details/<int:item_id>')
class ItemDetailResource(Resource):
    @items_ns.marshal_with(item_model)
    @jwt_required()
    def get(self, item_id):
        user_id = int(get_jwt_identity())

        item = Item.query.filter_by(id=item_id, owner_id=user_id).first()

        if not item:
            return {'error': 'item not found'}, 404

        attribute_values = []
        for val in item.values:
            attribute = CategoryAttribute.query.get(val.field_id)
            attribute_values.append({
                'attribute_name': attribute.name if attribute else None,
                'value': val.value,
                'field_id': val.field_id
            })

        return {
            'id': item.id,
            'category_id': item.category_id,
            'values': attribute_values
        }
    
    @jwt_required()
    def delete(self, item_id):
        user_id = int(get_jwt_identity())

        item = Item.query.filter_by(id=item_id, owner_id=user_id).first()
        if not item:
            return {'error': 'item not found or unauthorized'}, 404

        db.session.delete(item)
        db.session.commit()
        return {'message': 'item deleted successfully'}, 200

    @items_ns.expect(item_create_input)  # reusing the same model for editing
    @jwt_required()
    def put(self, item_id):
        user_id = int(get_jwt_identity())
        data = items_ns.payload

        item = Item.query.filter_by(id=item_id, owner_id=user_id).first()
        if not item:
            return {'error': 'item not found or unauthorized'}, 404

        category_id = data.get('category_id')
        new_values = data.get('values', [])

        if category_id != item.category_id:
            return {'error': 'changing item category is not allowed'}, 400

        # clear old values
        ItemAttributeValue.query.filter_by(item_id=item.id).delete()

        # insert new values
        for val in new_values:
            field_id = val.get('field_id')
            value = val.get('value')

            attribute = CategoryAttribute.query.filter_by(id=field_id, category_id=category_id).first()
            if not attribute:
                return {'error': f'attribute ID {field_id} does not belong to category {category_id}'}, 400

            item_value = ItemAttributeValue(
                item_id=item.id,
                field_id=field_id,
                value=value
            )
            db.session.add(item_value)

        db.session.commit()
        return {'message': 'item updated successfully'}, 200
    
@items_ns.route('/all/<int:category_id>')
class ItemListResource(Resource):
    @items_ns.marshal_list_with(item_model)
    @jwt_required()
    def get(self, category_id):
        user_id = get_jwt_identity()

        # fetch items owned by user and belonging to the given category
        items = Item.query.filter_by(owner_id=user_id, category_id=category_id).all()

        result = []
        for item in items:
            # only fetch the first attribute value (if it exists)
            first_value = item.values[0] if item.values else None

            attribute_data = []
            if first_value:
                attribute = CategoryAttribute.query.get(first_value.field_id)
                attribute_data.append({
                    'attribute_name': attribute.name if attribute else None,
                    'value': first_value.value
                })

            result.append({
                'id': item.id,
                'category_id': item.category_id,
                'values': attribute_data
            })

        return result


@items_ns.route('')
class ItemListResource(Resource):
    @items_ns.expect(item_create_input)
    @items_ns.response(201, 'item created successfully')
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = items_ns.payload

        category_id = data.get('category_id')
        values = data.get('values', [])

        # Validate category ownership
        category = Category.query.filter_by(id=category_id, owner_id=user_id).first()
        if not category:
            return {'error': 'invalid category or access denied'}, 403

        # create the item
        new_item = Item(category_id=category_id, owner_id=user_id)
        db.session.add(new_item)
        db.session.flush()  # get new_item.id

        # add attribute values
        for val in values:
            field_id = val.get('field_id')
            value = val.get('value')

            # validate the field belongs to this category
            attribute = CategoryAttribute.query.filter_by(id=field_id, category_id=category_id).first()
            if not attribute:
                return {'error': f'attribute ID {field_id} does not belong to category {category_id}'}, 400

            item_value = ItemAttributeValue(
                item_id=new_item.id,
                field_id=field_id,
                value=value
            )
            db.session.add(item_value)

        db.session.commit()
        return {'message': 'item created successfully'}, 201