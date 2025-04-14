from flask import Blueprint, request, jsonify
from helpers.cors_helpers import pre_authorized_cors_preflight
from services.chat_service import process_chat, process_tool_call, generate_summary, get_summary

chat_bp = Blueprint("chat", __name__)

@pre_authorized_cors_preflight
@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages from users."""
    try:
        data = request.get_json(force=True)
        print("DEBUG: Received request JSON:", data)

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Get the user message and conversation history
        user_message = data.get("message", "").strip()
        conversation_history = data.get("conversation_history", [])
        
        print("DEBUG: Initial conversation history:", conversation_history)

        # Process the chat message
        result, status_code = process_chat(user_message, conversation_history)
        return jsonify(result), status_code

    except Exception as e:
        print("DEBUG: Exception encountered:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@chat_bp.route("/tool-call-result", methods=["POST"])
def tool_call_result():
    """Handle tool call results."""
    try:
        data = request.get_json(force=True)
        print("DEBUG: Received tool call result request JSON:", data)

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Get the conversation history
        conversation_history = data.get("conversation_history", [])
        
        # Process the tool call
        result, status_code = process_tool_call(conversation_history)
        return jsonify(result), status_code

    except Exception as e:
        print("DEBUG: Exception encountered in tool call result:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@chat_bp.route("/generate-summary", methods=["POST"])
def generate_summary_endpoint():
    """Generate a summary for a conversation."""
    try:
        data = request.get_json(force=True)
        print("DEBUG: Received generate summary request JSON:", data)

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Get the conversation history and optional conversation ID
        conversation_history = data.get("conversation_history", [])
        conversation_id = data.get("conversation_id")
        
        # Generate the summary
        result, status_code = generate_summary(conversation_history, conversation_id)
        return jsonify(result), status_code

    except Exception as e:
        print("DEBUG: Exception encountered in generate summary:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@chat_bp.route("/get-summary/<conversation_id>", methods=["GET"])
def get_summary_endpoint(conversation_id):
    """Get a summary for a conversation by ID."""
    try:
        print(f"DEBUG: Retrieving summary for conversation ID: {conversation_id}")
        
        # Get the summary
        result, status_code = get_summary(conversation_id)
        return jsonify(result), status_code

    except Exception as e:
        print("DEBUG: Exception encountered in get summary:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500 