from flask import Blueprint, request, jsonify
from helpers.cors_helpers import pre_authorized_cors_preflight
from services.analytics_service import store_request_analytics, get_analytics_summary

analytics_bp = Blueprint("analytics", __name__)

@pre_authorized_cors_preflight
@analytics_bp.route("/analytics/store", methods=["POST"])
def store_analytics():
    """Store analytics data for a request."""
    try:
        data = request.get_json(force=True)
        print("DEBUG: Received analytics data:", data)

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Get the token usage and cost info
        token_usage = data.get("token_usage", {})
        cost_info = data.get("cost", {})
        model = data.get("model", "o3-mini-2025-01-31")
        
        # Store the analytics data
        success = store_request_analytics(token_usage, cost_info, model)
        
        if success:
            return jsonify({"message": "Analytics data stored successfully"}), 200
        else:
            return jsonify({"error": "Failed to store analytics data"}), 500

    except Exception as e:
        print("DEBUG: Exception encountered in store analytics:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@analytics_bp.route("/analytics/summary", methods=["GET"])
def get_summary():
    """Get analytics summary."""
    try:
        # Get the analytics summary
        summary = get_analytics_summary()
        return jsonify(summary), 200

    except Exception as e:
        print("DEBUG: Exception encountered in get analytics summary:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500 