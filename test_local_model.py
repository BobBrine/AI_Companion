import sys

try:
    import ollama
except ImportError:
    print("Missing dependency: ollama")
    print("Install with: pip install ollama")
    sys.exit(1)


def main() -> None:
    model_name = "llama3.2"

    messages = [
        {"role": "user", "content": "Hi there! Can you tell me a joke?"},
    ]
    
    try:
        response = ollama.chat(
            model=model_name,
            messages=messages,
        )
    except Exception as exc:
        print("Failed to run the model.")
        print("Make sure Ollama is installed and the model is downloaded.")
        print(f"Error: {exc}")
        sys.exit(1)

    print(response["message"]["content"])


if __name__ == "__main__":
    main()
