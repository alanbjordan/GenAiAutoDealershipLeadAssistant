from database import db
from models.sql_models import CarInventory, ConversationSummary
import json
import uuid

def fetch_cars(filter_params: dict) -> list:
    """
    Query the CarInventory table based on provided filter criteria.
    
    If the user does not provide a parameter or provides -1 for numeric fields,
    the function will skip applying that filter.
    
    :param filter_params: A dictionary with keys such as:
        {
            "make": <str>,         # Car manufacturer (non-empty string to filter)
            "model": <str>,        # Car model (non-empty string to filter)
            "year": <int>,         # Minimum car model year (-1 means no filtering)
            "max_year": <int>,     # Maximum car model year (-1 means no filtering)
            "price": <float>,      # Minimum price (-1 means no filtering)
            "max_price": <float>,  # Maximum price (-1 means no filtering)
            "mileage": <int>,      # Maximum mileage (-1 means no filtering)
            "color": <str>,        # Car color (non-empty string to filter)
            "stock_number": <str>, # Exact stock number (non-empty string to filter)
            "vin": <str>           # Exact vehicle identification number (non-empty string to filter)
        }
    :return: A list of dictionaries, each representing a car in the inventory.
    """
    query = db.session.query(CarInventory)
    
    # Check string filters only if they are non-empty
    if "make" in filter_params and filter_params["make"]:
        query = query.filter(CarInventory.make.ilike(f"%{filter_params['make']}%"))
    if "model" in filter_params and filter_params["model"]:
        query = query.filter(CarInventory.model.ilike(f"%{filter_params['model']}%"))
    if "color" in filter_params and filter_params["color"]:
        query = query.filter(CarInventory.color.ilike(f"%{filter_params['color']}%"))
    if "stock_number" in filter_params and filter_params["stock_number"]:
        query = query.filter(CarInventory.stock_number == filter_params["stock_number"])
    if "vin" in filter_params and filter_params["vin"]:
        query = query.filter(CarInventory.vin == filter_params["vin"])
    
    # Check numeric filters only if they are provided and not equal to -1
    if "year" in filter_params and filter_params["year"] != -1:
        query = query.filter(CarInventory.year >= filter_params["year"])
    if "max_year" in filter_params and filter_params["max_year"] != -1:
        query = query.filter(CarInventory.year <= filter_params["max_year"])
    if "price" in filter_params and filter_params["price"] != -1:
        query = query.filter(CarInventory.price >= filter_params["price"])
    if "max_price" in filter_params and filter_params["max_price"] != -1:
        query = query.filter(CarInventory.price <= filter_params["max_price"])
    if "mileage" in filter_params and filter_params["mileage"] != -1:
        query = query.filter(CarInventory.mileage <= filter_params["mileage"])
    
    results = query.all()
    
    def to_dict(car: CarInventory) -> dict:
        return {
            "stock_number": car.stock_number,
            "vin": car.vin,
            "make": car.make,
            "model": car.model,
            "year": car.year,
            "price": float(car.price),
            "mileage": car.mileage,
            "color": car.color,
            "description": car.description,
            "created_at": car.created_at.isoformat() if car.created_at else None
        }
    
    return [to_dict(c) for c in results]

def generate_conversation_summary(conversation_history: list, conversation_id: str = None) -> dict:
    """
    Generate a summary of the conversation using OpenAI's API.
    
    :param conversation_history: List of message objects in the conversation
    :param conversation_id: Optional ID for the conversation. If not provided, a new one will be generated.
    :return: Dictionary containing the summary information
    """
    from openai import OpenAI
    import os
    
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Generate a conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    # Prepare the conversation for analysis
    # Filter out system messages and tool messages to focus on the actual conversation
    filtered_history = [
        msg for msg in conversation_history 
        if msg.get("role") in ["user", "assistant"] and 
        not (msg.get("role") == "assistant" and "tool_calls" in msg)
    ]
    
    # Create a prompt for the summary generation
    summary_prompt = {
        "role": "system",
        "content": """
        You are an expert at analyzing car dealership conversations and creating concise, informative summaries.
        
        Analyze the provided conversation and create a summary with the following components:
        
        1. Overall sentiment analysis (positive, neutral, or negative)
        2. Key tags/keywords extracted from the conversation (e.g., 'new model', 'financing', 'trade-in', 'service appointment')
        3. A concise summary of the main discussion points and any relevant customer information
        4. A follow-up routing recommendation (Sales, Service, Management, HR, Finance, or Parts)
        5. Additional insights such as urgency or potential upsell opportunities
        
        Format your response as a JSON object with the following structure:
        {
            "sentiment": "positive/neutral/negative",
            "keywords": ["keyword1", "keyword2", ...],
            "summary": "Concise summary text",
            "department": "Sales/Service/Management/HR/Finance/Parts",
            "insights": {
                "urgency": "high/medium/low",
                "upsell_opportunity": true/false,
                "customer_interest": "high/medium/low",
                "additional_notes": "Any other relevant information"
            }
        }
        
        Be thorough but concise in your analysis.
        """
    }
    
    # Combine the prompt with the conversation history
    messages_for_analysis = [summary_prompt] + filtered_history
    
    # Call the OpenAI API to generate the summary
    try:
        response = client.chat.completions.create(
            model="o3-mini-2025-01-31",
            messages=messages_for_analysis,
            response_format={"type": "json_object"}
        )
        
        # Extract the summary from the response
        summary_json = json.loads(response.choices[0].message.content)
        
        # Add the conversation ID to the summary
        summary_json["conversation_id"] = conversation_id
        
        # Save the summary to the database
        save_summary_to_db(summary_json)
        
        return summary_json
    
    except Exception as e:
        print(f"Error generating conversation summary: {e}")
        # Return a default summary in case of error
        return {
            "conversation_id": conversation_id,
            "sentiment": "neutral",
            "keywords": ["error"],
            "summary": "Error generating summary. Please try again.",
            "department": "Sales",
            "insights": {
                "urgency": "low",
                "upsell_opportunity": False,
                "customer_interest": "unknown",
                "additional_notes": f"Error: {str(e)}"
            }
        }

