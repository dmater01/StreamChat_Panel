import os
import openai
import panel as pn
from collections import deque
from dotenv import load_dotenv

# --- New LangChain Imports ---
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool

# --- Step 1: Configuration and Setup ---
load_dotenv()
pn.extension('tabulator', 'material')

openai.api_key = os.getenv("OPENAI_API_KEY")
serper_api_key = os.getenv("SERPAPI_API_KEY")

if not openai.api_key or not serper_api_key:
    raise ValueError(
        "API keys not found. Please set OPENAI_API_KEY and SERPER_API_KEY in your .env file."
    )

# **New: Initialize the LangChain Agent Components**
chat_history = deque(maxlen=10)

llm = ChatOpenAI(model="gpt-4", temperature=0)

search_wrapper = SerpAPIWrapper(serpapi_api_key=serper_api_key)

search_tool = Tool(
    name="google_search",
    description="Search Google for current information and facts",
    func=search_wrapper.run
)

tools = [search_tool]

# **FIXED: Removed {tools} variable from prompt template**
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a powerful research assistant with access to web search capabilities. Use the available tools to find current information and provide comprehensive, accurate responses."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# **Initialize the agent with `create_openai_tools_agent`**
agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt_template)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
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
    callback_exception='verbose',
)

chat_interface.send(
    "Hello! I am a research assistant. Ask me anything that requires external knowledge!",
    user="System", respond=False
)

template = pn.template.MaterialTemplate(
    title="Research Assistant",
    sidebar_width=300,
    sidebar=[
        pn.pane.Markdown("## About"),
        pn.pane.Markdown("This chatbot uses a LangChain agent with a Google Search tool for real-time information retrieval."),
        pn.pane.Markdown("## Features"),
        pn.pane.Markdown("• **Web Search**: Access current information from Google\n• **GPT-4**: Powered by OpenAI's latest model\n• **Memory**: Maintains conversation context"),
        pn.pane.Markdown("## Settings"),
        model_selector,
        clear_button,
    ],
    main=[
        chat_interface,
    ],
)

template.servable()
