# OpenAI Assistants demo

This script runs an assistant with a couple of tools and allows you to interact with it.

Currently the available custom tools are

* web requests (Requests library)
* Github file fetching (Pygithub library)
* Google searches (Serpapi library)

Pygithub and Serpapi require tokens to work. Tokens are read from environment varialbes.
Look up the code files to find the correct environment variables to set.

Also set your `OPENAI_API_KEY` env variable.

To get started run

```sh
python main.py
```

When you run the code for the first time, an assistant is created. You should now see
this assistant also in your openai web ui. Take note of the ID (in the log or in the
web) and make sure it is found in the environment variable `ASSISTANT_ID`. 
You can edit it into the `.env` file. This avoids creating a new assistant every time the code is run.