def save_summary_to_db(summary_data: dict) -> bool:
    """
    Save the conversation summary to the database.
    
    :param summary_data: Dictionary containing the summary information
    :return: True if successful, False otherwise
    """
    try:
        # Check if a summary with this conversation ID already exists
        existing_summary = db.session.query(ConversationSummary).filter_by(
            conversation_id=summary_data["conversation_id"]
        ).first()
        
        if existing_summary:
            # Update the existing summary
            existing_summary.sentiment = summary_data["sentiment"]
            existing_summary.keywords = summary_data["keywords"]
            existing_summary.summary = summary_data["summary"]
            existing_summary.department = summary_data["department"]
            existing_summary.insights = summary_data["insights"]
        else:
            # Create a new summary
            new_summary = ConversationSummary(
                conversation_id=summary_data["conversation_id"],
                sentiment=summary_data["sentiment"],
                keywords=summary_data["keywords"],
                summary=summary_data["summary"],
                department=summary_data["department"],
                insights=summary_data["insights"]
            )
            db.session.add(new_summary)
        
        # Commit the changes
        db.session.commit()
        return True
    
    except Exception as e:
        print(f"Error saving summary to database: {e}")
        db.session.rollback()
        return False

def get_conversation_summary(conversation_id: str) -> dict:
    """
    Retrieve a conversation summary from the database.
    
    :param conversation_id: ID of the conversation
    :return: Dictionary containing the summary information or None if not found
    """
    try:
        summary = db.session.query(ConversationSummary).filter_by(
            conversation_id=conversation_id
        ).first()
        
        if summary:
            return {
                "conversation_id": summary.conversation_id,
                "sentiment": summary.sentiment,
                "keywords": summary.keywords,
                "summary": summary.summary,
                "department": summary.department,
                "insights": summary.insights,
                "created_at": summary.created_at.isoformat() if summary.created_at else None,
                "updated_at": summary.updated_at.isoformat() if summary.updated_at else None
            }
        else:
            return None
    
    except Exception as e:
        print(f"Error retrieving summary from database: {e}")
        return None

def detect_end_of_conversation(conversation_history: list) -> bool:
    """
    Analyze the conversation history to detect if the conversation has ended.
    
    This function looks for explicit end-of-conversation signals in the most recent messages.
    
    :param conversation_history: List of message objects in the conversation
    :return: True if the conversation appears to have ended, False otherwise
    """
    # We need at least a few messages to determine if the conversation has ended
    if len(conversation_history) < 3:
        return False
    
    # Get the last few messages (up to 5) to analyze
    recent_messages = conversation_history[-5:]
    
    # Look for end-of-conversation signals in the assistant's messages
    for msg in reversed(recent_messages):
        if msg.get("role") == "assistant":
            content = msg.get("content", "").lower()
            
            # Check for explicit end-of-conversation phrases
            end_phrases = [
                "goodbye", "bye", "thank you for chatting", "have a great day",
                "is there anything else", "anything else i can help", "end of conversation",
                "conversation is complete", "conversation has ended", "wrapping up",
                "summarizing our conversation", "conversation summary"
            ]
            
            # Check if any of the end phrases are in the message
            if any(phrase in content for phrase in end_phrases):
                return True
    
    return False
