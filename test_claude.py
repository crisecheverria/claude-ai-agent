import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def test_claude_api():
    """Test basic Claude API functionality"""
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "Hello! Can you tell me a short joke?"}
            ]
        )
        
        print("API Response:")
        print(message.content[0].text)
        print(f"\nTokens used: {message.usage.input_tokens} input, {message.usage.output_tokens} output")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_claude_api()