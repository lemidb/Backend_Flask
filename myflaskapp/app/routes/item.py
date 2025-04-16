from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Item, User, db

item_bp = Blueprint('items', __name__)

@item_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_data():
    """Get all items for the authenticated user."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    items = Item.query.filter_by(owner_id=user.id).all()
    return jsonify([{"id": item.id, "name": item.name, "value": item.value} for item in items])

@item_bp.route('/<int:item_id>', methods=['GET'])
@jwt_required()
def get_item(item_id):
    """Get specific item."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    item = Item.query.filter_by(id=item_id, owner_id=user.id).first()

    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    return jsonify({"id": item.id, "name": item.name, "value": item.value})

@item_bp.route('/', methods=['POST'])
@jwt_required()
def create_item():
    """Create a new item."""
    data = request.json
    if not data.get('name'):
        return jsonify({"error": "Name is required"}), 400
    
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    new_item = Item(name=data['name'], value=data.get('value'), owner_id=user.id)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"id": new_item.id, "name": new_item.name, "value": new_item.value}), 201

@item_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    """Update an existing item."""
    data = request.json
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    item = Item.query.filter_by(id=item_id, owner_id=user.id).first()

    if not item:
        return jsonify({"error": "Item not found"}), 404

    item.name = data.get('name', item.name)
    item.value = data.get('value', item.value)

    db.session.commit()
    return jsonify({"id": item.id, "name": item.name, "value": item.value})

@item_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    """Delete an item."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    item = Item.query.filter_by(id=item_id, owner_id=user.id).first()

    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted successfully"}), 200
