"""Get a file from github."""
import os

from github import Github, Auth

from .tool import Tool

TOKEN = os.environ["GITHUB_READ_TOKEN"]
CLIENT = Github(auth=Auth.Token(TOKEN))
NAME = "get_file_from_github"
FUNCTION_JSON = {
  "name": f"{NAME}",
  "description": "Return contents of a file from Github, typically code.",
  "parameters": {
    "type": "object",
    "properties": {
      "repository_owner": {
        "type": "string",
        "description": "Owner of the repository"
      },
      "repository_name": {
        "type": "string",
        "description": "Name of the repository"
      },
      "file_path": {
        "type": "string",
        "description": "Path to the file in the repository"
      }
    },
    "required": [
      "repository_owner",
      "repository_name",
      "file_path"
    ]
  }
}


def get_github_file(repository_owner: str, repository_name: str, file_path: str) -> str:
    """Get one file from a github repository."""
    try:
        repo = CLIENT.get_repo(f"{repository_owner}/{repository_name}")
        contents = repo.get_contents(file_path)
    except Exception as e:
        return str(e)
    return contents.decoded_content.decode("utf-8")


get_github_file_tool = Tool(NAME, FUNCTION_JSON, get_github_file)
