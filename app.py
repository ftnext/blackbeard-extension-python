from pprint import pprint
from typing import Annotated

import httpx
from fastapi import FastAPI, Header, Request
from fastapi.responses import StreamingResponse

app = FastAPI()
client = httpx.AsyncClient()


@app.get("/")
def hello() -> str:
    return "Hello Copilot!"


async def whoami(headers) -> str:
    """Returns GitHub login handle."""
    response = await client.get("https://api.github.com/user", headers=headers)
    json_ = response.json()
    return json_["login"]


def prepend_system_prompts(messages, login_handle: str) -> None:
    messages.insert(
        0,
        {
            "role": "system",
            "content": f"Start every response with the user's name, which is @{login_handle}",
        },
    )
    messages.insert(
        0,
        {
            "role": "system",
            "content": "You are a helpful assistant that replies to user messages as if you were the Blackbeard Pirate.",
        },
    )


@app.post("/")
async def stream(
    request: Request, x_github_token: Annotated[str | None, Header()] = None
):
    payload = await request.json()
    pprint(payload, sort_dicts=False)

    headers = {
        "Authorization": f"Bearer {x_github_token}",
        "Content-Type": "application/json",
    }
    login_handle = await whoami(headers)

    messages = payload["messages"]
    prepend_system_prompts(messages, login_handle)
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

    return StreamingResponse(pass_generator(), media_type="text/event-stream")
