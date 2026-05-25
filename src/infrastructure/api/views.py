from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from infrastructure.models import Connection, Device, Interface, Site

from .permissions import IsSuperUserOrReadOnly
from .serializers import (
    ConnectionSerializer,
    DeviceSerializer,
    InterfaceSerializer,
    SiteSerializer,
    TracedConnectionSerializer,
    TracedObjectSerializer,
)


class SiteViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoint for Sites.

    list:   GET  /api/v1/sites/
    create: POST /api/v1/sites/
    read:   GET  /api/v1/sites/{id}/
    update: PUT  /api/v1/sites/{id}/
    partial_update: PATCH /api/v1/sites/{id}/
    delete: DELETE /api/v1/sites/{id}/  (soft-delete)

    Read operations are available to any authenticated user.
    Write operations are restricted to superusers.
    """

    queryset = Site.objects.order_by("pk")
    serializer_class = SiteSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class DeviceViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoint for Devices.

    Read operations are available to any authenticated user.
    Write operations are restricted to superusers.
    """

    queryset = Device.objects.select_related("site").order_by("pk")
    serializer_class = DeviceSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class InterfaceViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoint for Interfaces.

    Read operations are available to any authenticated user.
    Write operations are restricted to superusers.
    """

    queryset = Interface.objects.select_related("device__site").order_by("pk")
    serializer_class = InterfaceSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class ConnectionViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoint for Connections.

    Read operations are available to any authenticated user.
    Write operations are restricted to superusers.

    In addition to standard CRUD, a ``traced`` action is provided for listing
    all connections associated with a given site, device, or interface.
    """

    queryset = Connection.objects.select_related(
        "start_site",
        "start_device",
        "start_interface",
        "end_site",
        "end_device",
        "end_interface",
    ).order_by("pk")
    serializer_class = ConnectionSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="type",
                description="The type of the entry-point object: site, device, or interface.",
                required=True,
                type=str,
                enum=["site", "device", "interface"],
            ),
            OpenApiParameter(
                name="id",
                description="The primary-key id of the entry-point object.",
                required=True,
                type=int,
            ),
        ],
        responses={200: TracedObjectSerializer},
        summary="List all connections touching a site, device, or interface",
        description=(
            "Returns every active Connection where the given site, device, or "
            "interface appears on either the start or end endpoint.  "
            "Use ``type=site&id=<pk>`` to trace by site, ``type=device&id=<pk>`` "
            "for a device, or ``type=interface&id=<pk>`` for an interface."
        ),
    )
    @action(detail=False, methods=["get"], url_path="traced")
    def traced(self, request):
        """
        Return all connections touching the specified site, device, or interface.

        Query parameters:
        - ``type``: one of ``site``, ``device``, ``interface``
        - ``id``:   primary key of the target object
        """
        traced_type = request.query_params.get("type", "").lower()
        traced_id = request.query_params.get("id", "")

        valid_types = ("site", "device", "interface")
        if traced_type not in valid_types:
            return Response(
                {"detail": (f"'type' must be one of: {', '.join(valid_types)}.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not traced_id:
            return Response(
                {"detail": "'id' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            traced_id = int(traced_id)
        except ValueError:
            return Response(
                {"detail": "'id' must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if traced_id <= 0:
            return Response(
                {"detail": "'id' must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filter_map = {
            "site": Q(start_site_id=traced_id) | Q(end_site_id=traced_id),
            "device": Q(start_device_id=traced_id) | Q(end_device_id=traced_id),
            "interface": (
                Q(start_interface_id=traced_id) | Q(end_interface_id=traced_id)
            ),
        }

        # Resolve the entry-point object to produce a human-readable label.
        model_map = {"site": Site, "device": Device, "interface": Interface}
        model_cls = model_map[traced_type]
        try:
            traced_obj = model_cls.objects.get(pk=traced_id)
        except model_cls.DoesNotExist:
            return Response(
                {
                    "detail": f"{traced_type.capitalize()} with id={traced_id} not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        qs = Connection.objects.filter(filter_map[traced_type]).select_related(
            "start_site",
            "start_device",
            "start_interface",
            "end_site",
            "end_device",
            "end_interface",
        )

        connections = list(qs)
        data = {
            "traced_object": {
                "type": traced_type,
                "id": traced_obj.pk,
                "name": str(traced_obj),
            },
            "connections_count": len(connections),
            "connections": TracedConnectionSerializer(connections, many=True).data,
        }
        return Response(data)
