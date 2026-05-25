from django.contrib import admin

from infrastructure.models import Connection, Device, Interface, Site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'active', 'time_deleted')
    search_fields = ('name',)
    list_filter = ('status', 'active')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'serial_number', 'active', 'time_deleted')
    search_fields = ('name', 'serial_number')
    list_filter = ('active',)


@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'active', 'time_deleted')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('connection_id', 'name', 'status', 'active', 'time_deleted')
    search_fields = ('connection_id', 'name')
    list_filter = ('status', 'active')

# Register your models here.
