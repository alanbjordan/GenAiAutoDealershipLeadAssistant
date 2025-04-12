import os
import json
import traceback
from flask import Blueprint, request, jsonify
from openai import OpenAI  # New import style
from helpers.cors_helpers import pre_authorized_cors_preflight
from models.sql_models import CarInventory  # Ensure your car model is imported
from database import db
from helpers.llm_utils import fetch_cars  # Import the fetch_cars function

# Initialize the OpenAI client using the new syntax
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

all_routes_bp = Blueprint("all_routes", __name__)

tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_cars",
            "description": (
                "Fetch car inventory details based on filter criteria. Users can provide filters "
                "such as make, model, model year range, price range, mileage, color, stock number, or VIN for a precise lookup. "
                "If a parameter is not applicable, please provide -1 for numeric values or an empty string for text values."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "make": {
                        "type": "string",
                        "description": "Car manufacturer (e.g., Toyota, Ford)"
                    },
                    "model": {
                        "type": "string",
                        "description": "Car model (e.g., Camry, Mustang)"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Minimum car model year. Use -1 to indicate no minimum."
                    },
                    "max_year": {
                        "type": "integer",
                        "description": "Maximum car model year. Use -1 to indicate no maximum."
                    },
                    "price": {
                        "type": "number",
                        "description": "Minimum price. Use -1 to indicate no minimum."
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price. Use -1 to indicate no maximum."
                    },
                    "mileage": {
                        "type": "integer",
                        "description": "Maximum mileage. Use -1 to indicate no limit."
                    },
                    "color": {
                        "type": "string",
                        "description": "Car color"
                    },
                    "stock_number": {
                        "type": "string",
                        "description": "Exact stock number"
                    },
                    "vin": {
                        "type": "string",
                        "description": "Exact Vehicle Identification Number"
                    }
                },
                "required": [
                    "make",
                    "model",
                    "year",
                    "max_year",
                    "price",
                    "max_price",
                    "mileage",
                    "color",
                    "stock_number",
                    "vin"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

@pre_authorized_cors_preflight
@all_routes_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        print("DEBUG: Received request JSON:", data)

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Try to get 'message' or fallback to 'message_content'
        user_message = data.get("message") or data.get("message_content", "")
        user_message = user_message.strip()

        conversation_history = data.get("conversation_history", [])
        if not isinstance(conversation_history, list):
            conversation_history = []

        print("DEBUG: Initial conversation history:", conversation_history)

        if not user_message:
            return jsonify({"error": "No 'message' provided"}), 400

        # If no conversation history, add a system message to define the assistant's identity
        if not conversation_history:
            system_message = (
                "You are a car sales agent named Patrica. "
                "Help users with car inventory queries and use function calling if you need to fetch car details. "
                "Always supply default values for any missing filters: use -1 for numeric fields and an empty string for text fields."
            )
            conversation_history.append({"role": "system", "content": system_message})
            print("DEBUG: Added system message to conversation history.")

        # Append the new user message
        conversation_history.append({"role": "user", "content": user_message})
        print("DEBUG: Appended user message:", user_message)

        # Call ChatCompletion API using the new tools syntax
        completion = client.chat.completions.create(
            model="o1-2024-12-17",
            messages=conversation_history,
            tools=tools
        )
        print("DEBUG: Received ChatCompletion API response.")
        message = completion.choices[0].message
        print("DEBUG: Assistant message object:", message)

        # Check if a tool call was triggered
        if message.tool_calls and len(message.tool_calls) > 0:
            tool_call = message.tool_calls[0]
            func_name = tool_call.function.name
            args_str = tool_call.function.arguments
            print("DEBUG: Tool call detected. Function:", func_name, "Arguments string:", args_str)

            try:
                func_args = json.loads(args_str)
                print("DEBUG: Parsed tool call arguments:", func_args)
            except Exception as parse_error:
                print("DEBUG: Error parsing tool arguments:", parse_error)
                assistant_response = "Error parsing tool arguments."
            else:
                if func_name == "fetch_cars":
                    result = fetch_cars(func_args)
                    print("DEBUG: fetch_cars result:", result)
                    conversation_history.append({
                        "role": "function",
                        "name": "fetch_cars",
                        "content": json.dumps(result)
                    })
                    print("DEBUG: Updated conversation history after tool call:", conversation_history)
                    completion = client.chat.completions.create(
                        model="gpt-4o",
                        messages=conversation_history
                    )
                    message = completion.choices[0].message
                    print("DEBUG: Assistant message after tool integration:", message)
                    assistant_response = message.content or ""
                else:
                    assistant_response = f"Unknown tool '{func_name}' called."
                    print("DEBUG: Unknown tool call detected:", func_name)
        else:
            assistant_response = message.content or ""
            print("DEBUG: No tool call detected. Assistant response:", assistant_response)

        # Append final message to conversation history
        conversation_history.append({
            "role": message.role,
            "content": message.content,
            "tool_calls": [
                {
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    },
                    "type": tc.type
                } for tc in message.tool_calls
            ] if message.tool_calls else None
        })
        print("DEBUG: Final conversation history:", conversation_history)

        return jsonify({
            "chat_response": assistant_response,
            "conversation_history": conversation_history
        }), 200

    except Exception as e:
        print("DEBUG: Exception encountered:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
