import os
import json
import traceback
from flask import Blueprint, request, jsonify
from openai import OpenAI 
from helpers.cors_helpers import pre_authorized_cors_preflight
from models.sql_models import CarInventory 
from database import db
from helpers.llm_utils import fetch_cars 

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

        # Get the user message and conversation history
        user_message = data.get("message", "").strip()
        conversation_history = data.get("conversation_history", [])
        
        if not isinstance(conversation_history, list):
            conversation_history = []

        print("DEBUG: Initial conversation history:", conversation_history)

        if not user_message:
            return jsonify({"error": "No 'message' provided"}), 400

        # Define the system message
        system_message = {
            "role": "system",
            "content": (
                """ 
                You are Patricia, a knowledgeable and friendly car sales agent at Nissan of Hendersonville, a family-owned and operated Nissan dealership in Hendersonville, North Carolina.
                
                IMPORTANT: You must ONLY provide information that is explicitly stated in this system message. DO NOT make up or guess any information about the dealership, including:
                - Business hours
                - Address
                - Phone number
                - Website
                - Staff names
                - Available vehicles
                - Pricing
                
                If asked for information not provided in this message, politely inform the customer that you need to verify that information and suggest they call the dealership directly.
                
                Your primary responsibilities:
                - Help customers find the perfect Nissan vehicle that meets their needs and budget
                - Provide accurate information about Nissan models, features, pricing, and availability
                - Assist with scheduling test drives and answering questions about the car buying process
                - Represent the dealership with professionalism and enthusiasm
                
                Company Information (VERIFY ALL INFORMATION BEFORE PROVIDING):
                - Name: Nissan of Hendersonville
                - Address: 1340 Spartanburg Hwy, Hendersonville, NC 28792
                - Phone: +1 (828) 697-2222
                - Website: https://www.nissanofhendersonville.com
                
                Business Hours (VERIFY ALL INFORMATION BEFORE PROVIDING):
                - Monday-Friday: 7 AM - 6 PM
                - Saturday: 7 AM - 6 PM
                - Sunday: Closed
                
                When customers ask about inventory, use the fetch_cars function to provide accurate, up-to-date information. Always supply default values for any missing filters: use -1 for numeric fields and an empty string for text fields.
                
                Remember that you are representing a family-owned business that prides itself on customer service and helping customers find the perfect car. Be helpful, friendly, and professional in all interactions.
                
                NEVER schedule appointments for days when the dealership is closed (like Sundays).
                NEVER provide information about test drives without verifying the customer's contact information first.
                NEVER make up information about the dealership or its staff.
                """
            )
        }
        
        # Check if the conversation history already has a system message
        has_system_message = any(msg.get("role") == "system" for msg in conversation_history)
        
        # If no conversation history or no system message, add the system message
        if not conversation_history or not has_system_message:
            # Insert the system message at the beginning of the conversation history
            conversation_history.insert(0, system_message)
            print("DEBUG: Added system message to conversation history.")

        # Call ChatCompletion API using the new tools syntax
        completion = client.chat.completions.create(
            model="o3-mini-2025-01-31",
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
                    
                    # Add the result as an assistant message
                    result_message = {
                        "role": "assistant",
                        "content": f"Here are the car details I found: {json.dumps(result)}"
                    }
                    conversation_history.append(result_message)
                    
                    print("DEBUG: Updated conversation history after tool call:", conversation_history)
                    completion = client.chat.completions.create(
                        model="o3-mini-2025-01-31",
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

        # Append the assistant's response to the conversation history
        # Remove the tool_calls from the message to avoid the error
        conversation_history.append({
            "role": "assistant",
            "content": assistant_response
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
