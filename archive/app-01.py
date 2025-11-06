import os
import openai
import panel as pn
from collections import deque
from dotenv import load_dotenv

# --- New LangChain Imports ---
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
# **CORRECTED IMPORT STATEMENT - NO SPACES**
from langchain_community.tools.google_search.tool import GoogleSearchRun
from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory

# --- Step 1: Configuration and Setup ---
load_dotenv()
pn.extension('fast', 'bootstrap')

openai.api_key = os.getenv("OPENAI_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

if not openai.api_key or not serper_api_key:
    raise ValueError(
        "API keys not found. Please set OPENAI_API_KEY and SERPER_API_KEY in your .env file."
    )

# **New: Initialize the LangChain Agent Components**
chat_history = deque(maxlen=10)

llm = ChatOpenAI(model="gpt-4", temperature=0)

# **CORRECTED TOOL DEFINITION**
tools = [
    GoogleSearchRun(),
]

prompt_template = PromptTemplate.from_template(
    """You are a powerful research assistant. You have access to the following tools:

    {tools}

    Use the tools to answer questions, perform research, and provide factual information.
    You should always try to use a tool if the question is about current events or requires external knowledge.
    
    You have access to the following conversational memory:
    {chat_history}
    
    Begin!
    {input}
    {agent_scratchpad}
    """
)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt_template)
memory = ConversationBufferMemory(memory_key="chat_history")
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)

# --- Step 2: Define UI Components ---
model_selector = pn.widgets.Select(
    name="Model",
    options=["gpt-4"],
    value="gpt-4"
)

clear_button = pn.widgets.Button(name="Clear History", button_type="danger")

# --- Step 3: Define Event Handlers and Callback Logic ---
def clear_chat_history(event):
    chat_history.clear()
    memory.clear()
    chat_interface.clear()
    chat_interface.send(
        "Chat history has been cleared. I'm ready for new research!", user="System", respond=False
    )

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    print(f"User input received: {contents}")
    chat_history.append({"role": "user", "content": contents})

    try:
        response_dict = await agent_executor.ainvoke({"input": contents})
        
        message = response_dict.get("output", "I could not find a response.")
        
        chat_history.append({"role": "assistant", "content": message})
        yield message

    except Exception as e:
        yield f"**Error:** An unexpected error occurred. Details: {e}"

# --- Step 4: Assemble the Application ---
clear_button.on_click(clear_chat_history)

chat_interface = pn.chat.ChatInterface(
    callback=callback,
    callback_user="ChatGPT",
    widgets=[model_selector, clear_button],
    callback_exception='verbose',
)

chat_interface.send(
    "Hello! I am a research assistant. Ask me anything that requires external knowledge!",
    user="System", respond=False
)

template = pn.template.FastListTemplate(
    site="Panel Chatbot",
    title="Research Assistant",
    sidebar=[
        pn.pane.Markdown("# Settings"),
        pn.pane.Markdown("This chatbot uses a LangChain agent with a Google Search tool."),
        model_selector,
        clear_button,
    ],
    main=[
        chat_interface,
    ],
)

template.servable()
