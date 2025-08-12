import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages):
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022", max_tokens=1024, messages=messages
    )

    return message.content[0].text


def main():
    print("Hello from claude-api-test!")
    messages = []
    add_user_message(messages, "What's is quantum computer? Short answer.")
    answer = chat(messages)
    print("Assistant:", answer)
    add_assistant_message(messages, answer)
    add_user_message(messages, "Write another sentence?")
    answer = chat(messages)
    print("Assistant:", answer)


if __name__ == "__main__":
    main()
