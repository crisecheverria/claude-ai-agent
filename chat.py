import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import Message

load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    default_headers={"anthropic-version": "2023-06-01"}
)

# Define the file creation tool
def create_file_tool(file_path, content):
    """Create a file with the specified content"""
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"File '{file_path}' created successfully!"
    except Exception as e:
        return f"Error creating file '{file_path}': {str(e)}"

# Tool definition for Claude
tools = [
    {
        "name": "create_file",
        "description": "Create a new file with specified content. Use this when the user asks to create, write, or save a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path where the file should be created (e.g., 'example.py', 'docs/readme.md')"
                },
                "content": {
                    "type": "string", 
                    "description": "The content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    }
]


def add_user_message(messages, message):
    user_message = {
        "role": "user", 
        "content": message.content if isinstance(message, Message) else message
    }
    messages.append(user_message)


def add_assistant_message(messages, message):
    assistant_message = {
        "role": "assistant", 
        "content": message.content if isinstance(message, Message) else message
    }
    messages.append(assistant_message)


def text_from_message(message):
    return "\n".join(
        [block.text for block in message.content if block.type == "text"]
    )


def run_tool(tool_name, tool_input):
    """Route tool requests to their implementations"""
    if tool_name == "create_file":
        return create_file_tool(tool_input["file_path"], tool_input["content"])
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message):
    """Execute all tool requests in a message and return tool result blocks"""
    tool_requests = [
        block for block in message.content if block.type == "tool_use"
    ]
    tool_result_blocks = []
    
    for tool_request in tool_requests:
        try:
            tool_output = run_tool(tool_request.name, tool_request.input)
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": json.dumps(tool_output),
                "is_error": False
            }
        except Exception as e:
            tool_result_block = {
                "type": "tool_result", 
                "tool_use_id": tool_request.id,
                "content": f"Error: {e}",
                "is_error": True
            }
        
        tool_result_blocks.append(tool_result_block)
    
    return tool_result_blocks


def run_conversation(messages, system=None, temperature=0.7, tools=None):
    """Run a multi-turn conversation with tools until Claude provides a final answer"""
    while True:
        response = chat(messages, system, temperature, tools)
        add_assistant_message(messages, response)
        
        # Display Claude's response (including any text before tool calls)
        response_text = text_from_message(response)
        if response_text.strip():
            print(f"🤖 {response_text}")
        
        # Check if Claude wants to use tools
        if response.stop_reason != "tool_use":
            break
            
        # Execute tools and add results to conversation
        tool_results = run_tools(response)
        add_user_message(messages, tool_results)
    
    return messages


# Temperature Ranges 0.0 to 1.0
# Temperature controls the randomness of the output.
# Low Temp (0.0 - 0.3): More deterministic, focused responses, factual responses, coding assistance.
# Medium Temp (0.4 - 0.7): Balanced, creative yet coherent, educational responses, problem-solving.
# High Temp (0.8 - 1.0): Highly creative, more varied responses, brainstorming, storytelling.


def chat(messages, system=None, temperature=0.7, tools=None):
    try:
        params = {
            "max_tokens": 1024,
            "model": "claude-3-5-sonnet-20241022",
            "messages": messages,
            "temperature": temperature
        }
        
        if tools:
            params["tools"] = tools

        if system:
            params["system"] = system

        message = client.messages.create(**params)
        return message
        
    except Exception as e:
        return f"API Error: {str(e)}"


def main():
    print("Hello from claude! I can help with math/coding problems.")
    print("Type 'exit' or 'quit' to end the chat.")
    # Initialize the conversation
    messages = []

    system = """
    You are a helpful assistant that can:
    1. Help with math, or coding problems as a patient tutor (guide step by step)
    2. Create files when requested using the create_file tool
    
    When users ask you to create, write, or save a file, use the create_file tool with the appropriate file path and content.
    """

    while True:
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break

        add_user_message(messages, user_input)
        run_conversation(messages, system, tools=tools)


if __name__ == "__main__":
    main()
