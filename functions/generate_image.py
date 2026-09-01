import urllib.parse
from config import IMAGE_PROVIDER


def generate_image(prompt: str) -> str:
    # dispatch to whichever image provider is configured
    if IMAGE_PROVIDER == "pollinations":
        return _generate_pollinations(prompt)
    else:
        return f'Error: Unknown image provider "{IMAGE_PROVIDER}"'


def _generate_pollinations(prompt: str) -> str:
    # build the Pollinations URL — the image IS this URL, no download needed
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}"
    # return it in a form the frontend can recognize and render as an image
    return f"IMAGE: {url}"


schema_generate_image = {
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Generates an image from a text description and returns it to display in the chat. Use when the user asks to create, draw, or generate an image or picture.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "A detailed text description of the image to generate",
                },
            },
            "required": ["prompt"],
        },
    }
}