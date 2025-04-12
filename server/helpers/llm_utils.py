# helpers/llm_utils.py
import os
from openai import OpenAI
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Your pre-created Assistant ID from when you set up your assistant.
assistant_id = "asst_JnQbdG73Isn5z5CfON1mWyo2"

if not client.api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

def generate_llm_natural_output(user_message: str, thread_id: str = None) -> dict:
    """
    Generate a conversational response by:
      1. Continuing an existing thread if thread_id is provided, or creating a new thread otherwise.
      2. Adding the user's message to the thread.
      3. Creating a Run on the thread and polling until it reaches a terminal status.
      4. Retrieving and returning the assistant's final message.

    Returns a dictionary with "chat_response" and "thread_id".
    """
    # 1) If no thread_id is provided, create a new thread.
    if not thread_id:
        thread = client.beta.threads.create()
        thread_id = thread.id
        print(f"[LOG] Created new thread. Thread ID: {thread_id}")
    else:
        # No need to retrieve the thread if the API accepts thread_id directly.
        # If necessary, you could add retrieval logic here to validate the thread.
        pass

    # 2) Append the user's message to the thread.
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    # 3) Create a new run on the thread.
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    print(f"[LOG] Created run. Run ID: {run.id}, initial status: {run.status}")

    # 4) Poll until the run reaches a terminal status.
    while True:
        updated_run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if updated_run.status in ["completed", "failed", "incomplete"]:
            break
        time.sleep(1)
    print(f"[LOG] Polled run => final status: {updated_run.status}")

    # 5) Retrieve messages from the thread and return the assistant's response.
    if updated_run.status == "completed":
        messages_response = client.beta.threads.messages.list(thread_id=thread_id)
        # Adjust attribute access as needed (assuming a "data" list is available).
        assistant_msgs = [msg for msg in messages_response.data if msg.role == "assistant"]
        if assistant_msgs:
            final_text = assistant_msgs[0].content[0].text.value
            final_text = str(final_text)
            print(f"[LOG] Final assistant message: {final_text}")
            return {
                "chat_response": final_text,
                "thread_id": thread_id
            }
        else:
            return {
                "chat_response": "No assistant response found.",
                "thread_id": thread_id
            }
    else:
        return {
            "chat_response": f"Run did not complete. Status: {updated_run.status}",
            "thread_id": thread_id
        }
