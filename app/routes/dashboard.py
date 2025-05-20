from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

dashboard_ns = Namespace('dashboard', description='Dashboard related operations')

# User output model
user_model = dashboard_ns.model('User_dashboard', {
    'id': fields.Integer,
    'email': fields.String,
})

@dashboard_ns.route('/user')
class CurrentUserResource(Resource):
    @dashboard_ns.marshal_with(user_model)
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            dashboard_ns.abort(404, 'User not found')
        return user