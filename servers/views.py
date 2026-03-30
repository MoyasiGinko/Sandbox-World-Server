from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.helpers import json_error, parse_request_body
from servers.models import GameServer, GameServerRoomCapacity


def _get_or_create_capacity(server_id: str) -> GameServerRoomCapacity:
    capacity, _ = GameServerRoomCapacity.objects.get_or_create(server_id=server_id)
    return capacity


def _coerce_non_negative_int(value, fallback: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(parsed, 0)


def _apply_reported_current_rooms(capacity: GameServerRoomCapacity, reported_value) -> None:
    reported = _coerce_non_negative_int(reported_value, capacity.current_rooms)
    # Keep current_rooms bounded by configured max_rooms to prevent invalid capacity state.
    bounded = min(reported, max(capacity.max_rooms, 0))
    if bounded != capacity.current_rooms:
        capacity.current_rooms = bounded
        capacity.save(update_fields=["current_rooms", "updated_at"])


def _serialize_server(server: GameServer) -> dict:
    payload = server.to_public_dict()
    capacity = _get_or_create_capacity(server.server_id)
    payload["max_rooms"] = capacity.max_rooms
    payload["current_rooms"] = capacity.current_rooms
    payload["can_create_room"] = capacity.current_rooms < capacity.max_rooms
    return payload


@csrf_exempt
@require_http_methods(["GET", "POST"])
def game_servers_api(request: HttpRequest) -> HttpResponse:
    try:
        if request.method == "GET":
            public_only = request.GET.get("public", "true").lower() != "false"
            queryset = GameServer.objects.filter(is_active=True)
            if public_only:
                queryset = queryset.filter(is_public=True)
            servers = [_serialize_server(server) for server in queryset]
            return JsonResponse({"success": True, "servers": servers})

        data = parse_request_body(request)
        required = ["id", "name", "api_url", "ws_url"]
        missing = [field for field in required if not data.get(field)]
        if missing:
            return json_error("missing fields: " + ", ".join(missing))

        server, _created = GameServer.objects.update_or_create(
            server_id=str(data.get("id")),
            defaults={
                "name": str(data.get("name")),
                "region": str(data.get("region") or "global"),
                "api_url": str(data.get("api_url")),
                "ws_url": str(data.get("ws_url")),
                "is_public": bool(data.get("is_public", True)),
                "is_active": bool(data.get("is_active", True)),
                "current_players": int(data.get("current_players", 0) or 0),
                "max_players": int(data.get("max_players", 64) or 64),
                "build_version": str(data.get("build_version") or ""),
            },
        )

        capacity = _get_or_create_capacity(server.server_id)
        if "current_rooms" in data:
            _apply_reported_current_rooms(capacity, data.get("current_rooms", capacity.current_rooms))

        return JsonResponse({"success": True, "server": _serialize_server(server)})
    except (OperationalError, ProgrammingError):
        return JsonResponse(
            {
                "error": "database_unavailable",
                "message": "Game server registry is not ready. Run migrations.",
            },
            status=503,
        )


@csrf_exempt
@require_http_methods(["POST"])
def game_server_heartbeat_api(request: HttpRequest, server_id: str) -> HttpResponse:
    try:
        data = parse_request_body(request)
        try:
            server = GameServer.objects.get(server_id=server_id)
        except GameServer.DoesNotExist:
            return json_error("server not found", status=404)

        if "current_players" in data:
            server.current_players = int(data.get("current_players", 0) or 0)
        if "max_players" in data:
            server.max_players = int(data.get("max_players", server.max_players) or server.max_players)
        if "is_active" in data:
            server.is_active = bool(data.get("is_active", True))

        server.last_heartbeat = timezone.now()
        server.save(update_fields=["current_players", "max_players", "is_active", "last_heartbeat"])

        capacity = _get_or_create_capacity(server.server_id)
        if "current_rooms" in data:
            _apply_reported_current_rooms(capacity, data.get("current_rooms", capacity.current_rooms))

        return JsonResponse({"success": True, "server": _serialize_server(server)})
    except (OperationalError, ProgrammingError):
        return JsonResponse(
            {
                "error": "database_unavailable",
                "message": "Game server registry is not ready. Run migrations.",
            },
            status=503,
        )
