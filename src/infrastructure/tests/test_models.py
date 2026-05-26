from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from infrastructure.models import Connection, Device, Interface, Site


class TestSiteModel(TestCase):
    def test_active_unique_name_with_soft_delete(self):
        first = Site.objects.create(name="Site 1")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Site.objects.create(name="Site 1")

        first.delete()

        second = Site.objects.create(name="Site 1")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Site.objects.create(name="Site 1")

        second.delete()
        second_with_deleted = Site.objects.with_deleted().get(pk=second.pk)
        self.assertFalse(second_with_deleted.active)

        third = Site.objects.create(name="Site 1")
        self.assertEqual(third.name, "Site 1")

    def test_manager_excludes_deleted_by_default(self):
        site = Site.objects.create(name="Site 1")
        site.delete()

        self.assertFalse(Site.objects.filter(pk=site.pk).exists())
        self.assertTrue(Site.objects.with_deleted().filter(pk=site.pk).exists())


class TestDeviceModel(TestCase):
    def test_active_unique_fields_with_soft_delete(self):
        site = Site.objects.create(name="Site 1")
        first = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Device.objects.create(name="Device 1", site=site, serial_number="sn-2")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Device.objects.create(name="Device 2", site=site, serial_number="sn-1")

        first.delete()
        Device.objects.create(name="Device 1", site=site, serial_number="sn-1")

    def test_manager_excludes_deleted_by_default(self):
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        device.delete()

        self.assertFalse(Device.objects.filter(pk=device.pk).exists())
        self.assertTrue(Device.objects.with_deleted().filter(pk=device.pk).exists())
        self.assertFalse(site.devices.filter(pk=device.pk).exists())

    def test_soft_deleted_object_can_be_edited_and_stays_deleted(self):
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        device.delete()

        device.name = "Device 1 updated"
        device.save()

        reloaded = Device.objects.with_deleted().get(pk=device.pk)
        self.assertEqual(reloaded.name, "Device 1 updated")
        self.assertFalse(reloaded.active)


class TestInterfaceModel(TestCase):
    def test_active_unique_name_per_device_with_soft_delete(self):
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        other_device = Device.objects.create(
            name="Device 2", site=site, serial_number="sn-2"
        )
        first = Interface.objects.create(name="eth0", device=device)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Interface.objects.create(name="eth0", device=device)

        Interface.objects.create(name="eth0", device=other_device)

        first.delete()
        recreated = Interface.objects.create(name="eth0", device=device)
        self.assertEqual(recreated.name, "eth0")

    def test_manager_excludes_deleted_by_default(self):
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        interface = Interface.objects.create(name="eth0", device=device)
        interface.delete()

        self.assertFalse(Interface.objects.filter(pk=interface.pk).exists())
        self.assertTrue(
            Interface.objects.with_deleted().filter(pk=interface.pk).exists()
        )
        self.assertFalse(device.interfaces.filter(pk=interface.pk).exists())

    def test_str_includes_device_name(self):
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        interface = Interface.objects.create(name="eth0", device=device)

        self.assertEqual(str(interface), "Device 1 / eth0")

    def test_speed_nullable_defaults_to_none(self):
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        interface = Interface.objects.create(name="eth0", device=device)

        self.assertIsNone(interface.speed)

    def test_speed_stores_positive_integer(self):
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        interface = Interface.objects.create(name="eth0", device=device, speed=1000)

        interface.refresh_from_db()
        self.assertEqual(interface.speed, 1000)

    def test_status_defaults_to_up(self):
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        interface = Interface.objects.create(name="eth0", device=device)

        self.assertEqual(interface.status, Interface.INTERFACE_STATUS_UP)

    def test_status_accepts_all_allowed_values(self):
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        for i, status_val in enumerate(
            [
                Interface.INTERFACE_STATUS_UP,
                Interface.INTERFACE_STATUS_DOWN,
                Interface.INTERFACE_STATUS_MAINTENANCE,
            ]
        ):
            iface = Interface.objects.create(
                name=f"eth{i}", device=device, status=status_val
            )
            iface.refresh_from_db()
            self.assertEqual(iface.status, status_val)

    def test_verbose_names_are_defined(self):
        self.assertEqual(Site._meta.verbose_name, "site")
        self.assertEqual(Site._meta.verbose_name_plural, "sites")
        self.assertEqual(Device._meta.verbose_name, "device")
        self.assertEqual(Device._meta.verbose_name_plural, "devices")
        self.assertEqual(Interface._meta.verbose_name, "interface")
        self.assertEqual(Interface._meta.verbose_name_plural, "interfaces")
        self.assertEqual(Connection._meta.verbose_name, "connection")
        self.assertEqual(Connection._meta.verbose_name_plural, "connections")


class TestConnectionModelValidation(TestCase):
    def setUp(self):
        self.site_1 = Site.objects.create(name="Site 1")
        self.site_2 = Site.objects.create(name="Site 2")

        self.device_1 = Device.objects.create(
            name="Device 1", site=self.site_1, serial_number="sn-1"
        )
        self.device_2 = Device.objects.create(
            name="Device 2", site=self.site_2, serial_number="sn-2"
        )

        self.interface_1 = Interface.objects.create(name="eth0", device=self.device_1)
        self.interface_2 = Interface.objects.create(name="eth0", device=self.device_2)

    def test_rejects_device_that_does_not_belong_to_site(self):
        with self.assertRaises(ValidationError):
            Connection.objects.create(
                connection_id="conn-1",
                start_site=self.site_1,
                start_device=self.device_2,
                end_site=self.site_2,
            )

    def test_rejects_interface_that_does_not_belong_to_device(self):
        connection = Connection(
            connection_id="conn-2",
            start_site=self.site_1,
            start_device=self.device_1,
            start_interface=self.interface_2,
            end_site=self.site_2,
        )

        with self.assertRaises(ValidationError):
            connection.full_clean()

    def test_rejects_interface_without_device(self):
        connection = Connection(
            connection_id="conn-3",
            start_site=self.site_1,
            start_interface=self.interface_1,
            end_site=self.site_2,
        )

        with self.assertRaises(ValidationError):
            connection.full_clean()
