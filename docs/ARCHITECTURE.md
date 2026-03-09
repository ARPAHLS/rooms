# Multi-Agent Rooms Architecture

## How LiteLLM Works
**LiteLLM is a universal routing library, not an AI model or an API endpoint itself.**

The Multi-Agent Rooms framework uses LiteLLM as an adapter. Different AI providers (OpenAI, Anthropic, local applications like Ollama) expect code formatted in entirely different ways. LiteLLM acts as a universal translator. The Rooms framework sends standard "messages" to LiteLLM, and LiteLLM translates them and routes them to the correct backend.

### Is it Free? Does it require API Keys?
LiteLLM is a completely free, open-source python package. Because it's just a translator, it does not charge money or process your data externally.

When you configure an agent's `model` to a string like `ollama/llama3`, LiteLLM recognizes the `ollama/` prefix. It explicitly **does not** send the request over the internet to a commercial provider. Instead, it routes the HTTP request to `http://localhost:11434`, which is the default port Ollama uses on your local machine. 

Because the request never leaves your computer, **there are no API keys required, no rate limits, and zero costs.**

When the Agents reply to you in the terminal, it means your computer's local CPU/GPU is quietly processing the inference via the Ollama application running in your background!

## Custom Model Integrations (Bring Your Own Code)

If you do not want to use LiteLLM at all, the framework allows you to inject arbitrary Python scripts as the "brain" for an agent.

1. Create a python file (e.g. `my_model.py`).
2. Write a function that accepts a `List[Dict[str, str]]` (the conversation history) and returns a `str` (the agent's reply).
3. In the CLI wizard, select `custom_function` as the Model Type.
4. Provide the path to `my_model.py` and the exact name of the function you wrote.

The framework will dynamically import your file at runtime and use it exclusively for that agent's turns.
