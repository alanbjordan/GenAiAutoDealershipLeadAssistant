from database import db
from models.sql_models import CarInventory

def fetch_cars(filter_params: dict) -> list:
    """
    Query the CarInventory table based on provided filter criteria.
    
    If the user does not provide a parameter or provides -1 for numeric fields,
    the function will skip applying that filter.
    
    :param filter_params: A dictionary with keys such as:
        {
            "make": <str>,         # Car manufacturer (non-empty string to filter)
            "model": <str>,        # Car model (non-empty string to filter)
            "year": <int>,         # Minimum car model year (-1 means no filtering)
            "max_year": <int>,     # Maximum car model year (-1 means no filtering)
            "price": <float>,      # Minimum price (-1 means no filtering)
            "max_price": <float>,  # Maximum price (-1 means no filtering)
            "mileage": <int>,      # Maximum mileage (-1 means no filtering)
            "color": <str>,        # Car color (non-empty string to filter)
            "stock_number": <str>, # Exact stock number (non-empty string to filter)
            "vin": <str>           # Exact vehicle identification number (non-empty string to filter)
        }
    :return: A list of dictionaries, each representing a car in the inventory.
    """
    query = db.session.query(CarInventory)
    
    # Check string filters only if they are non-empty
    if "make" in filter_params and filter_params["make"]:
        query = query.filter(CarInventory.make.ilike(f"%{filter_params['make']}%"))
    if "model" in filter_params and filter_params["model"]:
        query = query.filter(CarInventory.model.ilike(f"%{filter_params['model']}%"))
    if "color" in filter_params and filter_params["color"]:
        query = query.filter(CarInventory.color.ilike(f"%{filter_params['color']}%"))
    if "stock_number" in filter_params and filter_params["stock_number"]:
        query = query.filter(CarInventory.stock_number == filter_params["stock_number"])
    if "vin" in filter_params and filter_params["vin"]:
        query = query.filter(CarInventory.vin == filter_params["vin"])
    
    # Check numeric filters only if they are provided and not equal to -1
    if "year" in filter_params and filter_params["year"] != -1:
        query = query.filter(CarInventory.year >= filter_params["year"])
    if "max_year" in filter_params and filter_params["max_year"] != -1:
        query = query.filter(CarInventory.year <= filter_params["max_year"])
    if "price" in filter_params and filter_params["price"] != -1:
        query = query.filter(CarInventory.price >= filter_params["price"])
    if "max_price" in filter_params and filter_params["max_price"] != -1:
        query = query.filter(CarInventory.price <= filter_params["max_price"])
    if "mileage" in filter_params and filter_params["mileage"] != -1:
        query = query.filter(CarInventory.mileage <= filter_params["mileage"])
    
    results = query.all()
    
    def to_dict(car: CarInventory) -> dict:
        return {
            "stock_number": car.stock_number,
            "vin": car.vin,
            "make": car.make,
            "model": car.model,
            "year": car.year,
            "price": float(car.price),
            "mileage": car.mileage,
            "color": car.color,
            "description": car.description,
            "created_at": car.created_at.isoformat() if car.created_at else None
        }
    
    return [to_dict(c) for c in results]
