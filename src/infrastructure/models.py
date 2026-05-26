from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    def with_deleted(self):
        return super().get_queryset()


class SoftDeleteModel(models.Model):
    time_deleted = models.DateTimeField(null=True, blank=True, default=None)
    active = models.BooleanField(default=True, db_index=True)

    all_objects = models.Manager()
    objects = ActiveManager()

    class Meta:
        abstract = True
        base_manager_name = "all_objects"
        default_manager_name = "objects"

    def delete(self, using=None, keep_parents=False):
        if not self.active:
            return 0, {self._meta.label: 0}
        self.active = False
        self.time_deleted = timezone.now()
        self.save(update_fields=["active", "time_deleted"])
        return 1, {self._meta.label: 1}


class Site(SoftDeleteModel):
    SITE_STATUS_ACTIVE = "Active"
    SITE_STATUS_PLANNED = "Planned"
    SITE_STATUS_DECOMMISSIONED = "Decommissioned"

    name = models.CharField(max_length=64, null=False, blank=False)
    description = models.TextField(default="", blank=True)
    status = models.CharField(max_length=32, default=SITE_STATUS_PLANNED, db_index=True)

    class Meta:
        verbose_name = "site"
        verbose_name_plural = "sites"
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=Q(active=True),
                name="uniq_active_site_name",
            ),
            models.CheckConstraint(
                condition=Q(
                    status__in=[
                        "Active",
                        "Planned",
                        "Decommissioned",
                    ]
                ),
                name="site_status_allowed_values",
            ),
        ]

    def __str__(self):
        return self.name


class Device(SoftDeleteModel):
    name = models.CharField(max_length=64, null=False, blank=False)
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name="devices")
    serial_number = models.CharField(max_length=256, null=False, blank=False)

    class Meta:
        verbose_name = "device"
        verbose_name_plural = "devices"
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=Q(active=True),
                name="uniq_active_device_name",
            ),
            models.UniqueConstraint(
                fields=["serial_number"],
                condition=Q(active=True),
                name="uniq_active_device_serial_number",
            ),
        ]

    def __str__(self):
        return self.name


class Interface(SoftDeleteModel):
    INTERFACE_STATUS_UP = "Up"
    INTERFACE_STATUS_DOWN = "Down"
    INTERFACE_STATUS_MAINTENANCE = "Maintenance"

    name = models.CharField(max_length=64, null=False, blank=False)
    device = models.ForeignKey(
        Device, on_delete=models.PROTECT, related_name="interfaces"
    )
    speed = models.PositiveIntegerField(
        verbose_name="throughput in Mbps", null=True, blank=True, default=None
    )
    status = models.CharField(max_length=32, default=INTERFACE_STATUS_UP, db_index=True)

    class Meta:
        verbose_name = "interface"
        verbose_name_plural = "interfaces"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "name"],
                condition=Q(active=True),
                name="uniq_active_interface_device_name",
            ),
            models.CheckConstraint(
                condition=Q(
                    status__in=[
                        "Up",
                        "Down",
                        "Maintenance",
                    ]
                ),
                name="interface_status_allowed_values",
            ),
        ]

    def __str__(self):
        return f"{self.device.name} / {self.name}"


class Connection(SoftDeleteModel):
    CONNECTION_STATUS_CONNECTED = "Connected"
    CONNECTION_STATUS_DISCONNECTED = "Disconnected"

    connection_id = models.CharField(max_length=64, null=False, blank=False)
    name = models.CharField(max_length=64, blank=True, default="")
    status = models.CharField(
        max_length=32, default=CONNECTION_STATUS_DISCONNECTED, db_index=True
    )
    start_site = models.ForeignKey(
        Site, on_delete=models.PROTECT, related_name="connections_starting_here"
    )
    start_device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="connections_starting_here",
        null=True,
        blank=True,
    )
    start_interface = models.ForeignKey(
        Interface,
        on_delete=models.PROTECT,
        related_name="connections_starting_here",
        null=True,
        blank=True,
    )
    end_site = models.ForeignKey(
        Site, on_delete=models.PROTECT, related_name="connections_ending_here"
    )
    end_device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="connections_ending_here",
        null=True,
        blank=True,
    )
    end_interface = models.ForeignKey(
        Interface,
        on_delete=models.PROTECT,
        related_name="connections_ending_here",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "connection"
        verbose_name_plural = "connections"
        constraints = [
            models.UniqueConstraint(
                fields=["connection_id"],
                condition=Q(active=True),
                name="uniq_active_connection_connection_id",
            ),
            models.CheckConstraint(
                condition=Q(
                    status__in=[
                        "Connected",
                        "Disconnected",
                    ]
                ),
                name="connection_status_allowed_values",
            ),
        ]

    def clean(self):
        errors = {}

        for endpoint in ("start", "end"):
            site = getattr(self, f"{endpoint}_site")
            device = getattr(self, f"{endpoint}_device")
            interface = getattr(self, f"{endpoint}_interface")

            if site and device and device.site_id != site.id:
                errors[f"{endpoint}_device"] = (
                    f"{endpoint.title()} device must belong to the selected site."
                )
            if interface and not device:
                errors[f"{endpoint}_interface"] = (
                    f"{endpoint.title()} interface requires a {endpoint} device."
                )
            if interface and device and interface.device_id != device.id:
                errors[f"{endpoint}_interface"] = (
                    f"{endpoint.title()} interface must belong to the selected device."
                )
            if site and interface and interface.device.site_id != site.id:
                errors[f"{endpoint}_interface"] = (
                    f"{endpoint.title()} interface must belong to the selected site."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.connection_id
