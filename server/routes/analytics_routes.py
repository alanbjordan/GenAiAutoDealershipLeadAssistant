from flask import Blueprint, request, jsonify, send_file
from helpers.cors_helpers import pre_authorized_cors_preflight
from services.analytics_service import store_request_analytics
from services.analytics_helpers import get_analytics_summary
from models.sql_models import AnalyticsData
from database.session import ScopedSession
import csv
import io
from datetime import datetime

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
        success, updated_analytics = store_request_analytics(token_usage, cost_info, model)
        
        if success:
            return jsonify({
                "message": "Analytics data stored successfully",
                "analytics": updated_analytics
            }), 200
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

@pre_authorized_cors_preflight
@analytics_bp.route("/analytics/reset", methods=["POST"])
def reset_analytics():
    """Reset all analytics data."""
    try:
        # Delete all records from the analytics_data table
        ScopedSession.query(AnalyticsData).delete()
        ScopedSession.commit()
        
        # Get the updated analytics summary (should be empty)
        updated_analytics = get_analytics_summary()
        
        return jsonify({
            "message": "Analytics data reset successfully",
            "analytics": updated_analytics
        }), 200
    except Exception as e:
        print("DEBUG: Exception encountered in reset analytics:", e)
        import traceback
        traceback.print_exc()
        ScopedSession.rollback()
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@analytics_bp.route("/analytics/download", methods=["GET"])
def download_report():
    """Generate and download analytics report."""
    try:
        # Get all analytics data
        analytics_data = ScopedSession.query(AnalyticsData).order_by(AnalyticsData.date.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date',
            'Model',
            'Prompt Tokens',
            'Completion Tokens',
            'Total Tokens',
            'Prompt Cost',
            'Completion Cost',
            'Total Cost'
        ])
        
        # Write data
        for record in analytics_data:
            writer.writerow([
                record.date.strftime("%Y-%m-%d %H:%M:%S"),
                record.model,
                record.prompt_tokens,
                record.completion_tokens,
                record.total_tokens,
                float(record.prompt_cost),
                float(record.completion_cost),
                float(record.total_cost)
            ])
        
        # Prepare the response
        output.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'analytics_report_{timestamp}.csv'
        )

    except Exception as e:
        print("DEBUG: Exception encountered in download report:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500 