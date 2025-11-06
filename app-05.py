import os
import openai
import panel as pn
from collections import deque
from dotenv import load_dotenv  # Import the function

# Load environment variables from the .env file
load_dotenv()

pn.extension()

# Securely load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is set
if not openai.api_key:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    )

# The rest of the code remains the same
model_selector = pn.widgets.Select(
    name="Model",
    options=["gpt-3.5-turbo", "gpt-4"],
    value="gpt-3.5-turbo",
)

chat_history = deque(maxlen=10)

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    chat_history.append({"role": "user", "content": contents})
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

        message = ""
        for chunk in response:
            content = chunk["choices"][0]["delta"].get("content", "")
            message += content
            yield message

        chat_history.append({"role": "assistant", "content": message})

    except openai.error.OpenAIError as e:
        yield f"**Error:** An OpenAI API error occurred. Details: {e}"
    except Exception as e:
        yield f"**Error:** An unexpected error occurred. Details: {e}"

def clear_chat_history(event):
    chat_history.clear()
    chat_interface.clear()
    chat_interface.send(
        "Chat history has been cleared.", user="System", respond=False
    )

clear_button = pn.widgets.Button(name="Clear History", button_type="danger")
clear_button.on_click(clear_chat_history)

chat_interface = pn.chat.ChatInterface(
    callback=callback,
    callback_user="ChatGPT",
    widgets=[model_selector, clear_button],
)

chat_interface.send(
    "Hello! I am a helpful AI. Let's chat!", user="System", respond=False
)

chat_interface.servable()
