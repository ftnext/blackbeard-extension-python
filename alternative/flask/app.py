from pprint import pprint

import httpx
from flask import Flask, request

app = Flask(__name__)


@app.post("/")
def stream():
    x_github_token = request.headers["x-github-token"]
    payload = request.get_json()
    pprint(payload, sort_dicts=False)
    messages = payload["messages"]
    messages.insert(
        0,
        {
            "role": "system",
            "content": "You are a helpful assistant that replies to user messages as if you were the Blackbeard Pirate.",
        },
    )

    headers = {
        "Authorization": f"Bearer {x_github_token}",
        "Content-Type": "application/json",
    }
    data = {"messages": messages, "stream": True}

    def pass_generator():
        with httpx.stream(
            "POST",
            "https://api.githubcopilot.com/chat/completions",
            headers=headers,
            json=data,
        ) as response:
            for chunk in response.iter_lines():
                if chunk:
                    yield f"{chunk}\n\n"

    return pass_generator(), {"Content-Type": "text/event-stream"}
