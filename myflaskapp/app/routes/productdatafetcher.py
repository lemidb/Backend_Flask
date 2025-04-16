from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Item, Product, User, db
from ..commands.getdatafromamazon import  get_product_data_sync
from ..commands.scrapewithllm import scrape_amazon_products_with_llm

product_bp = Blueprint('productdatafetcher', __name__)

@product_bp.route('/', methods=['GET'])
@jwt_required()
def get_product_data():
    """Get product info from amazon and return it"""
    try:
        # Get the product name from query parameters
        product_name = request.args.get('product_name')
        if not product_name:
            return jsonify({"error": "Product name is required"}), 400
        # product_data = get_product_data_sync(product_name)
        product_data = scrape_amazon_products_with_llm(product_name)
        return jsonify(product_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@product_bp.route('/', methods=['POST'])
@jwt_required()
def add_product_data():
    """Add product data to the database"""
    try:
        data = request.json
        product_data = Product(name=data['name'], price=data['price'], description=data['description'], image_url=data['image_url'], owner_id=get_jwt_identity())
        db.session.add(product_data)
        db.session.commit()
        return jsonify(product_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

