import requests
from bs4 import BeautifulSoup
from config import WEB_MAX_CHARS


def fetch_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        
        for tag in soup(["script", "style"]):
            tag.decompose()

       
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        if len(clean_text) > WEB_MAX_CHARS:
            clean_text = clean_text[:WEB_MAX_CHARS] + f'[...Page "{url}" truncated at {WEB_MAX_CHARS} characters]'

        if not clean_text:
            return f'Error: No readable text found at "{url}"'

        return clean_text

    except requests.exceptions.Timeout:
        return f'Error: Request to "{url}" timed out'
    except requests.exceptions.RequestException as e:
        return f'Error: Could not fetch "{url}" - {str(e)}'
    except Exception as e:
        return f'Error: An unexpected error occurred - {str(e)}'


schema_fetch_url = {
    "type": "function",
    "function": {
        "name": "fetch_url",
        "description": "Fetches a web page at the given URL and returns its readable text content, truncated to a maximum number of characters",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL of the web page to fetch, including https://",
                },
            },
            "required": ["url"],
        },
    }
}