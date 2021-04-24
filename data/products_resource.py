import datetime

from flask import jsonify
from flask_restful import abort, Resource
from . import db_session
from .products import Product
from .users_resource import abort_if_user_not_found
from flask_restful import reqparse

# PRODUCTS POST
products_post_resource_parser = reqparse.RequestParser()
products_post_resource_parser.add_argument('user_id', required=True, type=int)
products_post_resource_parser.add_argument('title', required=True, type=str)
products_post_resource_parser.add_argument('cost', required=True, type=int)
products_post_resource_parser.add_argument('content', required=True, type=str)
products_post_resource_parser.add_argument('contact_number', required=True, type=str)
products_post_resource_parser.add_argument('is_showing_by_user', required=True, type=bool)

# PRODUCTS PUT
products_put_resource_parser = reqparse.RequestParser()
products_post_resource_parser.add_argument('user_id', type=int)
products_post_resource_parser.add_argument('title', type=str)
products_post_resource_parser.add_argument('cost', type=int)
products_post_resource_parser.add_argument('content', type=str)
products_post_resource_parser.add_argument('contact_number', type=str)
products_post_resource_parser.add_argument('is_showing_by_user', type=bool)


class ProductsResource(Resource):
    def get(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        return jsonify({'product': product.to_dict()})

    def delete(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        session.delete(product)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        args = products_put_resource_parser.parse_args()
        if args['user_id']:
            abort_if_user_not_found(int(args['user_id']))

        for key in args:
            if args[key]:
                setattr(product, key, args[key])
        session.commit()
        return jsonify({'success': 'OK'})


class ProductsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Product).all()
        return jsonify({'products': [item.to_dict() for item in products]})

    def post(self):
        args = products_post_resource_parser.parse_args()
        abort_if_user_not_found(int(args['user_id']))
        session = db_session.create_session()
        product = Product(
            user_id=args.get("user_id"),
            cost=args.get("cost"),
            title=args.get("title"),
            content=args.get("content"),
            created_date=datetime.datetime.now(),
            contact_number=args.get("contact_number"),
            is_showing_by_user=args.get("is_showing_by_user"),
            is_showing_by_admin=False,
        )
        product.reinitialized_indexes()

        session.add(product)
        session.commit()
        return jsonify({'success': 'OK'})


def abort_if_product_not_found(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    if not product:
        abort(404, message=f"Product {product_id} not found")
