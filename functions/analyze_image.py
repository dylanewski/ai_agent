import os
import base64
from openai import OpenAI
from config import MODEL_BACKEND


def analyze_image(image_url: str, question: str = "Describe this image in detail.") -> str:
    try:
        if MODEL_BACKEND != "openrouter":
            return "Error: image analysis requires the cloud (openrouter) backend with a vision-capable model."

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if api_key is None:
            return "Error: OPENROUTER_API_KEY is not set"

        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

        # if it's a local file path read it and base64-encode it so model can access it, otherwise just pass the URL directly
        
        if not image_url.startswith("http"):
            with open(image_url, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            image_ref = f"data:image/png;base64,{encoded}"
        else:
            image_ref = image_url

        response = client.chat.completions.create(
            model="google/gemini-3.7-flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": image_ref}},
                    ],
                }
            ],
        )
        return response.choices[0].message.content  # type: ignore

    except Exception as e:
        return f"Error: could not analyze image - {str(e)}"



schema_analyze_image = {
    "type": "function",
    "function": {
        "name": "analyze_image",
        "description": "Analyzes an image at a given URL and answers a question about it or describes it. Use when the user provides an image URL and asks what's in it, to describe it, or to answer a question about it.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "The URL of the image to analyze",
                },
                "question": {
                    "type": "string",
                    "description": "What to ask about the image (optional; defaults to a general description)",
                },
            },
            "required": ["image_url"],
        },
    }
}