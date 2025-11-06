# StreamChat Panel - User Guide

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Using the Chat Interface](#using-the-chat-interface)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## Overview

StreamChat Panel is an AI-powered research assistant that combines the capabilities of OpenAI's GPT-4 with real-time web search functionality. The application provides an interactive chat interface where you can ask questions that require current information, research topics, and get comprehensive answers backed by web search results.

### What Makes This Different?

Unlike standard ChatGPT, this application can:
- Access current information from the web via Google Search
- Provide up-to-date facts and data
- Cite sources from real-time search results
- Maintain conversation context across multiple messages

## Features

- **Real-time Web Search**: Integrates Google Search through SerpAPI to fetch current information
- **GPT-4 Powered**: Leverages OpenAI's GPT-4 for intelligent responses
- **Conversation Memory**: Maintains context across the conversation
- **Interactive UI**: Clean, modern web interface built with Panel
- **Async Processing**: Streaming responses for a smooth user experience
- **Clear History**: Reset the conversation at any time

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- OpenAI API key
- SerpAPI API key

### Step 1: Clone or Download the Repository

```bash
cd /path/to/your/projects
# Navigate to the StreamChat_Panel directory
cd StreamChat_Panel
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install panel langchain langchain-openai langchain-community openai python-dotenv
```

Required packages:
- `panel` - Web application framework
- `langchain` - LLM orchestration framework
- `langchain-openai` - OpenAI integration for LangChain
- `langchain-community` - Community tools including SerpAPI
- `openai` - OpenAI Python client
- `python-dotenv` - Environment variable management

## Configuration

### Step 1: Obtain API Keys

1. **OpenAI API Key**:
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Navigate to API Keys section
   - Create a new API key
   - Note: GPT-4 access requires a paid account

2. **SerpAPI Key**:
   - Sign up at [SerpAPI](https://serpapi.com/)
   - Get your API key from the dashboard
   - Free tier includes 100 searches/month

### Step 2: Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# Create .env file
touch .env
```

Add the following content to `.env`:

```
OPENAI_API_KEY=your-openai-api-key-here
SERPAPI_API_KEY=your-serpapi-key-here
```

**Important**:
- Replace `your-openai-api-key-here` and `your-serpapi-key-here` with your actual API keys
- Never commit the `.env` file to version control
- The `.gitignore` file already excludes `.env` from git

### Example `.env` Structure

```
OPENAI_API_KEY=sk-proj-AbCdEf123456789...
SERPAPI_API_KEY=e85dab1f7bd069b2522a70e8eb8cc7cf...
```

## Running the Application

### Basic Usage

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run the application
panel serve app.py --show --autoreload
```

### Command Options

- `--show`: Automatically opens the application in your default web browser
- `--autoreload`: Restarts the server when code changes are detected (useful for development)
- `--port 5006`: Specify a custom port (default is 5006)

### Accessing the Application

Once running, the application will be available at:
```
http://localhost:5006/app
```

Your web browser should open automatically if you used the `--show` flag.

## Using the Chat Interface

### Main Interface

The application consists of two main sections:

1. **Sidebar** (left):
   - About information
   - Features list
   - Model selector (currently GPT-4)
   - Clear History button

2. **Main Panel** (right):
   - Chat interface
   - Message history
   - Input field for your questions

### Asking Questions

1. **Type your question** in the input field at the bottom
2. **Press Enter** or click the send button
3. **Wait for response**: The assistant will:
   - Analyze your question
   - Determine if web search is needed
   - Use Google Search if required
   - Formulate a comprehensive answer
   - Display the response in the chat

### Example Queries

**Current Events:**
```
What are the latest developments in AI technology this week?
```

**Research Questions:**
```
Compare the GDP growth rates of major economies in 2024
```

**Fact-Checking:**
```
What is the current population of Tokyo?
```

**General Knowledge with Context:**
```
Explain quantum computing and list companies working on it
```

### Conversation Flow

The assistant maintains conversation context:

```
You: What is the capital of France?
Assistant: The capital of France is Paris...

You: What is its population?
Assistant: [Understands "its" refers to Paris and provides population data]
```

### Clearing History

Click the **"Clear History"** button in the sidebar to:
- Reset the conversation
- Clear all message history
- Start fresh with a new topic

## Troubleshooting

### Application Won't Start

**Error: API keys not found**
```
ValueError: API keys not found. Please set OPENAI_API_KEY and SERPAPI_API_KEY in your .env file.
```

**Solution**:
- Verify `.env` file exists in the project root
- Check that both `OPENAI_API_KEY` and `SERPAPI_API_KEY` are set
- Ensure no extra spaces around the `=` sign
- Restart the application

### No Response from Assistant

**Possible Causes**:
1. **Invalid API Keys**: Check that your OpenAI and SerpAPI keys are valid
2. **API Quota Exceeded**:
   - SerpAPI free tier: 100 searches/month
   - OpenAI: Check your usage limits
3. **Network Issues**: Verify internet connection

**Check the Console**:
The application runs with `verbose=True`, so agent reasoning is logged to the console. Look for error messages.

### Search Tool Not Working

**Symptoms**: Assistant doesn't use web search or returns generic answers

**Solutions**:
- Verify `SERPAPI_API_KEY` is correct
- Check SerpAPI quota at [SerpAPI Dashboard](https://serpapi.com/dashboard)
- Try asking explicitly: "Search the web for..."

### Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Use a different port
panel serve app.py --port 5007 --show
```

Or kill the process using port 5006:
```bash
# Find process
lsof -i :5006

# Kill process
kill -9 <PID>
```

## FAQ

### Q: How much does it cost to run?

**A**: Costs depend on usage:
- **OpenAI GPT-4**: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
- **SerpAPI**: Free tier (100 searches/month), then $50/month for 5K searches
- A typical conversation (10 messages) costs approximately $0.10-0.30

### Q: Can I use GPT-3.5 instead of GPT-4?

**A**: Yes, modify `app.py` line 30:
```python
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
```
GPT-3.5 is cheaper but less capable.

### Q: Does this work offline?

**A**: No, the application requires internet access for:
- OpenAI API calls
- SerpAPI web searches

### Q: Can I add more tools?

**A**: Yes! LangChain supports many tools. You can add:
- Wikipedia search
- Calculator
- Python REPL
- Custom tools

See the LangChain documentation for details.

### Q: How is my data stored?

**A**:
- Conversations are stored in memory only (not persisted to disk)
- Chat history is limited to the last 10 messages
- Clearing history removes all conversation data
- API calls are subject to OpenAI and SerpAPI privacy policies

### Q: Can multiple users use this simultaneously?

**A**: The current implementation is single-user. Each instance maintains its own conversation state. For multi-user support, you would need to implement session management.

### Q: The responses are too verbose/concise

**A**: Adjust the temperature parameter in `app.py` line 30:
```python
llm = ChatOpenAI(model="gpt-4", temperature=0.7)  # 0=focused, 1=creative
```

Or modify the system prompt to request specific response styles.

## Advanced Usage

### Running on a Different Host

To make the application accessible from other devices on your network:

```bash
panel serve app.py --address 0.0.0.0 --port 5006 --show
```

Access from other devices at: `http://your-ip-address:5006/app`

### Development Mode

For development with auto-reload:

```bash
panel serve app.py --autoreload --show
```

Changes to `app.py` will automatically restart the server.

### Viewing Agent Reasoning

The console output shows the agent's thought process:

```
User input received: What is the weather in London?
> Entering new AgentExecutor chain...
Thought: I should search for current weather information
Action: google_search
Action Input: weather London today
Observation: [Search results...]
Thought: I now have the information needed
Final Answer: [Response to user]
```

This is helpful for debugging and understanding how the agent makes decisions.

## Support

For issues, questions, or contributions:
- Check the console output for error messages
- Verify API keys and quotas
- Review the [LangChain documentation](https://python.langchain.com/)
- Check [Panel documentation](https://panel.holoviz.org/)

---

**Version**: 1.0
**Last Updated**: 2025-11-03
**Python Version**: 3.11+
**License**: [Add your license here]
