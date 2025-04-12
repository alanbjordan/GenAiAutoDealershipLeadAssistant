# routes/all_routes.py

# Importing necessary libraries
from flask import Blueprint, jsonify, request
from helpers.cors_helpers import pre_authorized_cors_preflight
import pandas as pd
from helpers.llm_utils import generate_llm_natural_output  # This function now generates a natural chat response

# Blueprint for all routes
all_routes_bp = Blueprint('all_routes', __name__)

# Chat Endpoint
@pre_authorized_cors_preflight
@all_routes_bp.route('/chat', methods=['POST'])
def chat_route():
    # Extract the JSON payload from the request
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Extract the user's message content from the payload
    user_message = data.get("message_content", "")
    if not user_message:
        return jsonify({'error': 'message_content field is required.'}), 400

    # Generate a chat response based on the user's input.
    # The LLM utility is designed to consider the context (e.g., querying PostgreSQL for matching cars)
    chat_response = generate_llm_natural_output(user_message)

    # Return the generated chat response along with a success message to the client
    return jsonify({
        'message': 'Chat response generated successfully.',
        'chat_response': chat_response
    }), 200
