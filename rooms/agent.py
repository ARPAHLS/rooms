import litellm
import logging
import importlib.util
import sys
import os
from typing import Optional, List, Dict, Any
from .config import AgentConfig, ModelType

# Optional: Disable extreme litellm verbosity for normal usage
litellm.suppress_debug_info = True

# Custom JSON formatting or extra logic can be added here
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.model = config.model
        self.model_type = config.model_type
        self.system_prompt = config.system_prompt
        self.expertise = config.expertise
        
    def _execute_custom_function(self, messages: List[Dict[str, str]]) -> str:
        """Dynamically loads and invokes a custom python function for inference."""
        file_path = self.config.custom_function_path
        func_name = self.config.custom_function_name
        
        if not file_path or not func_name:
            return "[Error: Custom function path or name not provided]"
            
        if not os.path.isfile(file_path):
            return f"[Error: File not found: {file_path}]"
            
        try:
            # Dynamically import the module from the path
            spec = importlib.util.spec_from_file_location("custom_model_module", file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["custom_model_module"] = module
            spec.loader.exec_module(module)
            
            # Get the function
            inference_func = getattr(module, func_name)
            
            # We enforce standard (messages: List[Dict]) -> str signature for custom functions
            response = inference_func(messages)
            return str(response).strip()
            
        except AttributeError:
             return f"[Error: Function '{func_name}' not found in {file_path}]"
        except Exception as e:
            logger.error(f"Error executing custom function '{func_name}' in {file_path}: {e}")
            return f"[Error: Custom function failed. Details: {str(e)}]"

    def generate_response(self, context_messages: List[Dict[str, str]], override_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response using LiteLLM or a custom function.
        """
        params = override_params or {}
        
        # Build the system message for this agent
        full_system_prompt = self.config.system_prompt
        if self.config.custom_instructions:
            full_system_prompt += f"\n\nADDITIONAL INSTRUCTIONS FOR THIS SESSION:\n{self.config.custom_instructions}"
            
        messages = [{"role": "system", "content": full_system_prompt}]
        messages.extend(context_messages)
        
        if self.model_type == ModelType.CUSTOM_FUNCTION:
            return self._execute_custom_function(messages)
            
        try:
            # LiteLLM handling
            litellm_params = {
                "model": self.model,
                "messages": messages,
                "temperature": self.config.temperature
            }
            if self.config.max_tokens:
                litellm_params["max_tokens"] = self.config.max_tokens
                
            litellm_params["timeout"] = self.config.timeout
            litellm_params.update(params)

            response = litellm.completion(**litellm_params)
            return response.choices[0].message.content.strip()
            
        except litellm.Timeout as e:
            logger.error(f"Timeout logic executed for agent '{self.name}' on model '{self.model}': {e}")
            return f"[Timeout Error: The model '{self.model}' took too long to respond ({self.config.timeout}s)]"
        except Exception as e:
            logger.error(f"Error getting response from agent '{self.name}' on model '{self.model}': {e}")
            return f"[Error: Could not generate response. Details: {str(e)}]"

    def __repr__(self):
        return f"<Agent name={self.name} model={self.model}>"
