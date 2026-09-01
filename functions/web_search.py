import os
import time
from config import SEARCH_PROVIDER, SEARCH_MAX_RESULTS

_CACHE = {}
_CACHE_TTL = 300  # seconds a cached search stays valid (5 minutes)


def web_search(query: str) -> str:
    if query in _CACHE:
        result_text, searched_at = _CACHE[query]
        if time.time() - searched_at < _CACHE_TTL:
            print(f"(search cache hit for '{query}')")
            return result_text

    # dispatch to whichever provider is configured
    if SEARCH_PROVIDER == "tavily":
        result = _search_tavily(query)
    else:
        return f'Error: Unknown search provider "{SEARCH_PROVIDER}"'

   
    if not result.startswith("Error:"):
        _CACHE[query] = (result, time.time())

    return result


def _search_tavily(query: str) -> str:
    try:
        from tavily import TavilyClient

        api_key = os.environ.get("TAVILY_API_KEY")
        if api_key is None:
            return "Error: TAVILY_API_KEY is not set in the environment"

        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=SEARCH_MAX_RESULTS)

        results = response.get("results", [])
        if not results:
            return f'No search results found for "{query}"'

        formatted = []
        for r in results:
            title = r.get("title", "(no title)")
            url = r.get("url", "")
            content = r.get("content", "")
            formatted.append(f"Title: {title}\nURL: {url}\nSnippet: {content}")

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Error: Search failed - {str(e)}"


schema_web_search = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Searches the web for current information and returns a list of relevant results, each with a title, URL, and content snippet. Use this to find pages about a topic; follow up with fetch_url to read a specific page in full.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query describing what to look for",
                },
            },
            "required": ["query"],
        },
    }
}