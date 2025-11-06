# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StreamChat_Panel is a Panel-based web application that implements an AI research assistant chatbot with web search capabilities. The application uses LangChain agents powered by OpenAI's GPT-4 and integrates SerpAPI for real-time Google search functionality.

## Core Architecture

### Main Application Stack
- **UI Framework**: Panel (Holoviz) - Python web application framework
- **LLM Integration**: LangChain with OpenAI GPT-4
- **Agent Pattern**: LangChain AgentExecutor with tools
- **Search Integration**: SerpAPI via LangChain's SerpAPIWrapper
- **Async Support**: Application uses async/await for chat callbacks

### Key Components

**Agent Configuration** (`app.py`):
- Uses `create_openai_tools_agent` (preferred over deprecated `create_react_agent`)
- `ChatPromptTemplate` with MessagesPlaceholder for chat history and agent scratchpad
- `ConversationBufferMemory` maintains conversation context
- `AgentExecutor` orchestrates LLM + tools with verbose logging

**Memory Management**:
- Dual memory system: `deque(maxlen=10)` for UI chat history + LangChain's ConversationBufferMemory
- Both memories cleared together via clear_button handler

**UI Structure**:
- MaterialTemplate with sidebar (settings, info) and main panel (chat interface)
- ChatInterface with async callback for streaming responses
- Model selector widget (currently GPT-4 only)
- Clear history button for resetting conversation

### File Organization

- `app.py` - Current production version (uses `create_openai_tools_agent`)
- `app-nohis.py` - Earlier version without chat history in prompt
- `app-01.py` through `app-06.py` - Development iterations showing evolution
- `.env` - API keys (OPENAI_API_KEY, SERPAPI_API_KEY required)
- `venv/` - Python virtual environment

## Development Commands

### Running the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run with Panel server
panel serve app.py --show --autoreload

# Alternative: specific port
panel serve app.py --port 5006 --show
```

### Dependencies
```bash
# Install from environment
pip install panel langchain langchain-openai langchain-community openai python-dotenv

# Key versions (from current environment):
# - Python 3.11.13
# - panel 1.7.5
# - langchain 0.3.27
# - langchain-openai 0.3.28
# - openai 1.98.0
```

### Testing
No formal test suite currently exists. Manual testing via the web UI.

## Environment Configuration

Required environment variables in `.env`:
- `OPENAI_API_KEY` - OpenAI API access for GPT-4
- `SERPAPI_API_KEY` - SerpAPI key for Google search tool

Other API keys present but unused: ANTHROPIC_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY

## Important Implementation Notes

### Agent Pattern Evolution
The codebase shows progression from older to newer LangChain patterns:
- Older files use `create_react_agent` with `PromptTemplate`
- Current `app.py` uses `create_openai_tools_agent` with `ChatPromptTemplate` and `MessagesPlaceholder`
- When modifying agent code, use the OpenAI tools pattern, not ReAct

### Tool Definition
Use the SerpAPIWrapper with custom Tool definition:
```python
search_wrapper = SerpAPIWrapper(serpapi_api_key=serper_api_key)
search_tool = Tool(
    name="google_search",
    description="Search Google for current information and facts",
    func=search_wrapper.run
)
```

### Prompt Template Structure
The ChatPromptTemplate must include three placeholders:
1. `MessagesPlaceholder(variable_name="chat_history")` - Conversation context
2. `("human", "{input}")` - User input
3. `MessagesPlaceholder(variable_name="agent_scratchpad")` - Agent reasoning

Do NOT include `{tools}` in the prompt template when using `create_openai_tools_agent`.

### Async Callback Pattern
The chat callback must:
- Be async with signature: `async def callback(contents: str, user: str, instance: pn.chat.ChatInterface)`
- Use `await agent_executor.ainvoke({"input": contents})`
- Yield responses for streaming display
- Handle exceptions gracefully with formatted error messages

## Common Debugging

If agent execution fails:
- Check `.env` file has both required API keys
- Verify SerpAPI has remaining quota
- Check `verbose=True` in AgentExecutor for agent reasoning logs
- Ensure prompt template matches agent type (OpenAI tools vs ReAct)
