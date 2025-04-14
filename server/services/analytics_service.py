# server/services/analytics_service.py

from datetime import datetime
from models.sql_models import AnalyticsData
from database.session import ScopedSession
from services.websocket_service import emit_analytics_update
from services.analytics_helpers import get_analytics_summary as get_summary_helper

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
        ScopedSession.add(analytics)
        ScopedSession.commit()
        
        # Get the updated analytics summary
        updated_analytics = get_summary_helper()
        
        # Emit WebSocket update after successful storage
        emit_analytics_update()
        
        return True, updated_analytics
    except Exception as e:
        print(f"Error storing analytics data: {e}")
        ScopedSession.rollback()
        return False, None

# The get_analytics_summary function has been moved to analytics_helpers.py
# This function is kept for backward compatibility
def get_analytics_summary():
    """Get summary of analytics data."""
    return get_summary_helper() 