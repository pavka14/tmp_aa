from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from infrastructure.models import Connection, Device, Interface, Site

# ---------------------------------------------------------------------------
# Proof-of-concept note on API-level validators
# ---------------------------------------------------------------------------
# The validators below show how DRF serializers can enforce rules *additional*
# to (or *stricter* than) model-level constraints.  Here, Site.name has a
# model-level max_length of 64 characters, but the API enforces a stricter
# window of 4–40 characters.  This demonstrates the layered validation
# approach: models guard database integrity, serializers shape the API contract.
# ---------------------------------------------------------------------------

SITE_NAME_MIN_LENGTH = 4
SITE_NAME_MAX_LENGTH = 40


# ---------------------------------------------------------------------------
# Minimal reference serializers (used inside nested connection targets)
# ---------------------------------------------------------------------------


class SiteRefSerializer(serializers.Serializer):
    """Compact site reference: id + name only."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class DeviceRefSerializer(serializers.Serializer):
    """Compact device reference: id + name only."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class InterfaceRefSerializer(serializers.Serializer):
    """Compact interface reference: id + name only."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


# ---------------------------------------------------------------------------
# Full CRUD serializers
# ---------------------------------------------------------------------------


class SiteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Site model.

    Applies API-level name length constraints (min 4, max 40) that are stricter
    than the underlying model field (max 64).  This is a proof-of-concept
    demonstration of how the API can impose additional validation on top of
    model-level constraints.
    """

    name = serializers.CharField(
        min_length=SITE_NAME_MIN_LENGTH,
        max_length=SITE_NAME_MAX_LENGTH,
    )

    class Meta:
        model = Site
        fields = ["id", "name", "description", "status", "active"]
        read_only_fields = ["active"]


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for the Device model."""

    class Meta:
        model = Device
        fields = ["id", "name", "site", "serial_number", "active"]
        read_only_fields = ["active"]


class InterfaceSerializer(serializers.ModelSerializer):
    """Serializer for the Interface model."""

    class Meta:
        model = Interface
        fields = ["id", "name", "device", "active"]
        read_only_fields = ["active"]


class ConnectionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Connection model.

    Cross-field validation (device ↔ site, interface ↔ device) is delegated to
    the model's ``clean()`` method to avoid duplicating business logic.
    """

    class Meta:
        model = Connection
        fields = [
            "id",
            "connection_id",
            "name",
            "status",
            "start_site",
            "start_device",
            "start_interface",
            "end_site",
            "end_device",
            "end_interface",
            "active",
        ]
        read_only_fields = ["active"]

    def validate(self, attrs):
        if self.instance:
            # For partial/full updates: build a merged view of existing + new data.
            merged = {}
            for field in Connection._meta.fields:
                if field.primary_key:
                    continue
                merged[field.attname] = getattr(self.instance, field.attname)
            # Overwrite with submitted FK values (DRF uses field.name → object).
            for attr_name, value in attrs.items():
                merged[attr_name] = value
            temp = Connection(**merged)
        else:
            temp = Connection(**attrs)

        try:
            temp.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs


# ---------------------------------------------------------------------------
# Traced-connections response serializers (read-only)
# ---------------------------------------------------------------------------


class ConnectionEndpointSerializer(serializers.Serializer):
    """
    Nested representation of one end of a connection.

    Each optional FK (device, interface) is rendered as a compact {id, name}
    object and omitted from the output when null.
    """

    site = SiteRefSerializer()
    device = DeviceRefSerializer(allow_null=True)
    interface = InterfaceRefSerializer(allow_null=True)


class TracedConnectionSerializer(serializers.ModelSerializer):
    """
    Connection representation used by the traced-connections endpoint.

    Renders start/end endpoints as nested objects rather than raw FK ids.
    """

    start_target = serializers.SerializerMethodField()
    end_target = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = [
            "id",
            "connection_id",
            "name",
            "status",
            "start_target",
            "end_target",
        ]

    @extend_schema_field(ConnectionEndpointSerializer)
    def get_start_target(self, obj):
        return self._build_target(obj.start_site, obj.start_device, obj.start_interface)

    @extend_schema_field(ConnectionEndpointSerializer)
    def get_end_target(self, obj):
        return self._build_target(obj.end_site, obj.end_device, obj.end_interface)

    @staticmethod
    def _build_target(site, device, interface):
        target = {}
        if site:
            target["site"] = {"id": site.id, "name": site.name}
        if device:
            target["device"] = {"id": device.id, "name": device.name}
        if interface:
            target["interface"] = {"id": interface.id, "name": interface.name}
        return target


class TracedObjectSerializer(serializers.Serializer):
    """
    Top-level response envelope for the traced-connections endpoint.

    traced_object — the entity used as the query entry point.
    connections_count — total number of matching connections.
    connections — list of matching Connection objects.
    """

    traced_object = serializers.DictField()
    connections_count = serializers.IntegerField()
    connections = TracedConnectionSerializer(many=True)
