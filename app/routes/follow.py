from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Category, CategoryAttribute, Follow, User
from app import db

follow_ns = Namespace('follow', description='follow related operations')

@follow_ns.route('/<string:email>')
class FollowUserResource(Resource):
    @follow_ns.doc(description="Follow another user by their email")
    @jwt_required()
    def post(self, email):
        follower_id = get_jwt_identity()
        email = email

        if not email:
            return {'error': 'Email is required'}, 400

        # Find the user to follow
        user_to_follow = User.query.filter_by(email=email).first()
        if not user_to_follow:
            return {'error': 'User with this email does not exist'}, 404

        if user_to_follow.id == follower_id:
            return {'error': 'You cannot follow yourself'}, 400

        # Check if already following
        existing_follow = Follow.query.filter_by(
            follower_id=follower_id,
            followed_id=user_to_follow.id
        ).first()
        if existing_follow:
            return {'message': 'Already following this user'}, 200

        # Create follow relationship
        follow = Follow(follower_id=follower_id, followed_id=user_to_follow.id)
        db.session.add(follow)
        db.session.commit()

        return {'message': f'Now following {email}'}, 201

@follow_ns.route('/')
class FollowListResource(Resource):
    @follow_ns.doc(description="Show all followed users")
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        followed = Follow.query.filter_by(follower_id=user_id).all()
        followed_ids = [f.followed_id for f in followed]
        followed_users = User.query.filter(User.id.in_(followed_ids)).all()
        result = [
            {'id': user.id, 'email': user.email}
            for user in followed_users if user
        ]
        return {'followed users': result}, 200