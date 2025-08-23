import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

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


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


# Temperature Ranges 0.0 to 1.0
# Temperature controls the randomness of the output.
# Low Temp (0.0 - 0.3): More deterministic, focused responses, factual responses, coding assistance.
# Medium Temp (0.4 - 0.7): Balanced, creative yet coherent, educational responses, problem-solving.
# High Temp (0.8 - 1.0): Highly creative, more varied responses, brainstorming, storytelling.


def chat(messages, system=None, temperature=0.7):
    try:
        params = {
            "max_tokens": 1024,
            "model": "claude-3-5-sonnet-20241022",
            "messages": messages,
            "temperature": temperature,
            "tools": tools
        }

        if system:
            params["system"] = system

        message = client.messages.create(**params)

        # Handle tool use
        if message.stop_reason == "tool_use":
            # Add the assistant's tool use message to conversation
            messages.append({
                "role": "assistant",
                "content": message.content
            })
            
            # Process tool results
            tool_results = []
            for content_block in message.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    
                    if tool_name == "create_file":
                        result = create_file_tool(tool_input["file_path"], tool_input["content"])
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": result
                        })
            
            # Add tool results as user message
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Get Claude's response to the tool results
            follow_up_params = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "messages": messages,
                "tools": tools,
                "temperature": temperature
            }
            
            if system:
                follow_up_params["system"] = system
                
            follow_up_response = client.messages.create(**follow_up_params)
            
            return follow_up_response.content[0].text
        
        # Regular text response
        return message.content[0].text
        
    except Exception as e:
        return f"API Error: {str(e)}"


def main():
    print("Hello from claude! I can help with math and also create files for you.")
    print("Type 'exit' or 'quit' to end the chat.")
    # Initialize the conversation
    messages = []

    system = """
    You are a helpful assistant that can:
    1. Help with math problems as a patient tutor (guide step by step)
    2. Create files when requested using the create_file tool
    
    When users ask you to create, write, or save a file, use the create_file tool with the appropriate file path and content.
    """

    while True:
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break

        add_user_message(messages, user_input)
        response = chat(messages, system)
        add_assistant_message(messages, response)

        print(f"🤖 {response}")


if __name__ == "__main__":
    main()
