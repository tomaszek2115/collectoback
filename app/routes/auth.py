from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.models import User
from app import db

# Namespace for Auth-related operations
auth_ns = Namespace('auth', description='Authentication related operations')

# Bcrypt instance for password hashing
bcrypt = Bcrypt()

# User model for validation via Flask-RESTX
user_model = auth_ns.model('User_auth', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = auth_ns.payload
        email = data.get('email')
        password = data.get('password')

        # Input validation
        if not email or not password:
            return {"error": "Email and password are required"}, 400

        if User.query.filter_by(email=email).first():
            return {"error": "Email already taken"}, 409

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create new user and save to DB
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'Account created successfully'}, 201


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = auth_ns.payload
        email = data.get('email')
        password = data.get('password')

        # Find user in DB
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # Generate JWT token on successful login
            access_token = create_access_token(identity=str(user.id))
            return {'access_token': access_token}, 200
        else:
            return {'error': 'Invalid email or password'}, 401