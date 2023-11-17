from .tool import Tool

NAME = "make_get_request"
FUNCTION_JSON = {
  "name": f"{NAME}",
  "parameters": {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "The URL address of the web request."
      }
    },
    "required": [
      "url"
    ]
  },
  "description": "Make a GET web request to an URL"
}


def make_get_request(url: str) -> str:
    """Make a GET web request to an URL."""
    import requests
    result = requests.get(url, timeout=30)
    return result.text


get_request_tool = Tool(NAME, FUNCTION_JSON, make_get_request)
