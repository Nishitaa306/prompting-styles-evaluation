import os
from google import genai

try:
    print("Starting script...")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Please set your API key first."
        )

    print("API key found")

    client = genai.Client(api_key=api_key)

    print("Gemini client created")

    with open("meta_prompt.txt", "r") as f:
        template = f.read()

    print("Meta prompt loaded")

    brief = input("\nEnter vague brief: ")

    final_prompt = template.replace("{brief}", brief)

    print("\nSending request to Gemini...")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=final_prompt
    )

    print("\n==============================")
    print("GENERATED PROMPT")
    print("==============================\n")

    print(response.text)

except FileNotFoundError:
    print("Error: meta_prompt.txt not found in the current directory.")

except Exception as e:
    print(f"\nError: {e}")