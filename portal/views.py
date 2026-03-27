from django.shortcuts import render


API_GROUPS = {
    "auth": [
        {"method": "POST", "path": "/api/auth/register", "description": "Register a new account"},
        {"method": "POST", "path": "/api/auth/login", "description": "Login and receive JWT"},
        {"method": "GET", "path": "/api/auth/verify", "description": "Verify JWT token"},
    ],
    "users": [
        {"method": "PUT", "path": "/api/users/display-name", "description": "Update current user display name"},
    ],
    "worlds": [
        {"method": "GET", "path": "/api/worlds", "description": "List worlds or fetch by query params"},
        {"method": "POST", "path": "/api/worlds", "description": "Create a world"},
        {"method": "PUT", "path": "/api/worlds?id=<id>", "description": "Update world fields"},
        {"method": "DELETE", "path": "/api/worlds?id=<id>", "description": "Delete a world"},
        {"method": "GET", "path": "/api/worlds?report=<id>", "description": "Report a world"},
    ],
    "servers": [
        {"method": "GET", "path": "/api/game-servers", "description": "List active game servers"},
        {"method": "POST", "path": "/api/game-servers", "description": "Register or update a game server"},
        {"method": "POST", "path": "/api/game-servers/<id>/heartbeat", "description": "Heartbeat update"},
    ],
    "config": [
        {"method": "GET", "path": "/api/client-config", "description": "Fetch runtime client configuration"},
    ],
}


def dashboard(request):
    return render(request, "portal/dashboard.html", {"api_groups": API_GROUPS})


def auth_page(request):
    return render(request, "portal/auth.html", {"api_list": API_GROUPS["auth"]})


def users_page(request):
    return render(request, "portal/users.html", {"api_list": API_GROUPS["users"]})


def worlds_page(request):
    return render(request, "portal/worlds.html", {"api_list": API_GROUPS["worlds"]})


def servers_page(request):
    return render(request, "portal/servers.html", {"api_list": API_GROUPS["servers"]})


def config_page(request):
    return render(request, "portal/config.html", {"api_list": API_GROUPS["config"]})
