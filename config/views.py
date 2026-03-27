from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.models import RuntimeConfig
from servers.models import GameServer


DEFAULT_PUBLIC_CLIENT_CONFIG = {
    "django_base_url": settings.PUBLIC_DJANGO_BASE_URL,
    "django_api_base_url": settings.PUBLIC_DJANGO_API_BASE_URL,
    "node_api_base_url": settings.DEFAULT_NODE_API_BASE_URL,
    "node_ws_url": settings.DEFAULT_NODE_WS_URL,
    "world_database_repo": settings.DEFAULT_WORLD_DATABASE_REPO,
    "legacy_server_list_url": settings.DEFAULT_SERVER_LIST_URL,
    "update_release_api_url": settings.DEFAULT_UPDATE_RELEASE_API_URL,
    "update_release_page_url": settings.DEFAULT_UPDATE_RELEASE_PAGE_URL,
}


def _load_runtime_public_config() -> dict[str, str]:
    values = dict(DEFAULT_PUBLIC_CLIENT_CONFIG)
    try:
        for row in RuntimeConfig.objects.filter(is_public=True):
            values[row.key] = row.value
    except (OperationalError, ProgrammingError):
        return values
    return values


@csrf_exempt
@require_http_methods(["GET"])
def client_config_api(request: HttpRequest) -> HttpResponse:
    config_values = _load_runtime_public_config()

    if config_values.get("node_api_base_url", "").strip() == "" or config_values.get("node_ws_url", "").strip() == "":
        try:
            active_server = (
                GameServer.objects.filter(is_active=True, is_public=True)
                .order_by("-last_heartbeat")
                .first()
            )
        except (OperationalError, ProgrammingError):
            active_server = None

        if active_server is not None:
            config_values["node_api_base_url"] = active_server.api_url
            config_values["node_ws_url"] = active_server.ws_url
            config_values["selected_server_id"] = active_server.server_id

    return JsonResponse({"success": True, "config": config_values})
