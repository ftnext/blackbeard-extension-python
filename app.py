from pprint import pprint

import httpx
from fastapi import FastAPI, Header, Request
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.post("/")
async def stream(request: Request, x_github_token: str = Header(None)):
    payload = await request.json()
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

    return StreamingResponse(pass_generator(), media_type="text/event-stream")
