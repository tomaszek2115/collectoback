from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.models import User
from app import db

#namespace for Auth-related operations
auth_ns = Namespace('auth', description='Authentication related operations')

# bcrypt instance for password hashing
bcrypt = Bcrypt()

# user model for validation via Flask-RESTX
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

        # input validation
        if not email or not password:
            return {"error": "email and password are required"}, 400

        if User.query.filter_by(email=email).first():
            return {"error": "email already taken"}, 409

        # hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # create new user and save to DB
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'account created successfully'}, 201


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = auth_ns.payload
        email = data.get('email')
        password = data.get('password')

        # find user in DB
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # generate JWT token on successful login
            access_token = create_access_token(identity=str(user.id))
            return {'access_token': access_token}, 200
        else:
            return {'error': 'invalid email or password'}, 401