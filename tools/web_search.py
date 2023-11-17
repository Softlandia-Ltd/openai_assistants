import os

import serpapi

from .tool import Tool

API_KEY = os.environ["SERPAPI_API_KEY"]
NAME = "search_web"
FUNCTION_JSON = {
  "name": f"{NAME}",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query for web search."
      }
    },
    "required": [
      "query"
    ]
  },
  "description": "Make a web search with a query"
}


def search_web(query: str) -> str:
    """Search the web for the query using the OpenAI API."""
    top_n = 5

    client = serpapi.Client(api_key=API_KEY)
    results = client.search({
        "engine": "google",
        "q": query, 
    })

    organic = results["organic_results"]
    organic = [o for o in organic if o["position"] <= top_n]
    # Only pick interesting fields
    organic = [{k: o[k] for k in ["position", "title", "link", "snippet"]} for o in organic]
    return organic


web_search_tool = Tool(NAME, FUNCTION_JSON, search_web)
