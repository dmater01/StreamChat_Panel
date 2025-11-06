import os
import openai
import panel as pn
from collections import deque
from dotenv import load_dotenv

# --- Step 1: Configuration and Setup ---
# Load environment variables from a .env file
load_dotenv()
pn.extension()

# Securely load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Stop the app if the API key is not set
if not openai.api_key:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    )

# --- Step 2: Define Components and State ---
# Global state for conversational history, with a fixed size
chat_history = deque(maxlen=10)

# Panel widgets for user control
model_selector = pn.widgets.Select(
    name="Model",
    options=["gpt-3.5-turbo", "gpt-4"],
    value="gpt-3.5-turbo",
)

clear_button = pn.widgets.Button(name="Clear History", button_type="danger")

# --- Step 3: Define Event Handlers and Callback Logic ---
def clear_chat_history(event):
    """Clears the chat history and sends a system message."""
    chat_history.clear()
    chat_interface.clear()
    chat_interface.send(
        "Chat history has been cleared.", user="System", respond=False
    )

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    """
    Handles user input, calls the OpenAI API, and streams the response.
    Includes conversational memory and error handling.
    """
    # Append the user's new message to the history
    chat_history.append({"role": "user", "content": contents})

    # Build the full message list for the API call
    messages = [
        {"role": "system", "content": "You are a helpful and friendly assistant."}
    ]
    messages.extend(list(chat_history))

    try:
        response = openai.ChatCompletion.create(
            model=model_selector.value,
            messages=messages,
            stream=True,
        )
        
        # Stream the response to the UI
        message = ""
        for chunk in response:
            content = chunk["choices"][0]["delta"].get("content", "")
            message += content
            yield message

        # Save the complete assistant response to the history
        chat_history.append({"role": "assistant", "content": message})

    except openai.error.OpenAIError as e:
        yield f"**Error:** An OpenAI API error occurred. Details: {e}"
    except Exception as e:
        yield f"**Error:** An unexpected error occurred. Details: {e}"


# --- Step 4: Assemble the Application ---
# Link the clear button to its event handler
clear_button.on_click(clear_chat_history)

# Create the main chat interface, passing the widgets and callback
chat_interface = pn.chat.ChatInterface(
    callback=callback,
    callback_user="ChatGPT",
    widgets=[model_selector, clear_button],
)

# Send an initial system message
chat_interface.send(
    "Hello! I am a helpful AI. Let's chat!", user="System", respond=False
)

# Make the application servable
chat_interface.servable()
