import os
import json
import traceback
from flask import Blueprint, request, jsonify
from openai import OpenAI 
from helpers.cors_helpers import pre_authorized_cors_preflight
from models.sql_models import CarInventory 
from database import db
from helpers.llm_utils import fetch_cars, generate_conversation_summary, get_conversation_summary

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
                You are Patricia, a knowledgeable and friendly customer support agent at Nissan of Hendersonville, a family-owned and operated Nissan dealership in Hendersonville, North Carolina.
                
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
                - Guide customers that need to schedule a service appointment
                - Handle customer complaints and provide solutions
                
                Company Information (VERIFY ALL INFORMATION BEFORE PROVIDING):
                - Name: Nissan of Hendersonville
                - Address: 1340 Spartanburg Hwy, Hendersonville, NC 28792
                - Phone: +1 (828) 697-2222
                - Website: https://www.nissanofhendersonville.com
                
                Business Hours (VERIFY ALL INFORMATION BEFORE PROVIDING):
                - Monday-Saturday: 9 AM - 7 PM
                - Sunday: Closed
                
                When customers ask about inventory, use the fetch_cars function to provide accurate, up-to-date information. Always supply default values for any missing filters: use -1 for numeric fields and an empty string for text fields.
                
                Remember that you are representing a family-owned business that prides itself on customer service and helping customers find the perfect car. Be helpful, friendly, and professional in all interactions.
                
                NEVER schedule appointments for days when the dealership is closed (like Sundays).
                NEVER provide information about test drives without verifying the customer's contact information first.
                NEVER make up information about the dealership or its staff.
                
                IMPORTANT - Time Awareness:
                You will receive a message with the current time in EST. Use this information to:
                1. Determine if the dealership is currently open or closed
                2. Avoid scheduling appointments outside of business hours
                3. Provide accurate information about when the dealership will be open next
                4. Consider the day of the week when discussing availability
                5. Dont mention the service hours or business hours unless asked or the customer asks about booking an appointment or test drive.
                """
            )
        }
        
        # Check if the conversation history already has a system message
        has_system_message = any(msg.get("role") == "system" and "You are Patricia" in msg.get("content", "") for msg in conversation_history)
        
        # If no conversation history or no system message, add the system message
        if not conversation_history or not has_system_message:
            # Insert the system message at the beginning of the conversation history
            conversation_history.insert(0, system_message)
            print("DEBUG: Added system message to conversation history.")
            
        # Check if there's a time context message in the conversation history
        has_time_context = any(msg.get("role") == "system" and "Current time:" in msg.get("content", "") for msg in conversation_history)
        
        # If no time context message, add one
        if not has_time_context:
            # Get current time in EST using a reliable method
            try:
                from datetime import datetime
                import pytz
                
                # Get current time in EST
                est = pytz.timezone('US/Eastern')
                current_time = datetime.now(est)
                current_time_formatted = current_time.strftime('%Y-%m-%d %H:%M:%S EST')
                print(f"DEBUG: Successfully got time in EST: {current_time_formatted}")
            except Exception as e:
                print(f"DEBUG: Error getting time in EST: {e}")
                # Fallback to a simpler approach
                from datetime import datetime, timedelta
                # EST is UTC-5
                utc_now = datetime.utcnow()
                est_offset = timedelta(hours=-5)
                est_time = utc_now + est_offset
                current_time_formatted = est_time.strftime('%Y-%m-%d %H:%M:%S EST')
                print(f"DEBUG: Using fallback time calculation: {current_time_formatted}")
            
            # Add time context message
            time_context_message = {
                "role": "system",
                "content": f"Current time: {current_time_formatted}"
            }
            conversation_history.append(time_context_message)
            print("DEBUG: Added time context message to conversation history.")

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
        tool_call_detected = False
        if message.tool_calls and len(message.tool_calls) > 0:
            tool_call_detected = True
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
                # For tool calls, we'll just return a placeholder response
                # The actual tool call processing will happen in the tool-call-result endpoint
                assistant_response = "Processing your request..."
        else:
            assistant_response = message.content or ""
            print("DEBUG: No tool call detected. Assistant response:", assistant_response)

        # Append the assistant's response to the conversation history
        # Include the tool_calls property if it exists
        assistant_message = {
            "role": "assistant",
            "content": assistant_response
        }
        
        # If there are tool calls, include them in the message
        if message.tool_calls and len(message.tool_calls) > 0:
            # Convert tool_calls to a dictionary format that can be serialized
            tool_calls_dict = []
            for tool_call in message.tool_calls:
                tool_calls_dict.append({
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                })
            assistant_message["tool_calls"] = tool_calls_dict
        
        conversation_history.append(assistant_message)
        print("DEBUG: Final conversation history:", conversation_history)

        return jsonify({
            "chat_response": assistant_response,
            "conversation_history": conversation_history,
            "tool_call_detected": tool_call_detected
        }), 200

    except Exception as e:
        print("DEBUG: Exception encountered:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@all_routes_bp.route("/tool-call-result", methods=["POST"])
def tool_call_result():
    try:
        data = request.get_json(force=True)
        print("DEBUG: Received tool call result request JSON:", data)

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Get the conversation history
        conversation_history = data.get("conversation_history", [])
        
        if not isinstance(conversation_history, list):
            return jsonify({"error": "Invalid conversation history format"}), 400

        print("DEBUG: Processing tool call with conversation history:", conversation_history)
        print("DEBUG: Conversation history length:", len(conversation_history))
        
        # Print each message in the conversation history for debugging
        for i, msg in enumerate(conversation_history):
            print(f"DEBUG: Message {i}:", msg)
            if msg.get("role") == "assistant":
                print(f"DEBUG: Assistant message {i} content:", msg.get("content"))
                print(f"DEBUG: Assistant message {i} has tool_calls:", "tool_calls" in msg)

        # Find the last assistant message with tool calls
        tool_call_message = None
        for msg in reversed(conversation_history):
            if msg.get("role") == "assistant" and "tool_calls" in msg:
                tool_call_message = msg
                print("DEBUG: Found assistant message with tool_calls:", msg)
                break
        
        # If no message with tool_calls is found, check for the last assistant message
        if not tool_call_message:
            for msg in reversed(conversation_history):
                if msg.get("role") == "assistant":
                    tool_call_message = msg
                    print("DEBUG: Found assistant message without tool_calls:", msg)
                    break
        
        if not tool_call_message:
            return jsonify({"error": "No assistant message found in conversation history"}), 400
            
        # Check if the message has tool_calls
        if not tool_call_message.get("tool_calls"):
            # If the message doesn't have tool_calls, check if it's the "Processing your request..." message
            if tool_call_message.get("content") == "Processing your request...":
                # This is likely the message we're looking for, but it doesn't have tool_calls
                # We need to find the original message with tool_calls from the OpenAI response
                # For now, we'll just return an error
                print("DEBUG: Found 'Processing your request...' message without tool_calls")
                
                # As a fallback, we'll try to process a default fetch_cars call
                print("DEBUG: Using fallback mechanism to process fetch_cars with default parameters")
                result = fetch_cars({
                    "make": "Nissan",
                    "model": "",
                    "year": -1,
                    "max_year": -1,
                    "price": -1,
                    "max_price": -1,
                    "mileage": -1,
                    "color": "",
                    "stock_number": "",
                    "vin": ""
                })
                print("DEBUG: Fallback fetch_cars result:", result)
                
                # Add the result as an assistant message
                result_message = {
                    "role": "assistant",
                    "content": f"Here are the car details I found: {json.dumps(result)}"
                }
                conversation_history.append(result_message)
                
                # Get the final response from the LLM
                print("DEBUG: Getting final response from LLM with fallback data")
                completion = client.chat.completions.create(
                    model="o3-mini-2025-01-31",
                    messages=conversation_history
                )
                message = completion.choices[0].message
                final_response = message.content or ""
                print("DEBUG: Final response from LLM with fallback data:", final_response)
                
                # Append the final response to the conversation history
                conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })
                
                return jsonify({
                    "final_response": final_response,
                    "final_conversation_history": conversation_history
                }), 200
            else:
                return jsonify({"error": "No tool call found in conversation history"}), 400

        # Process the tool call
        tool_call = tool_call_message["tool_calls"][0]
        func_name = tool_call["function"]["name"]
        args_str = tool_call["function"]["arguments"]

        try:
            func_args = json.loads(args_str)
            print("DEBUG: Processing tool call. Function:", func_name, "Arguments:", func_args)
        except Exception as parse_error:
            print("DEBUG: Error parsing tool arguments:", parse_error)
            return jsonify({"error": "Error parsing tool arguments"}), 400

        # Execute the appropriate function based on the tool name
        if func_name == "fetch_cars":
            result = fetch_cars(func_args)
            print("DEBUG: fetch_cars result:", result)
            
            # Add the tool response message with the tool_call_id
            tool_response_message = {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(result)
            }
            conversation_history.append(tool_response_message)
        else:
            return jsonify({"error": f"Unknown tool '{func_name}' called"}), 400

        # Get the final response from the LLM
        print("DEBUG: Getting final response from LLM")
        completion = client.chat.completions.create(
            model="o3-mini-2025-01-31",
            messages=conversation_history
        )
        message = completion.choices[0].message
        final_response = message.content or ""
        print("DEBUG: Final response from LLM:", final_response)

        # Append the final response to the conversation history
        conversation_history.append({
            "role": "assistant",
            "content": final_response
        })

        return jsonify({
            "final_response": final_response,
            "final_conversation_history": conversation_history
        }), 200

    except Exception as e:
        print("DEBUG: Exception encountered in tool call result:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@all_routes_bp.route("/generate-summary", methods=["POST"])
def generate_summary():
    try:
        data = request.get_json(force=True)
        print("DEBUG: Received generate summary request JSON:", data)

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Get the conversation history and optional conversation ID
        conversation_history = data.get("conversation_history", [])
        conversation_id = data.get("conversation_id")
        
        if not isinstance(conversation_history, list):
            return jsonify({"error": "Invalid conversation history format"}), 400

        print("DEBUG: Generating summary for conversation history length:", len(conversation_history))
        
        # Generate the summary
        summary = generate_conversation_summary(conversation_history, conversation_id)
        
        return jsonify({
            "summary": summary
        }), 200

    except Exception as e:
        print("DEBUG: Exception encountered in generate summary:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@all_routes_bp.route("/get-summary/<conversation_id>", methods=["GET"])
def get_summary(conversation_id):
    try:
        print(f"DEBUG: Retrieving summary for conversation ID: {conversation_id}")
        
        # Get the summary from the database
        summary = get_conversation_summary(conversation_id)
        
        if summary:
            return jsonify({
                "summary": summary
            }), 200
        else:
            return jsonify({"error": "Summary not found"}), 404

    except Exception as e:
        print("DEBUG: Exception encountered in get summary:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
