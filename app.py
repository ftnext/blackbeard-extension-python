import httpx
from fastapi import FastAPI, Header, Request
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.post("/")
async def stream(request: Request, x_github_token: str = Header(None)):
    req = await request.json()
    user_message = req["messages"][-1]["content"]

    headers = {
        "Authorization": f"Bearer {x_github_token}",
        "Content-Type": "application/json",
    }
    data = {"messages": [{"role": "user", "content": user_message}], "stream": True}

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
