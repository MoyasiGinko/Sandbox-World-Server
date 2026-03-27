import logging

from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.helpers import json_error, parse_request_body
from worlds.models import World


logger = logging.getLogger(__name__)


def _extract_tbw_metadata(tbw: str) -> dict:
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
        if len(meta) == 3:
            break
    return meta


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "PATCH", "DELETE"])
def worlds_api(request: HttpRequest) -> HttpResponse:
    try:
        if request.method == "GET":
            world_id = request.GET.get("id")
            report_id = request.GET.get("report")

            if world_id:
                try:
                    world = World.objects.get(pk=world_id)
                except World.DoesNotExist:
                    return json_error("world not found", status=404)

                world.downloads += 1
                world.save(update_fields=["downloads"])
                return JsonResponse({"tbw": world.tbw})

            if report_id:
                try:
                    world = World.objects.get(pk=report_id)
                except World.DoesNotExist:
                    return json_error("world not found", status=404)

                world.reports += 1
                world.save(update_fields=["reports"])
                return HttpResponse("OK")

            worlds = [world.to_public_dict() for world in World.objects.all()]
            return JsonResponse(worlds, safe=False)

        if request.method == "POST":
            data = parse_request_body(request)
            name = data.get("name")
            tbw = data.get("tbw")
            if not name or not tbw:
                return json_error("name and tbw are required")

            tbw_meta = _extract_tbw_metadata(str(tbw))
            world = World.objects.create(
                name=name,
                tbw=tbw,
                featured=bool(data.get("featured", False)),
                version=str(data.get("version") or tbw_meta.get("version") or "0"),
                author=str(data.get("author") or tbw_meta.get("author") or "unknown"),
                image=str(data.get("image") or tbw_meta.get("image") or ""),
            )
            logger.info(
                "World uploaded",
                extra={"world_id": world.pk, "name": world.name, "author": world.author},
            )
            return HttpResponse("OK")

        if request.method in {"PUT", "PATCH"}:
            world_id = request.GET.get("id")
            if not world_id:
                return json_error("id is required for update")
            try:
                world = World.objects.get(pk=world_id)
            except World.DoesNotExist:
                return json_error("world not found", status=404)

            data = parse_request_body(request)
            for field in ["name", "tbw", "version", "author", "image"]:
                if field in data:
                    setattr(world, field, data[field])
            if "featured" in data:
                world.featured = bool(data["featured"])
            world.save()
            return HttpResponse("OK")

        if request.method == "DELETE":
            world_id = request.GET.get("id")
            if not world_id:
                return json_error("id is required for delete")
            try:
                world = World.objects.get(pk=world_id)
            except World.DoesNotExist:
                return json_error("world not found", status=404)
            world.delete()
            return HttpResponse("OK")

        return json_error("method not allowed", status=405)
    except (OperationalError, ProgrammingError):
        return JsonResponse(
            {
                "error": "database_unavailable",
                "message": "World database is not ready. Run migrations.",
            },
            status=503,
        )
