from flask import Blueprint, request, jsonify
from helpers.cors_helpers import pre_authorized_cors_preflight
from services.inventory_service import get_all_inventory, search_cars, get_car_review_videos

inventory_bp = Blueprint("inventory", __name__)

@pre_authorized_cors_preflight
@inventory_bp.route("/inventory", methods=["GET"])
def get_inventory():
    """Get all cars from the inventory."""
    try:
        # Get all inventory
        result, status_code = get_all_inventory()
        return jsonify(result), status_code
    except Exception as e:
        print(f"Error in get_inventory endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@inventory_bp.route("/search-cars", methods=["POST"])
def search_cars_endpoint():
    """Search for cars based on filter criteria."""
    try:
        data = request.get_json(force=True)
        
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400
        
        # Search for cars
        result, status_code = search_cars(data)
        return jsonify(result), status_code
    except Exception as e:
        print(f"Error in search_cars endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@inventory_bp.route("/car-review-videos", methods=["POST"])
def car_review_videos():
    """Search for car review videos on YouTube."""
    try:
        data = request.get_json(force=True)
        
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400
        
        car_make = data.get("car_make")
        car_model = data.get("car_model")
        year = data.get("year")
        
        # Get car review videos
        result, status_code = get_car_review_videos(car_make, car_model, year)
        return jsonify(result), status_code
    except Exception as e:
        print(f"Error in car_review_videos endpoint: {str(e)}")
        return jsonify({"videos": [], "error": str(e)}), 500 