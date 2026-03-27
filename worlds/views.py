import json
import logging
import os
from datetime import UTC, datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import GameServer, RuntimeConfig, World


logger = logging.getLogger(__name__)
JWT_SECRET = settings.JWT_SECRET
JWT_EXPIRATION_DAYS = settings.JWT_EXPIRATION_DAYS

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


def _json_error(message: str, status: int = 400) -> JsonResponse:
	return JsonResponse({"error": message}, status=status)


def _get_bearer_token(request: HttpRequest) -> str | None:
	auth_header = request.headers.get("Authorization", "")
	if not auth_header.startswith("Bearer "):
		return None
	return auth_header.split(" ", 1)[1].strip()


def _decode_access_token(token: str) -> dict | None:
	try:
		decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
		if isinstance(decoded, dict):
			return decoded
	except Exception:
		return None
	return None


def _build_access_token(user: User) -> str:
	display_name = user.first_name.strip() if user.first_name else user.username
	payload = {
		"userId": user.id,
		"username": user.username,
		"display_name": display_name,
		"exp": datetime.now(UTC) + timedelta(days=JWT_EXPIRATION_DAYS),
	}
	return str(jwt.encode(payload, JWT_SECRET, algorithm="HS256"))


def _serialize_user(user: User) -> dict:
	display_name = user.first_name.strip() if user.first_name else user.username
	return {
		"id": user.id,
		"username": user.username,
		"email": user.email,
		"display_name": display_name,
	}


def _parse_request_body(request: HttpRequest) -> dict:
	"""Accept JSON or form-encoded bodies; fall back to empty dict."""
	# If form-encoded or multipart, Django parses into POST already.
	if request.POST:
		return request.POST.dict()

	if not request.body:
		return {}

	try:
		return json.loads(request.body.decode("utf-8"))
	except json.JSONDecodeError:
		return {}


def _extract_tbw_metadata(tbw: str) -> dict:
	"""Parse the TBW text for known metadata fields the game expects."""
	meta = {}
	for raw_line in tbw.splitlines():
		line = raw_line.strip()
		if ";" not in line:
			continue
		key, value = line.split(";", 1)
		key = key.strip().lower()
		value = value.strip()
		if key in {"author", "version", "image"} and value:
			meta[key] = value
		# Stop early if we already found everything.
		if len(meta) == 3:
			break
	return meta


def _load_runtime_public_config() -> dict[str, str]:
	values = dict(DEFAULT_PUBLIC_CLIENT_CONFIG)
	for row in RuntimeConfig.objects.filter(is_public=True):
		values[row.key] = row.value
	return values


@csrf_exempt
@require_http_methods(["GET"])
def client_config_api(request: HttpRequest) -> HttpResponse:
	config_values = _load_runtime_public_config()

	# If node endpoints are not explicitly set in RuntimeConfig,
	# derive them from the most recently active public game server.
	if config_values.get("node_api_base_url", "").strip() == "" or config_values.get("node_ws_url", "").strip() == "":
		active_server = (
			GameServer.objects.filter(is_active=True, is_public=True)
			.order_by("-last_heartbeat")
			.first()
		)
		if active_server is not None:
			config_values["node_api_base_url"] = active_server.api_url
			config_values["node_ws_url"] = active_server.ws_url
			config_values["selected_server_id"] = active_server.server_id

	return JsonResponse({"success": True, "config": config_values})


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "PATCH", "DELETE"])
def worlds_api(request: HttpRequest) -> HttpResponse:
	# GET / - list worlds
	if request.method == "GET":
		world_id = request.GET.get("id")
		report_id = request.GET.get("report")

		if world_id:
			try:
				world = World.objects.get(pk=world_id)
			except World.DoesNotExist:
				return _json_error("world not found", status=404)

			world.downloads += 1
			world.save(update_fields=["downloads"])
			return JsonResponse({"tbw": world.tbw})

		if report_id:
			try:
				world = World.objects.get(pk=report_id)
			except World.DoesNotExist:
				return _json_error("world not found", status=404)

			world.reports += 1
			world.save(update_fields=["reports"])
			return HttpResponse("OK")

		worlds = [world.to_public_dict() for world in World.objects.all()]
		return JsonResponse(worlds, safe=False)

	# POST / - upload a world
	if request.method == "POST":
		data = _parse_request_body(request)
		name = data.get("name")
		tbw = data.get("tbw")
		if not name or not tbw:
			return _json_error("name and tbw are required")

		tbw_meta = _extract_tbw_metadata(tbw)

		world = World.objects.create(
			name=name,
			tbw=tbw,
			featured=bool(data.get("featured", False)),
			version=str(data.get("version") or tbw_meta.get("version") or "0"),
			author=str(data.get("author") or tbw_meta.get("author") or "unknown"),
			image=str(data.get("image") or tbw_meta.get("image") or ""),
		)
		# Log to console so uploads are visible in runserver output.
		logger.info("World uploaded", extra={"world_id": world.pk, "name": world.name, "author": world.author})
		return HttpResponse("OK")

	# PUT/PATCH /?id=X - update a world
	if request.method in {"PUT", "PATCH"}:
		world_id = request.GET.get("id")
		if not world_id:
			return _json_error("id is required for update")
		try:
			world = World.objects.get(pk=world_id)
		except World.DoesNotExist:
			return _json_error("world not found", status=404)

		data = _parse_request_body(request)
		for field in ["name", "tbw", "version", "author", "image"]:
			if field in data:
				setattr(world, field, data[field])
		if "featured" in data:
			world.featured = bool(data["featured"])
		world.save()
		return HttpResponse("OK")

	# DELETE /?id=X - remove a world
	if request.method == "DELETE":
		world_id = request.GET.get("id")
		if not world_id:
			return _json_error("id is required for delete")
		try:
			world = World.objects.get(pk=world_id)
		except World.DoesNotExist:
			return _json_error("world not found", status=404)
		world.delete()
		return HttpResponse("OK")

	return _json_error("method not allowed", status=405)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def game_servers_api(request: HttpRequest) -> HttpResponse:
	if request.method == "GET":
		public_only = request.GET.get("public", "true").lower() != "false"
		queryset = GameServer.objects.filter(is_active=True)
		if public_only:
			queryset = queryset.filter(is_public=True)
		servers = [server.to_public_dict() for server in queryset]
		return JsonResponse({"success": True, "servers": servers})

	data = _parse_request_body(request)
	required = ["id", "name", "api_url", "ws_url"]
	missing = [field for field in required if not data.get(field)]
	if missing:
		return _json_error("missing fields: " + ", ".join(missing))

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


