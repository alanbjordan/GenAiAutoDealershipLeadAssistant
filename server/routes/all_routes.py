from flask import Blueprint, jsonify, request
from helpers.cors_helpers import pre_authorized_cors_preflight
from helpers.llm_utils import generate_llm_natural_output

all_routes_bp = Blueprint('all_routes', __name__)

@pre_authorized_cors_preflight
@all_routes_bp.route('/chat', methods=['POST'])
def chat_route():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    user_message = data.get("message_content", "")
    if not user_message:
        return jsonify({'error': 'message_content field is required.'}), 400

    # Accept thread_id from the client if it exists.
    if "thread_id" not in data:
        thread_id = None
        result = generate_llm_natural_output(user_message)
    else:
        thread_id = data.get("thread_id")
        result = generate_llm_natural_output(user_message, thread_id)

    # Ensure that we always return a response regardless of the branch.
    return jsonify(result), 200
