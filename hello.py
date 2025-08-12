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


# Temperature Ranges 0.0 to 1.0
# Temperature controls the randomness of the output.
# Low Temp (0.0 - 0.3): More deterministic, focused responses, factual responses, coding assistance.
# Medium Temp (0.4 - 0.7): Balanced, creative yet coherent, educational responses, problem-solving.
# High Temp (0.8 - 1.0): Highly creative, more varied responses, brainstorming, storytelling.


def chat(messages, system=None, temperature=0.7):
    params = {
        "max_tokens": 1024,
        "model": "claude-3-5-sonnet-20241022",
        "messages": messages,
        "temperature": temperature,
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)

    return message.content[0].text


def main():
    print("Hello from claude!. Type 'exit' or 'quit' to end the chat.")
    # Initialize the conversation
    messages = []

    system = """
    You are a patient math tutor.
    Do not directly answer a student's question.
    Guide them to a solution step by step.
    """
    # system = "You are a helpful coding assistant who provides clear and concise explanations."

    while True:
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break

        add_user_message(messages, user_input)
        response = chat(messages, system=system)
        add_assistant_message(messages, response)

        print(f"🤖 {response}")


if __name__ == "__main__":
    main()
