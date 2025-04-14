from models.sql_models import CarInventory
from helpers.llm_utils import fetch_cars, find_car_review_videos

def get_all_inventory():
    """Get all cars from the inventory."""
    try:
        # Query all cars from the inventory
        cars = CarInventory.query.all()
        
        # Convert the cars to a list of dictionaries
        inventory = []
        for car in cars:
            inventory.append({
                'id': car.id,
                'stock_number': car.stock_number,
                'vin': car.vin,
                'make': car.make,
                'model': car.model,
                'year': car.year,
                'price': float(car.price),
                'mileage': car.mileage,
                'color': car.color,
                'description': car.description
            })
        
        return inventory, 200
    except Exception as e:
        print(f"Error fetching inventory: {str(e)}")
        return {"error": "Failed to fetch inventory"}, 500

def search_cars(filter_params):
    """Search for cars based on filter criteria."""
    try:
        result = fetch_cars(filter_params)
        return result, 200
    except Exception as e:
        print(f"Error searching cars: {str(e)}")
        return {"error": "Failed to search cars"}, 500

def get_car_review_videos(car_make, car_model, year=None):
    """Get car review videos for a specific car."""
    try:
        if not car_make or not car_model:
            return {"videos": [], "error": "Car make and model are required"}, 400
        
        result = find_car_review_videos(car_make, car_model, year)
        return result, 200
    except Exception as e:
        print(f"Error getting car review videos: {str(e)}")
        return {"videos": [], "error": str(e)}, 500 