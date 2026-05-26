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

    ``url`` is a self-link to the record's detail endpoint and is rendered as
    a clickable hyperlink in the DRF browsable API.
    """

    url = serializers.HyperlinkedIdentityField(view_name="site-detail")
    name = serializers.CharField(
        min_length=SITE_NAME_MIN_LENGTH,
        max_length=SITE_NAME_MAX_LENGTH,
    )

    class Meta:
        model = Site
        fields = [
            "url",
            "id",
            "name",
            "description",
            "status",
            "active",
            "time_deleted",
        ]
        read_only_fields = ["id", "active", "time_deleted"]


class DeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Device model.

    ``url`` is a self-link to the record's detail endpoint.
    """

    url = serializers.HyperlinkedIdentityField(view_name="device-detail")

    class Meta:
        model = Device
        fields = [
            "url",
            "id",
            "name",
            "site",
            "serial_number",
            "active",
            "time_deleted",
        ]
        read_only_fields = ["id", "active", "time_deleted"]


class InterfaceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Interface model.

    ``url`` is a self-link to the record's detail endpoint.
    """

    url = serializers.HyperlinkedIdentityField(view_name="interface-detail")

    class Meta:
        model = Interface
        fields = [
            "url",
            "id",
            "name",
            "device",
            "speed",
            "status",
            "active",
            "time_deleted",
        ]
        read_only_fields = ["id", "active", "time_deleted"]


# ---------------------------------------------------------------------------
# Connection endpoint nested input/output
# ---------------------------------------------------------------------------


class ConnectionEndpointInputSerializer(serializers.Serializer):
    """
    Nested input for one end of a connection.

    ``site`` is required.  ``device`` and ``interface`` are optional but must
    follow the site → device → interface hierarchy enforced by the model's
    ``clean()`` method.

    All three FK values are resolved against the *active* record set: attempts
    to reference a soft-deleted site, device, or interface will be rejected with
    a 400 error.  This is automatic because the default manager (``ActiveManager``)
    filters to ``active=True`` and PrimaryKeyRelatedField uses it for lookups.
    """

    site = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all())
    device = serializers.PrimaryKeyRelatedField(
        queryset=Device.objects.all(), required=False, allow_null=True, default=None
    )
    interface = serializers.PrimaryKeyRelatedField(
        queryset=Interface.objects.all(), required=False, allow_null=True, default=None
    )


class ConnectionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Connection model.

    **Creating and updating connections**

    Payloads must supply the complete endpoint tuple via ``start`` and ``end``
    nested objects rather than flat FK fields::

        {
            "connection_id": "CONN-001",
            "status": "Connected",
            "start": {"site": 1, "device": 2, "interface": 3},
            "end":   {"site": 4, "device": 5, "interface": 6}
        }

    Each nested object is validated by ``ConnectionEndpointInputSerializer``,
    which rejects references to soft-deleted records automatically.  Cross-field
    integrity (device belongs to the given site, interface belongs to the given
    device) is then delegated to the model's ``clean()`` method so validation
    logic is not duplicated in the serializer.

    **Partial updates (PATCH)**

    When processing a PATCH request, any top-level field omitted from the
    payload keeps its current value on the instance.  For the ``start`` and
    ``end`` nested objects this means: if a PATCH payload supplies only ``start``,
    the ``end`` endpoint is taken unchanged from the existing record before
    model-level cross-field validation runs.  This lets callers update a single
    endpoint without re-supplying the other.  The full six-field state is always
    validated by ``clean()`` after merging, so partial payloads cannot create
    inconsistent records.

    This behaviour is intentional but noteworthy: a partial-update payload
    represents a *delta* against the current state, not the complete new state.
    See the Limitations section in the PRD for the corresponding trade-off note.

    ``url`` is a self-link to the record's detail endpoint.
    """

    url = serializers.HyperlinkedIdentityField(view_name="connection-detail")
    start = ConnectionEndpointInputSerializer(write_only=True)
    end = ConnectionEndpointInputSerializer(write_only=True)

    class Meta:
        model = Connection
        fields = [
            "url",
            "id",
            "connection_id",
            "name",
            "status",
            "start",
            "end",
            "active",
            "time_deleted",
        ]
        read_only_fields = ["id", "active", "time_deleted"]

    def to_representation(self, instance: Connection) -> dict:
        ret = super().to_representation(instance)
        ret["start"] = {
            "site": instance.start_site_id,
            "device": instance.start_device_id,
            "interface": instance.start_interface_id,
        }
        ret["end"] = {
            "site": instance.end_site_id,
            "device": instance.end_device_id,
            "interface": instance.end_interface_id,
        }
        return ret

    def validate(self, attrs: dict) -> dict:
        """
        Run model-level cross-field validation.

        Builds a temporary Connection object to call ``model.clean()`` so that
        device ↔ site and interface ↔ device consistency is checked without
        duplicating validation rules.  For partial updates the current instance
        state is merged with the incoming delta first.
        """

        def _endpoint_kwargs(prefix: str, endpoint: dict) -> dict:
            return {
                f"{prefix}_site": endpoint.get("site"),
                f"{prefix}_device": endpoint.get("device"),
                f"{prefix}_interface": endpoint.get("interface"),
            }

        if self.instance:
            merged = {
                "start_site": self.instance.start_site,
                "start_device": self.instance.start_device,
                "start_interface": self.instance.start_interface,
                "end_site": self.instance.end_site,
                "end_device": self.instance.end_device,
                "end_interface": self.instance.end_interface,
                "connection_id": self.instance.connection_id,
                "name": self.instance.name,
                "status": self.instance.status,
            }
            for prefix in ("start", "end"):
                if prefix in attrs:
                    merged.update(_endpoint_kwargs(prefix, attrs[prefix]))
            for key in ("connection_id", "name", "status"):
                if key in attrs:
                    merged[key] = attrs[key]
            temp = Connection(**merged)
        else:
            flat: dict = {}
            for prefix in ("start", "end"):
                flat.update(_endpoint_kwargs(prefix, attrs.get(prefix, {})))
            for key in ("connection_id", "name", "status"):
                if key in attrs:
                    flat[key] = attrs[key]
            temp = Connection(**flat)

        try:
            temp.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs

    def create(self, validated_data: dict) -> Connection:
        flat: dict = {}
        for prefix in ("start", "end"):
            endpoint = validated_data.pop(prefix, {})
            flat[f"{prefix}_site"] = endpoint.get("site")
            flat[f"{prefix}_device"] = endpoint.get("device")
            flat[f"{prefix}_interface"] = endpoint.get("interface")
        flat.update(validated_data)
        return Connection.objects.create(**flat)

    def update(self, instance: Connection, validated_data: dict) -> Connection:
        for prefix in ("start", "end"):
            endpoint = validated_data.pop(prefix, None)
            if endpoint is not None:
                setattr(instance, f"{prefix}_site", endpoint.get("site"))
                setattr(instance, f"{prefix}_device", endpoint.get("device"))
                setattr(instance, f"{prefix}_interface", endpoint.get("interface"))
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ---------------------------------------------------------------------------
# Traced-connections response serializers (read-only)
# ---------------------------------------------------------------------------


class ConnectionEndpointSerializer(serializers.Serializer):
    """
    Nested representation of one end of a connection.

    ``site`` is always present.  ``device`` and ``interface`` are optional —
    they are omitted from the response when the connection endpoint only
    specifies a site.  Marking them ``required=False`` here keeps the
    generated OpenAPI schema accurate for clients.
    """

    site = SiteRefSerializer()
    device = DeviceRefSerializer(required=False)
    interface = InterfaceRefSerializer(required=False)


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
