from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Category, CategoryAttribute, Follow, Item
from app import db

explore_ns = Namespace('explore', description='explore related operations')

def is_following(current_user_id, target_user_id):
    return Follow.query.filter_by(follower_id=current_user_id, followed_id=target_user_id).first() is not None

@explore_ns.route('/<int:user_id>/categories')
class ExploreCategoriesResource(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user_id = get_jwt_identity()

        if not is_following(current_user_id, user_id):
            return {'error': 'You are not following this user'}, 403

        categories = Category.query.filter_by(owner_id=user_id).all()
        return [{'id': cat.id, 'name': cat.name} for cat in categories], 200

@explore_ns.route('/<int:user_id>/items/<int:category_id>')
class ExploreItemsResource(Resource):
    @jwt_required()
    def get(self, user_id, category_id):
        current_user_id = get_jwt_identity()

        if not is_following(current_user_id, user_id):
            return {'error': 'You are not following this user'}, 403

        items = Item.query.filter_by(owner_id=user_id, category_id=category_id).all()
        result = []

        for item in items:
            attribute_values = []
            for val in item.values:
                attr = CategoryAttribute.query.get(val.field_id)
                attribute_values.append({
                    'attribute_name': attr.name if attr else None,
                    'value': val.value
                })

            result.append({
                'id': item.id,
                'category_id': item.category_id,
                'values': attribute_values
            })

        return result, 200
