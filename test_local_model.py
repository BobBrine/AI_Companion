import sys

try:
    import ollama
except ImportError:
    print("Missing dependency: ollama")
    print("Install with: pip install ollama")
    sys.exit(1)


def main() -> None:
    # Simple prompt for a 16 GB RAM machine; llama3.2 is a good starting point.
    model_name = "llama3.2"
    prompt = "Write a short friendly greeting for a desktop AI companion."

    try:
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        print("Failed to run the model.")
        print("Make sure Ollama is installed and the model is downloaded.")
        print(f"Error: {exc}")
        sys.exit(1)

    print(response["message"]["content"])


if __name__ == "__main__":
    main()
