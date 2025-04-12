# This file defines the SQLAlchemy models for the car inventory system.
# server/models/sql_models.py
from datetime import datetime
from database import db  

# Define the CarInventory model
class CarInventory(db.Model):
    __tablename__ = "car_inventory"

    id = db.Column(db.Integer, primary_key=True)
    stock_number = db.Column(db.String(50), unique=True, nullable=False)
    vin = db.Column(db.String(50), unique=True, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    mileage = db.Column(db.Integer, nullable=True)
    color = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CarInventory {self.stock_number} - {self.make} {self.model}>"