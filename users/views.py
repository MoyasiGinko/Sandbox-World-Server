from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.helpers import (
    build_access_token,
    decode_access_token,
    get_bearer_token,
    json_error,
    parse_request_body,
    serialize_user,
)


@csrf_exempt
@require_http_methods(["POST"])
def auth_register_api(request: HttpRequest) -> HttpResponse:
    data = parse_request_body(request)
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if len(username) < 3 or len(username) > 20:
        return json_error("Username must be 3-20 characters", status=400)
    if not username.replace("_", "a").isalnum():
        return json_error("Username format is invalid", status=400)
    if "@" not in email or "." not in email:
        return json_error("Email format is invalid", status=400)
    if len(password) < 8:
        return json_error("Password must be at least 8 characters", status=400)

    if User.objects.filter(username=username).exists():
        return json_error("Username already taken", status=409)
    if User.objects.filter(email=email).exists():
        return json_error("Email already registered", status=409)

    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password),
        first_name=username,
    )
    token = build_access_token(user)

    return JsonResponse({"token": token, "user": serialize_user(user)}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def auth_login_api(request: HttpRequest) -> HttpResponse:
    data = parse_request_body(request)
    login_id = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if login_id == "" or password == "":
        return json_error("Invalid credentials", status=401)

    user = User.objects.filter(username=login_id).first()
    if user is None:
        user = User.objects.filter(email=login_id.lower()).first()
    if user is None:
        return json_error("Invalid credentials", status=401)

    if not check_password(password, user.password):
        return json_error("Invalid credentials", status=401)

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    token = build_access_token(user)
    return JsonResponse({"token": token, "user": serialize_user(user)})


@csrf_exempt
@require_http_methods(["GET"])
def auth_verify_api(request: HttpRequest) -> HttpResponse:
    token = get_bearer_token(request)
    if token is None:
        return JsonResponse({"valid": False, "error": "No token provided"}, status=401)

    decoded = decode_access_token(token)
    if decoded is None:
        return JsonResponse({"valid": False, "error": "Invalid token"}, status=403)

    user_id = int(decoded.get("userId", 0) or 0)
    user = User.objects.filter(id=user_id).first()
    if user is None:
        return JsonResponse({"valid": False, "error": "User not found"}, status=404)

    return JsonResponse({"valid": True, "user": serialize_user(user)})


@csrf_exempt
@require_http_methods(["PUT"])
def update_display_name_api(request: HttpRequest) -> HttpResponse:
    token = get_bearer_token(request)
    if token is None:
        return json_error("Authentication required", status=401)

    decoded = decode_access_token(token)
    if decoded is None:
        return json_error("Invalid token", status=403)

    user_id = int(decoded.get("userId", 0) or 0)
    user = User.objects.filter(id=user_id).first()
    if user is None:
        return json_error("User not found", status=404)

    data = parse_request_body(request)
    display_name = str(data.get("display_name", "")).strip()
    if display_name == "" or len(display_name) > 30:
        return json_error("Display name must be 1-30 characters", status=400)

    user.first_name = display_name
    user.save(update_fields=["first_name"])
    return JsonResponse({"success": True, "user": serialize_user(user)})
