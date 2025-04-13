# This file defines the SQLAlchemy models for the car inventory system.
# server/models/sql_models.py
from datetime import datetime
from database import db,bcrypt  

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

# Define the AutoLead model
class AutoLead(db.Model):
    __tablename__ = "auto_leads"

    id = db.Column(db.Integer, primary_key=True)
    # Add other fields as needed based on your database schema
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to interactions
    interactions = db.relationship('AutoLeadInteractionDetails', backref='lead', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AutoLead {self.id}>"

# Define the AutoLeadInteractionDetails model
class AutoLeadInteractionDetails(db.Model):
    __tablename__ = "auto_leads_interaction_details"

    interaction_id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('auto_leads.id', ondelete='CASCADE'), nullable=True)
    conversation_transcript = db.Column(db.Text, nullable=True)
    conversation_summary = db.Column(db.Text, nullable=True)
    sentiment = db.Column(db.String(20), nullable=True)
    product_keywords = db.Column(db.ARRAY(db.String), nullable=True)
    priority_flag = db.Column(db.Boolean, default=False)
    next_steps_recommendation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AutoLeadInteractionDetails {self.interaction_id}>"

# Define the ConversationSummary model
class ConversationSummary(db.Model):
    __tablename__ = "conversation_summaries"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(100), unique=True, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)  # positive, neutral, negative
    keywords = db.Column(db.JSON, nullable=True)  # Store as JSON array
    summary = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(50), nullable=False)  # Sales, Service, Management, etc.
    insights = db.Column(db.JSON, nullable=True)  # Store additional insights as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ConversationSummary {self.conversation_id} - {self.department}>"