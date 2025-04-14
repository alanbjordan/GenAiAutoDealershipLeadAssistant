from datetime import datetime
from models.sql_models import AnalyticsData
from database import db

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