# ai_core.py
import sys

try:
    import ollama
except ImportError:
    print("Missing dependency: ollama")
    print("Install with: pip install ollama")
    sys.exit(1)


def get_model_response(messages: list, model_name: str = "llama3.2") -> str:
    """
    Send a list of messages to the Ollama model and return the assistant's reply.

    Args:
        messages: List of message dicts, e.g. [{"role": "user", "content": "Hello"}]
        model_name: Name of the Ollama model to use (default "llama3.2")

    Returns:
        The content of the assistant's reply as a string.
        If an error occurs or the messages list is empty, returns an empty string.
    """
    if not messages:
        # No input to send
        return ""

    try:
        response = ollama.chat(model=model_name, messages=messages)
    except Exception as exc:
        print("Failed to run the model.")
        print("Make sure Ollama is installed and the model is downloaded.")
        print(f"Error: {exc}")
        # In a GUI app, you might want to return a user‑friendly error message
        return "I'm having trouble connecting to my brain right now."

    # Return only the assistant's content
    return response["message"]["content"]


def chat_with_llama(model_name: str = "llama3.2") -> None:
    """
    Start an interactive chat session with a specified Ollama model.
    Type 'exit' or 'quit' to end the conversation.
    """
    messages = []  # holds the entire conversation history

    print(f"Starting a chat with {model_name}. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = ollama.chat(model=model_name, messages=messages)
        except Exception as exc:
            print("Failed to run the model.")
            print("Make sure Ollama is installed and the model is downloaded.")
            print(f"Error: {exc}")
            sys.exit(1)

        assistant_reply = response["message"]["content"]
        print(f"Assistant: {assistant_reply}\n")

        messages.append({"role": "assistant", "content": assistant_reply})


if __name__ == "__main__":
    # If the script is run directly, start the interactive chat
    chat_with_llama()