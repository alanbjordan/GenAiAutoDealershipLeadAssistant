import os
import json
from openai import OpenAI
from datetime import datetime
import pytz
from helpers.llm_utils import (
    fetch_cars, 
    generate_conversation_summary, 
    get_conversation_summary, 
    detect_end_of_conversation, 
    find_car_review_videos
)

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the tools for the OpenAI API
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
                        "description": "Maximum mileage. Use -1 to indicate no maximum."
                    },
                    "color": {
                        "type": "string",
                        "description": "Car color. Use empty string to indicate no color filter."
                    },
                    "stock_number": {
                        "type": "string",
                        "description": "Exact stock number. Use empty string to indicate no stock number filter."
                    },
                    "vin": {
                        "type": "string",
                        "description": "Exact VIN. Use empty string to indicate no VIN filter."
                    }
                },
                "required": ["make", "model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_car_review_videos",
            "description": "Search for car review videos on YouTube based on make, model, and optionally year.",
            "parameters": {
                "type": "object",
                "properties": {
                    "car_make": {
                        "type": "string",
                        "description": "The make of the car (e.g., Toyota, Ford)"
                    },
                    "car_model": {
                        "type": "string",
                        "description": "The model of the car (e.g., Camry, Mustang)"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Optional year of the car model"
                    }
                },
                "required": ["car_make", "car_model"]
            }
        }
    }
]

def get_system_message():
    """Return the system message for the chat."""
    return {
        "role": "system",
        "content": (
            """ 
            You are Patricia, a knowledgeable and friendly customer support agent at Nissan of Hendersonville, a family-owned and operated Nissan dealership in Hendersonville, North Carolina.
            IF YOU GET A MESSAGE IN A NON ENGLISH LANGUAGE RESPONSE IN THE LANAGUAGE THE USER IS SPEAKING
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

            If a customer shows interest in a specific car or asks to see reviews or videos about a car, use the find_car_review_videos function to provide a list of car review videos on YouTube. This function requires the car_make and car_model parameters, and optionally accepts a year parameter.
            
            Remember that you are representing a family-owned business that prides itself on customer service and helping customers find the perfect car. Be helpful, friendly, and professional in all interactions.
            
            NEVER schedule appointments for days when the dealership is closed (like Sundays).
            NEVER provide information about test drives without verifying the customer's contact information first.
            NEVER make up information about the dealership or its staff.
            
            IMPORTANT - Appointment Scheduling Requirements:
            Only address the customer by their first name. No gender specific pronouns.
            Before scheduling any appointment (test drive, service, etc.), you MUST collect and verify:
            1. Customer's full name (first and last name)
            2. Phone number (must be a valid format)
            3. Email address (must be a valid format)
            
            If any of these three pieces of information is missing or invalid:
            1. Politely ask for the missing information
            2. Do not proceed with scheduling until all information is provided
            3. Explain that this information is required for appointment scheduling
            4. If the customer refuses to provide any of this information, explain that you cannot schedule the appointment without it
            
            IMPORTANT - Time Awareness:
            You will receive a message with the current time in EST. Use this information to:
            1. Determine if the dealership is currently open or closed
            2. Avoid scheduling appointments outside of business hours
            3. Provide accurate information about when the dealership will be open next
            4. Consider the day of the week when discussing availability
            5. Dont mention the service hours or business hours unless asked or the customer asks about booking an appointment or test drive.
            
            IMPORTANT - End of Conversation:
            When you detect that the conversation is coming to an end (e.g., the customer says goodbye, thanks you, or indicates they have no more questions), 
            you should explicitly signal the end of the conversation with a clear closing message such as:
            "Thank you for chatting with me today. I'm glad I could help you with your questions about Nissan vehicles. Have a great day!"
            
            This helps our system know when to generate a summary of the conversation.
            """
        )
    }

