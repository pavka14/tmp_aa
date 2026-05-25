from django.contrib import admin

from infrastructure.models import Connection, Device, Interface, Site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "active", "time_deleted")
    search_fields = ("name",)
    list_filter = ("status", "active")

    def get_queryset(self, request):
        return self.model.objects.with_deleted()


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "site", "serial_number", "active", "time_deleted")
    search_fields = ("name", "serial_number")
    list_filter = ("active",)
    raw_id_fields = ("site",)

    def get_queryset(self, request):
        return self.model.objects.with_deleted()


@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = ("name", "device", "active", "time_deleted")
    search_fields = ("name",)
    list_filter = ("active",)
    raw_id_fields = ("device",)

    def get_queryset(self, request):
        return self.model.objects.with_deleted()


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ("connection_id", "name", "status", "active", "time_deleted")
    raw_id_fields = (
        "start_site",
        "start_device",
        "start_interface",
        "end_site",
        "end_device",
        "end_interface",
    )
    list_filter = ("status", "active")

    def get_queryset(self, request):
        return self.model.objects.with_deleted()
