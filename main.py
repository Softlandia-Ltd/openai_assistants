from datetime import datetime
import json
import logging
import sys
import os
import time

import dotenv
import openai
# Import OpenAI classes for type hinting
from openai.types.beta.threads.required_action_function_tool_call import Function
from openai.types.beta.thread import Thread
from openai.types.beta.assistant import Assistant
from rich.console import Console
from rich.markdown import Markdown

# Read the .env file before importing tools that need configs
dotenv.load_dotenv()

from tools.web_search import web_search_tool
from tools.web_request import get_request_tool
from tools.github_client import get_github_file_tool


logger = logging.getLogger(__name__)

# Import the Tools you want the assistant to use,
# they will automatically be added to the assistant,
# note that this list needs to match the tools that were given to the 
# assistant when it was created, so if you change the tools, 
# don't use an old assistant ID!
TOOLS = {
    get_request_tool.name: get_request_tool,
    # web_search_tool.name: web_search_tool,
    # get_github_file_tool.name: get_github_file_tool,
}
CLIENT = openai.Client(api_key=os.environ["OPENAI_API_KEY"])


def call_function(function: Function):
    """Call the function given in run."""
    logger.info(f"Calling {function.name} with args: {function.arguments}")
    args = json.loads(function.arguments)
    fn = TOOLS[function.name].func
    result = fn(**args) 
    return str(result)


def answer(task: str, thread: Thread, assistant: Assistant) -> list[str]:
    """Get an answer from the assistant."""
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    message = CLIENT.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"{task} \n{date}",
    )
    run = CLIENT.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while run.status != "completed":

        # Check if we need to make function calls
        if run.status == "requires_action":
            logger.info("Action required!")

            if run.required_action.type != "submit_tool_outputs":
                logger.info("Unknown action type!")
                sys.exit(1)

            # Call the function..
            outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                tool_call_id = tool_call.id
                tool_output = call_function(tool_call.function)
                outputs.append({
                    "tool_call_id": tool_call_id,
                    "output": tool_output,
                })

            run = CLIENT.beta.threads.runs.submit_tool_outputs(
                run_id=run.id,
                thread_id=thread.id,
                tool_outputs=outputs
            )

        # Give some time for the assistant to work
        time.sleep(5)
        run = CLIENT.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        logger.info(f"Run status: {run.status}")

    logger.info("Run completed!")

    messages = CLIENT.beta.threads.messages.list(
      thread_id=thread.id
    )

    latest = messages.data[0]
    return [c.text for c in latest.content]


def run_loop(assistant: Assistant, thread: Thread):
    """Run the conversation loop."""
    # Ask the user for a task to complete
    task = input("What task would you like me to do? \n")
    
    # bail out if user didn't enter anything
    console = Console()
    while task:

        if not task:
            print("You didn't enter anything. Exiting.")
            sys.exit(0)

        a = answer(task, thread, assistant)

        for msg in a:
            md = (Markdown(msg.value))
            console.print(md)

        task = input("Reply: \n")


def main():

    try:
        assistant = CLIENT.beta.assistants.retrieve(os.environ["ASSISTANT_ID"])
    except:
        assistant = CLIENT.beta.assistants.create(
            name="Software developer",
            instructions="ROLE: exper Python developer. OS: Debian Linux, SHELL: Bash",
            tools = [{"type": "function", "function": tool.schema} for tool in TOOLS.values()],
            model="gpt-4-1106-preview",
        )
        logger.info("Created new assistants with ID %s", assistant.id)

    thread = CLIENT.beta.threads.create()

    try:
        run_loop(assistant, thread)
    except Exception as e:
        logger.exception("Shutting down.")
    finally:
        CLIENT.beta.threads.delete(thread.id)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