def get_time_context_message():
    """Get the current time in EST and return a time context message."""
    try:
        # Get current time in EST using a reliable method
        est = pytz.timezone('US/Eastern')
        current_time = datetime.now(est)
        current_time_formatted = current_time.strftime('%Y-%m-%d %H:%M:%S EST')
    except Exception as e:
        # Fallback to a simpler approach
        from datetime import datetime, timedelta
        # EST is UTC-5
        utc_now = datetime.utcnow()
        est_offset = timedelta(hours=-5)
        est_time = utc_now + est_offset
        current_time_formatted = est_time.strftime('%Y-%m-%d %H:%M:%S EST')
    
    return {
        "role": "system",
        "content": f"Current time: {current_time_formatted}"
    }

def process_chat(user_message, conversation_history):
    """Process a chat message and return the response."""
    if not user_message:
        return {"error": "No 'message' provided"}, 400
    
    # Ensure conversation_history is a list
    if not isinstance(conversation_history, list):
        conversation_history = []
    
    # Check if the conversation history already has a system message
    has_system_message = any(msg.get("role") == "system" and "You are Patricia" in msg.get("content", "") for msg in conversation_history)
    
    # If no conversation history or no system message, add the system message
    if not conversation_history or not has_system_message:
        # Insert the system message at the beginning of the conversation history
        conversation_history.insert(0, get_system_message())
    
    # Check if there's a time context message in the conversation history
    has_time_context = any(msg.get("role") == "system" and "Current time:" in msg.get("content", "") for msg in conversation_history)
    
    # If no time context message, add one
    if not has_time_context:
        # Add time context message
        conversation_history.append(get_time_context_message())
    
    # Call ChatCompletion API using the new tools syntax
    completion = client.chat.completions.create(
        model="o3-mini-2025-01-31",
        messages=conversation_history,
        tools=tools
    )
    
    message = completion.choices[0].message
    
    # Check if a tool call was triggered
    tool_call_detected = False
    if message.tool_calls and len(message.tool_calls) > 0:
        tool_call_detected = True
        tool_call = message.tool_calls[0]
        func_name = tool_call.function.name
        args_str = tool_call.function.arguments
        
        try:
            func_args = json.loads(args_str)
        except Exception as parse_error:
            assistant_response = "Error parsing tool arguments."
        else:
            # For tool calls, we'll just return a placeholder response
            # The actual tool call processing will happen in the tool-call-result endpoint
            assistant_response = "Processing your request..."
    else:
        assistant_response = message.content or ""
    
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
    
    # Check if the conversation has ended and generate a summary if needed
    summary = None
    if detect_end_of_conversation(conversation_history):
        # Generate a conversation ID if not already present
        conversation_id = None
        for msg in conversation_history:
            if msg.get("role") == "system" and "conversation_id" in msg.get("content", ""):
                try:
                    conversation_id = json.loads(msg.get("content")).get("conversation_id")
                    break
                except:
                    pass
        
        # Generate the summary
        summary = generate_conversation_summary(conversation_history, conversation_id)
    
    return {
        "chat_response": assistant_response,
        "conversation_history": conversation_history,
        "tool_call_detected": tool_call_detected,
        "summary": summary
    }, 200

