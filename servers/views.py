from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.helpers import json_error, parse_request_body
from servers.models import GameServer


@csrf_exempt
@require_http_methods(["GET", "POST"])
def game_servers_api(request: HttpRequest) -> HttpResponse:
    try:
        if request.method == "GET":
            public_only = request.GET.get("public", "true").lower() != "false"
            queryset = GameServer.objects.filter(is_active=True)
            if public_only:
                queryset = queryset.filter(is_public=True)
            servers = [server.to_public_dict() for server in queryset]
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
        return JsonResponse({"success": True, "server": server.to_public_dict()})
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
        server.save()
        return JsonResponse({"success": True, "server": server.to_public_dict()})
    except (OperationalError, ProgrammingError):
        return JsonResponse(
            {
                "error": "database_unavailable",
                "message": "Game server registry is not ready. Run migrations.",
            },
            status=503,
        )
