import os
import openai
import panel as pn
from collections import deque

pn.extension()

# 1. Securely load API key from environment variable
# This is a best practice for security.
openai.api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is set
if not openai.api_key:
    # Use a clear error message to inform the user
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    )

# 2. Add widgets for a more flexible user experience
# We'll add a model selector and a button to clear the chat history.
model_selector = pn.widgets.Select(
    name="Model",
    options=["gpt-3.5-turbo", "gpt-4"],
    value="gpt-3.5-turbo",
)

# 3. Use a deque for efficient conversational memory management
# We'll store a list of messages to maintain conversational context.
# We'll limit the history to a reasonable number to avoid exceeding the token limit.
chat_history = deque(maxlen=10)

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    """
    This enhanced callback function includes conversational memory and robust error handling.
    """
    # Append the user's new message to the chat history
    chat_history.append({"role": "user", "content": contents})

    # Prepare the message list for the API call.
    # We add a "system" prompt to define the chatbot's persona.
    messages = [
        {"role": "system", "content": "You are a helpful and friendly assistant."}
    ]
    messages.extend(list(chat_history))

    # 4. Implement robust error handling
    try:
        response = openai.ChatCompletion.create(
            model=model_selector.value,
            messages=messages,
            stream=True,
        )

        message = ""
        for chunk in response:
            content = chunk["choices"][0]["delta"].get("content", "")
            message += content
            yield message

        # 5. Update chat history with the assistant's final response
        chat_history.append({"role": "assistant", "content": message})

    except openai.error.OpenAIError as e:
        # Catch specific OpenAI API errors and provide a user-friendly message
        yield f"**Error:** An OpenAI API error occurred. Details: {e}"
    except Exception as e:
        # Catch any other unexpected errors
        yield f"**Error:** An unexpected error occurred. Details: {e}"

# Add a function to clear the chat history
def clear_chat_history(event):
    chat_history.clear()
    chat_interface.clear()
    chat_interface.send(
        "Chat history has been cleared.", user="System", respond=False
    )

clear_button = pn.widgets.Button(name="Clear History", button_type="danger")
clear_button.on_click(clear_chat_history)

# Initialize the chat interface with the enhanced callback and widgets
chat_interface = pn.chat.ChatInterface(
    callback=callback,
    callback_user="ChatGPT",
    widgets=[model_selector, clear_button],
)

# Send an initial system message
chat_interface.send(
    "Hello! I am a helpful AI. Let's chat!", user="System", respond=False
)

chat_interface.servable()