@csrf_exempt
@require_http_methods(["POST"])
def game_server_heartbeat_api(request: HttpRequest, server_id: str) -> HttpResponse:
	data = _parse_request_body(request)
	try:
		server = GameServer.objects.get(server_id=server_id)
	except GameServer.DoesNotExist:
		return _json_error("server not found", status=404)

	if "current_players" in data:
		server.current_players = int(data.get("current_players", 0) or 0)
	if "max_players" in data:
		server.max_players = int(data.get("max_players", server.max_players) or server.max_players)
	if "is_active" in data:
		server.is_active = bool(data.get("is_active", True))

	server.last_heartbeat = timezone.now()
	server.save()
	return JsonResponse({"success": True, "server": server.to_public_dict()})


@csrf_exempt
@require_http_methods(["POST"])
def auth_register_api(request: HttpRequest) -> HttpResponse:
	data = _parse_request_body(request)
	username = str(data.get("username", "")).strip()
	email = str(data.get("email", "")).strip().lower()
	password = str(data.get("password", ""))

	if len(username) < 3 or len(username) > 20:
		return _json_error("Username must be 3-20 characters", status=400)
	if not username.replace("_", "a").isalnum():
		return _json_error("Username format is invalid", status=400)
	if "@" not in email or "." not in email:
		return _json_error("Email format is invalid", status=400)
	if len(password) < 8:
		return _json_error("Password must be at least 8 characters", status=400)

	if User.objects.filter(username=username).exists():
		return _json_error("Username already taken", status=409)
	if User.objects.filter(email=email).exists():
		return _json_error("Email already registered", status=409)

	user = User.objects.create(
		username=username,
		email=email,
		password=make_password(password),
		first_name=username,
	)
	token = _build_access_token(user)

	return JsonResponse({"token": token, "user": _serialize_user(user)}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def auth_login_api(request: HttpRequest) -> HttpResponse:
	data = _parse_request_body(request)
	login_id = str(data.get("username", "")).strip()
	password = str(data.get("password", ""))

	if login_id == "" or password == "":
		return _json_error("Invalid credentials", status=401)

	user = User.objects.filter(username=login_id).first()
	if user is None:
		user = User.objects.filter(email=login_id.lower()).first()
	if user is None:
		return _json_error("Invalid credentials", status=401)

	if not check_password(password, user.password):
		return _json_error("Invalid credentials", status=401)

	user.last_login = timezone.now()
	user.save(update_fields=["last_login"])

	token = _build_access_token(user)
	return JsonResponse({"token": token, "user": _serialize_user(user)})


@csrf_exempt
@require_http_methods(["GET"])
def auth_verify_api(request: HttpRequest) -> HttpResponse:
	token = _get_bearer_token(request)
	if token is None:
		return JsonResponse({"valid": False, "error": "No token provided"}, status=401)

	decoded = _decode_access_token(token)
	if decoded is None:
		return JsonResponse({"valid": False, "error": "Invalid token"}, status=403)

	user_id = int(decoded.get("userId", 0) or 0)
	user = User.objects.filter(id=user_id).first()
	if user is None:
		return JsonResponse({"valid": False, "error": "User not found"}, status=404)

	return JsonResponse({"valid": True, "user": _serialize_user(user)})


@csrf_exempt
@require_http_methods(["PUT"])
def update_display_name_api(request: HttpRequest) -> HttpResponse:
	token = _get_bearer_token(request)
	if token is None:
		return _json_error("Authentication required", status=401)

	decoded = _decode_access_token(token)
	if decoded is None:
		return _json_error("Invalid token", status=403)

	user_id = int(decoded.get("userId", 0) or 0)
	user = User.objects.filter(id=user_id).first()
	if user is None:
		return _json_error("User not found", status=404)

	data = _parse_request_body(request)
	display_name = str(data.get("display_name", "")).strip()
	if display_name == "" or len(display_name) > 30:
		return _json_error("Display name must be 1-30 characters", status=400)

	user.first_name = display_name
	user.save(update_fields=["first_name"])
	return JsonResponse({"success": True, "user": _serialize_user(user)})

# Create your views here.
