import datetime

from flask import jsonify
from flask_restful import abort, Resource
from . import db_session

from .users import User
from flask_restful import reqparse

# USERS POST
users_post_resource_parser = reqparse.RequestParser()
users_post_resource_parser.add_argument('name', required=True)
users_post_resource_parser.add_argument('email', required=True)
users_post_resource_parser.add_argument('password', required=True)

# USERS PUT
users_put_resource_parser = reqparse.RequestParser()
users_put_resource_parser.add_argument('name')
users_put_resource_parser.add_argument('email')
users_put_resource_parser.add_argument('password')


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict()})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        args = users_put_resource_parser.parse_args()

        for key in args:
            if args[key]:
                setattr(user, key, args[key])

        if args.get('password', False):
            user.set_password(args['password'])
        user.modified_date = datetime.datetime.now()

        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        args = users_post_resource_parser.parse_args()
        abort_if_user_email_already_registered(args['email'])
        session = db_session.create_session()
        user = User()
        for key in args:
            setattr(user, key, args[key])
        user.set_password(args['password'])
        user.modified_date = datetime.datetime.now()

        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")


def abort_if_user_email_already_registered(user_email):
    session = db_session.create_session()
    users = session.query(User).filter(User.email == user_email).first()
    if users:
        abort(404, message=f"User with email {user_email} already exists")
