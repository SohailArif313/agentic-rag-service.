import httpx

from settings import API_ACCESS_KEY, API_URL


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def ask(question: str, openai_key: str) -> dict:
    try:
        response = httpx.post(
            f"{API_URL}/chat",
            json={"question": question},
            headers={"X-API-Key": API_ACCESS_KEY, "X-OpenAI-Key": openai_key},
            timeout=150,
        )
    except httpx.RequestError as exc:
        raise ApiError("Could not reach the API. Is the server running?") from exc

    if response.status_code == 200:
        return response.json()

    if response.status_code == 404:
        raise ApiError(f"API endpoint not found at {API_URL}/chat. Check API_URL.")

    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = None
    if not isinstance(detail, str):
        detail = f"Request failed (status {response.status_code})."
    raise ApiError(detail, response.status_code)