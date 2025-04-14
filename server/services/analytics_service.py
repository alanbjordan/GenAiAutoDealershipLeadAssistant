# server/services/analytics_service.py

from datetime import datetime
from models.sql_models import AnalyticsData
from database import db

def store_request_analytics(token_usage, cost_info, model="o3-mini-2025-01-31"):
    """Store analytics data for a request."""
    try:
        # Check if token_usage is a dictionary or an object with attributes
        if hasattr(token_usage, 'prompt_tokens'):
            # It's an object with attributes
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
        else:
            # It's a dictionary
            prompt_tokens = token_usage["prompt_tokens"]
            completion_tokens = token_usage["completion_tokens"]
            total_tokens = token_usage["total_tokens"]
            
        analytics = AnalyticsData(
            date=datetime.utcnow(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            prompt_cost=cost_info["prompt_cost"],
            completion_cost=cost_info["completion_cost"],
            total_cost=cost_info["total_cost"]
        )
        db.session.add(analytics)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error storing analytics data: {e}")
        db.session.rollback()
        return False

def get_analytics_summary():
    """Get summary of analytics data."""
    try:
        # Get total cost
        total_cost = db.session.query(db.func.sum(AnalyticsData.total_cost)).scalar() or 0
        
        # Get total requests
        total_requests = db.session.query(db.func.count(AnalyticsData.id)).scalar() or 0
        
        # Calculate average cost per request
        average_cost = total_cost / total_requests if total_requests > 0 else 0
        
        # Get total tokens
        total_sent_tokens = db.session.query(db.func.sum(AnalyticsData.prompt_tokens)).scalar() or 0
        total_received_tokens = db.session.query(db.func.sum(AnalyticsData.completion_tokens)).scalar() or 0
        
        # Get recent requests
        recent_requests = db.session.query(AnalyticsData).order_by(AnalyticsData.date.desc()).limit(10).all()
        
        # Format recent requests
        requests_by_date = [{
            "date": req.date.strftime("%Y-%m-%d %H:%M:%S"),
            "model": req.model,
            "sentTokens": req.prompt_tokens,
            "receivedTokens": req.completion_tokens,
            "cost": float(req.total_cost)  # Convert to float explicitly
        } for req in recent_requests]
        
        # Get cost by model
        cost_by_model = {}
        model_costs = db.session.query(
            AnalyticsData.model,
            db.func.sum(AnalyticsData.total_cost).label('total_cost')
        ).group_by(AnalyticsData.model).all()
        
        for model, cost in model_costs:
            cost_by_model[model] = float(cost)
        
        return {
            "totalCost": float(total_cost),
            "totalRequests": total_requests,
            "averageCostPerRequest": float(average_cost),
            "totalSentTokens": int(total_sent_tokens),
            "totalReceivedTokens": int(total_received_tokens),
            "requestsByDate": requests_by_date,
            "costByModel": cost_by_model
        }
    except Exception as e:
        print(f"Error getting analytics summary: {e}")
        return {
            "totalCost": 0,
            "totalRequests": 0,
            "averageCostPerRequest": 0,
            "totalSentTokens": 0,
            "totalReceivedTokens": 0,
            "requestsByDate": [],
            "costByModel": {}
        } 