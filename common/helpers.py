import json
from datetime import UTC, datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest, JsonResponse


JWT_SECRET = settings.JWT_SECRET
JWT_EXPIRATION_DAYS = settings.JWT_EXPIRATION_DAYS


def json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def parse_request_body(request: HttpRequest) -> dict:
    if request.POST:
        return request.POST.dict()

    if not request.body:
        return {}

    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


def get_bearer_token(request: HttpRequest) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip()


def decode_access_token(token: str) -> dict | None:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if isinstance(decoded, dict):
            return decoded
    except Exception:
        return None
    return None


def serialize_user(user: User) -> dict:
    display_name = user.first_name.strip() if user.first_name else user.username
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": display_name,
    }


def build_access_token(user: User) -> str:
    display_name = user.first_name.strip() if user.first_name else user.username
    payload = {
        "userId": user.id,
        "username": user.username,
        "display_name": display_name,
        "exp": datetime.now(UTC) + timedelta(days=JWT_EXPIRATION_DAYS),
    }
    return str(jwt.encode(payload, JWT_SECRET, algorithm="HS256"))
