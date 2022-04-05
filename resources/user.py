import traceback
from flask import request
from flask_restful import Resource
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
)
from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.user import UserSchema
from blocklist import BLOCKLIST

BLANK_ERROR = "'{}' cannot be left blank"
USER_ALREADY_EXIST = "A user with that username already exists."
EMAIL_ALREADY_EXIST = "A user with that email already exists."
USER_CREATED = "User created successfully. Please check your email for activation."
USER_NOT_FOUND = "User not found."
USER_DELETED = "User deleted."
LOGIN_ERROR = "Invalid credentials!"
LOGOUT_SUCCESS = "User <id={}> successfully logged out."
NOT_CONFIRMED_ERROR = "<{}> has not confirmed the email."
USER_CONFIRMED = "User confirmed."
FAILED_TO_CREATE = "Internal server error. Failed to create user."

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user.username):
            return {"message": USER_ALREADY_EXIST}, 400
        
        if UserModel.find_by_email(user.email):
            return {"message": EMAIL_ALREADY_EXIST}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
        except MailGunException as me:
            user.delete_from_db()
            return {"message": str(me)}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": FAILED_TO_CREATE}, 500

        return {"message": USER_CREATED}, 201


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating user_data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_data = user_schema.load(request.get_json(), partial=("email",))

        user = UserModel.find_by_username(user_data.username)

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user.password, user_data.password):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            return {"message": NOT_CONFIRMED_ERROR.format(user.username)}, 400

        return {"message": LOGIN_ERROR}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLOCKLIST.add(jti)
        return {"message": LOGOUT_SUCCESS.format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
        