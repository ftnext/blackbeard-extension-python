import httpx
import respx
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Hello Copilot!"


def github_llm_bytes_stream():
    yield b'data: {"id":"chatcmpl-TEST","object":"chat.completion.chunk","created":1732376103,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_0705bf87c0","choices":[{"index":0,"delta":{"role":"assistant","content":"","refusal":null},"logprobs":null,"finish_reason":null}]}\n\n'
    yield b'data: {"id":"chatcmpl-TEST","object":"chat.completion.chunk","created":1732376103,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_0705bf87c0","choices":[{"index":0,"delta":{"content":"1"},"logprobs":null,"finish_reason":null}]}\n\n'
    yield b'data: {"id":"chatcmpl-TEST","object":"chat.completion.chunk","created":1732376103,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_0705bf87c0","choices":[{"index":0,"delta":{},"logprobs":null,"finish_reason":"stop"}]}\n\n'
    yield b"data: [DONE]\n\n"


@respx.mock(assert_all_mocked=True, assert_all_called=True)
def test_blackbeard(respx_mock):
    respx_mock.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"login": "github_handle"})
    )
    respx_mock.post("https://api.githubcopilot.com/chat/completions").mock(
        return_value=httpx.Response(200, stream=github_llm_bytes_stream())
    )

    response = client.post(
        "/",
        headers={"X-Github-Token": "test-token"},
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )

    assert response.status_code == 200
    expected = b'data: {"id":"chatcmpl-TEST","object":"chat.completion.chunk","created":1732376103,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_0705bf87c0","choices":[{"index":0,"delta":{"role":"assistant","content":"","refusal":null},"logprobs":null,"finish_reason":null}]}\n\ndata: {"id":"chatcmpl-TEST","object":"chat.completion.chunk","created":1732376103,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_0705bf87c0","choices":[{"index":0,"delta":{"content":"1"},"logprobs":null,"finish_reason":null}]}\n\ndata: {"id":"chatcmpl-TEST","object":"chat.completion.chunk","created":1732376103,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_0705bf87c0","choices":[{"index":0,"delta":{},"logprobs":null,"finish_reason":"stop"}]}\n\ndata: [DONE]\n\n'
    assert list(response.stream)[0] == expected
