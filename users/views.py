from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db import transaction
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
from users.models import MatchHistory, PlayerStats


def _get_authenticated_user(request: HttpRequest) -> User | None:
    token = get_bearer_token(request)
    if token is None:
        return None
    decoded = decode_access_token(token)
    if decoded is None:
        return None
    user_id = int(decoded.get("userId", 0) or 0)
    return User.objects.filter(id=user_id).first()


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
    user = _get_authenticated_user(request)
    if user is None:
        return json_error("Authentication required", status=401)

    data = parse_request_body(request)
    display_name = str(data.get("display_name", "")).strip()
    if display_name == "" or len(display_name) > 30:
        return json_error("Display name must be 1-30 characters", status=400)

    user.first_name = display_name
    user.save(update_fields=["first_name"])
    return JsonResponse({"success": True, "user": serialize_user(user)})


@csrf_exempt
@require_http_methods(["GET"])
def user_stats_api(request: HttpRequest, user_id: int) -> HttpResponse:
    user = User.objects.filter(id=user_id).first()
    if user is None:
        return json_error("User not found", status=404)

    stats, _ = PlayerStats.objects.get_or_create(user=user)
    return JsonResponse(stats.to_public_dict())


@csrf_exempt
@require_http_methods(["GET"])
def leaderboard_api(request: HttpRequest) -> HttpResponse:
    stat = str(request.GET.get("stat", "kills")).strip()
    valid_stats = {
        "kills",
        "deaths",
        "wins",
        "losses",
        "playtime_seconds",
        "matches_played",
    }
    if stat not in valid_stats:
        stat = "kills"

    try:
        limit = int(request.GET.get("limit", "100"))
    except ValueError:
        limit = 100
    if limit < 1:
        limit = 1
    if limit > 500:
        limit = 500

    rows = (
        PlayerStats.objects.select_related("user")
        .filter(user__is_active=True)
        .order_by(f"-{stat}", "user__username")[:limit]
    )

    leaderboard = []
    for index, row in enumerate(rows, start=1):
        display_name = row.user.first_name.strip() if row.user.first_name else row.user.username
        leaderboard.append(
            {
                "rank": index,
                "user_id": row.user_id,
                "username": row.user.username,
                "display_name": display_name,
                "stat_value": getattr(row, stat),
                "kills": row.kills,
                "deaths": row.deaths,
                "wins": row.wins,
                "losses": row.losses,
                "matches_played": row.matches_played,
                "playtime_seconds": row.playtime_seconds,
            }
        )

    return JsonResponse({"stat": stat, "count": len(leaderboard), "leaderboard": leaderboard})


@csrf_exempt
@require_http_methods(["POST"])
def match_report_api(request: HttpRequest) -> HttpResponse:
    reporter = _get_authenticated_user(request)
    if reporter is None:
        return json_error("Authentication required", status=401)

    data = parse_request_body(request)
    room_id = str(data.get("room_id", "")).strip()
    gamemode = str(data.get("gamemode", "unknown")).strip() or "unknown"
    if room_id == "":
        return json_error("room_id is required", status=400)

    winner_user_id_raw = data.get("winner_user_id")
    winner_user = None
    if winner_user_id_raw is not None:
        try:
            winner_user = User.objects.filter(id=int(winner_user_id_raw)).first()
        except (TypeError, ValueError):
            winner_user = None

    try:
        duration_seconds = int(data.get("duration_seconds", 0) or 0)
    except (TypeError, ValueError):
        duration_seconds = 0
    if duration_seconds < 0:
        duration_seconds = 0

    players = data.get("players", [])
    if not isinstance(players, list):
        return json_error("players must be an array", status=400)

    now = timezone.now()
    stats_snapshot: list[dict] = []

    with transaction.atomic():
        match = MatchHistory.objects.create(
            room_id=room_id,
            gamemode=gamemode,
            winner=winner_user,
            ended_at=now,
            duration_seconds=duration_seconds,
            details={
                "reported_by": reporter.id,
                "players": players,
            },
        )

        for item in players:
            if not isinstance(item, dict):
                continue
            user_id_raw = item.get("user_id", item.get("userId"))
            try:
                target_user_id = int(user_id_raw)
            except (TypeError, ValueError):
                continue

            target_user = User.objects.filter(id=target_user_id).first()
            if target_user is None:
                continue

            try:
                kills_delta = int(item.get("kills", 0) or 0)
            except (TypeError, ValueError):
                kills_delta = 0
            try:
                deaths_delta = int(item.get("deaths", 0) or 0)
            except (TypeError, ValueError):
                deaths_delta = 0
            try:
                playtime_delta = int(item.get("playtime_seconds", 0) or 0)
            except (TypeError, ValueError):
                playtime_delta = 0

            won_flag = bool(item.get("won", False))
            if winner_user is not None and target_user.id == winner_user.id:
                won_flag = True

            stats, _ = PlayerStats.objects.get_or_create(user=target_user)
            stats.kills += max(kills_delta, 0)
            stats.deaths += max(deaths_delta, 0)
            stats.playtime_seconds += max(playtime_delta, 0)
            stats.matches_played += 1
            if won_flag:
                stats.wins += 1
            else:
                stats.losses += 1
            stats.last_match = now
            stats.save()

            snapshot_item = stats.to_public_dict()
            snapshot_item["won"] = won_flag
            stats_snapshot.append(snapshot_item)

        match.details = {
            **match.details,
            "stats_snapshot": stats_snapshot,
        }
        match.save(update_fields=["details"])

    return JsonResponse(
        {
            "success": True,
            "match_id": match.id,
            "processed_players": len(stats_snapshot),
            "stats": stats_snapshot,
        }
    )