def process_tool_call(conversation_history):
    """Process a tool call and return the final response."""
    if not isinstance(conversation_history, list):
        return {"error": "Invalid conversation history format"}, 400
    
    # Find the assistant message with tool calls
    tool_call_message = None
    for msg in reversed(conversation_history):
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            tool_call_message = msg
            break
    
    if not tool_call_message:
        return {"error": "No assistant message found in conversation history"}, 400
        
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
            
            # Check if the message contains a reference to car reviews
            review_keywords = ["review", "reviews", "video", "videos", "watch", "see", "look at"]
            message_content = tool_call_message.get("content", "").lower()
            
            if any(keyword in message_content for keyword in review_keywords):
                print("DEBUG: Detected car review request in fallback mechanism")
                result = find_car_review_videos("Nissan", "Kicks", 2025)
                print("DEBUG: Fallback find_car_review_videos result:", result)
                
                # Add the result as a tool response message
                tool_response_message = {
                    "role": "tool",
                    "tool_call_id": "fallback_tool_call",
                    "content": json.dumps(result)
                }
                conversation_history.append(tool_response_message)
                
                # If there's an error in the result, log it
                if "error" in result:
                    print("DEBUG: Error in fallback find_car_review_videos result:", result["error"])
            else:
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
                
                # Add the result as a tool response message
                tool_response_message = {
                    "role": "tool",
                    "tool_call_id": "fallback_tool_call",
                    "content": json.dumps(result)
                }
                conversation_history.append(tool_response_message)
            
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
            
            # Check if the conversation has ended and generate a summary if needed
            summary = None
            if detect_end_of_conversation(conversation_history):
                print("DEBUG: End of conversation detected, generating summary")
                # Generate a conversation ID if not already present
                conversation_id = None
                for msg in conversation_history:
                    if msg.get("role") == "system" and "conversation_id" in msg.get("content", ""):
                        try:
                            conversation_id = json.loads(msg.get("content")).get("conversation_id")
                            break
                        except:
                            pass
                
                # Generate the summary
                summary = generate_conversation_summary(conversation_history, conversation_id)
                print("DEBUG: Summary generated:", summary)
            
            return {
                "final_response": final_response,
                "final_conversation_history": conversation_history,
                "summary": summary
            }, 200
        else:
            return {"error": "No tool call found in conversation history"}, 400

    # Process each tool call
    for tool_call in tool_call_message["tool_calls"]:
        func_name = tool_call["function"]["name"]
        args_str = tool_call["function"]["arguments"]
        tool_call_id = tool_call["id"]

        try:
            func_args = json.loads(args_str)
        except Exception as parse_error:
            return {"error": "Error parsing tool arguments"}, 400

        # Execute the appropriate function based on the tool name
        if func_name == "fetch_cars":
            result = fetch_cars(func_args)
        elif func_name == "find_car_review_videos":
            result = find_car_review_videos(func_args.get("car_make"), func_args.get("car_model"), func_args.get("year"))
            # If there's an error in the result, include it in the tool response
            if "error" in result:
                print("DEBUG: Error in find_car_review_videos result:", result["error"])
        else:
            return {"error": f"Unknown tool '{func_name}' called"}, 400

        # Add the tool response message with the tool_call_id
        tool_response_message = {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(result)
        }
        conversation_history.append(tool_response_message)

    # Get the final response from the LLM
    completion = client.chat.completions.create(
        model="o3-mini-2025-01-31",
        messages=conversation_history
    )
    message = completion.choices[0].message
    final_response = message.content or ""

    # Append the final response to the conversation history
    conversation_history.append({
        "role": "assistant",
        "content": final_response
    })
    
    # Check if the conversation has ended and generate a summary if needed
    summary = None
    if detect_end_of_conversation(conversation_history):
        # Generate a conversation ID if not already present
        conversation_id = None
        for msg in conversation_history:
            if msg.get("role") == "system" and "conversation_id" in msg.get("content", ""):
                try:
                    conversation_id = json.loads(msg.get("content")).get("conversation_id")
                    break
                except:
                    pass
        
        # Generate the summary
        summary = generate_conversation_summary(conversation_history, conversation_id)

    return {
        "final_response": final_response,
        "final_conversation_history": conversation_history,
        "summary": summary
    }, 200

def generate_summary(conversation_history, conversation_id=None):
    """Generate a summary for a conversation."""
    if not isinstance(conversation_history, list):
        return {"error": "Invalid conversation history format"}, 400
    
    # Generate the summary
    summary = generate_conversation_summary(conversation_history, conversation_id)
    
    return {
        "summary": summary
    }, 200

def get_summary(conversation_id):
    """Get a summary for a conversation by ID."""
    # Get the summary from the database
    summary = get_conversation_summary(conversation_id)
    
    if summary:
        return {
            "summary": summary
        }, 200
    else:
        return {"error": "Summary not found"}, 404 