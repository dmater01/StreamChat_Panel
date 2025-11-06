import os
import openai
import panel as pn
from collections import deque
from dotenv import load_dotenv

# --- Step 1: Configuration and Setup ---
load_dotenv()
pn.extension('fast', 'bootstrap') # Use the 'fast' and 'bootstrap' extensions for a better layout

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    )

client = openai.OpenAI(api_key=openai.api_key)

# --- Step 2: Define Components and State ---
chat_history = deque(maxlen=10)

model_selector = pn.widgets.Select(
    name="Model",
    options=["gpt-3.5-turbo", "gpt-4"],
    value="gpt-3.5-turbo",
)

clear_button = pn.widgets.Button(name="Clear History", button_type="danger")

# --- Step 3: Define Event Handlers and Callback Logic ---
def clear_chat_history(event):
    chat_history.clear()
    chat_interface.clear()
    chat_interface.send(
        "Chat history has been cleared.", user="System", respond=False
    )

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    print(f"User input received: {contents}")
    chat_history.append({"role": "user", "content": contents})

    messages = [
        {"role": "system", "content": "You are a helpful and friendly assistant."}
    ]
    messages.extend(list(chat_history))

    try:
        response = client.chat.completions.create(
            model=model_selector.value,
            messages=messages,
            stream=True,
        )
        
        message = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content is not None:
                message += content
                yield message

        chat_history.append({"role": "assistant", "content": message})

    except openai.APIError as e:
        yield f"**Error:** An OpenAI API error occurred. Details: {e}"
    except Exception as e:
        yield f"**Error:** An unexpected error occurred. Details: {e}"

# --- Step 4: Assemble the Application ---
clear_button.on_click(clear_chat_history)

# **Refactored Layout:**
# The chat interface no longer takes widgets in its constructor
chat_interface = pn.chat.ChatInterface(
    callback=callback,
    callback_user="ChatGPT",
    callback_exception='verbose',
)

# Send an initial system message
chat_interface.send(
    "Hello! I am a helpful AI. Let's chat!", user="System", respond=False
)

# Use a template to create a clean layout with a sidebar
template = pn.template.FastListTemplate(
    site="Panel Chatbot",
    title="OpenAI Chatbot",
    sidebar=[
        model_selector,
        clear_button,
    ],
    main=[
        chat_interface,
    ],
)

# Make the template servable
template.servable()
