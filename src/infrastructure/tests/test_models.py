from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from infrastructure.models import Connection, Device, Interface, Site


class SiteModelTests(TestCase):
    def test_active_unique_name_with_soft_delete(self):
        first = Site.objects.create(name='Site 1')

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Site.objects.create(name='Site 1')

        first.delete()

        second = Site.objects.create(name='Site 1')

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Site.objects.create(name='Site 1')

        second.delete()
        second.refresh_from_db()
        self.assertFalse(second.active)

        third = Site.objects.create(name='Site 1')
        self.assertEqual(third.name, 'Site 1')

    def test_manager_excludes_deleted_by_default(self):
        site = Site.objects.create(name='Site 1')
        site.delete()

        self.assertFalse(Site.objects.filter(pk=site.pk).exists())
        self.assertTrue(Site.objects.with_deleted().filter(pk=site.pk).exists())


class ConnectionModelValidationTests(TestCase):
    def setUp(self):
        self.site_1 = Site.objects.create(name='Site 1')
        self.site_2 = Site.objects.create(name='Site 2')

        self.device_1 = Device.objects.create(name='Device 1', site=self.site_1, serial_number='sn-1')
        self.device_2 = Device.objects.create(name='Device 2', site=self.site_2, serial_number='sn-2')

        self.interface_1 = Interface.objects.create(name='eth0', device=self.device_1)
        self.interface_2 = Interface.objects.create(name='eth0', device=self.device_2)

    def test_rejects_device_that_does_not_belong_to_site(self):
        with self.assertRaises(ValidationError):
            Connection.objects.create(
                connection_id='conn-1',
                start_site=self.site_1,
                start_device=self.device_2,
                end_site=self.site_2,
            )

    def test_rejects_interface_that_does_not_belong_to_device(self):
        connection = Connection(
            connection_id='conn-2',
            start_site=self.site_1,
            start_device=self.device_1,
            start_interface=self.interface_2,
            end_site=self.site_2,
        )

        with self.assertRaises(ValidationError):
            connection.full_clean()

    def test_rejects_interface_without_device(self):
        connection = Connection(
            connection_id='conn-3',
            start_site=self.site_1,
            start_interface=self.interface_1,
            end_site=self.site_2,
        )

        with self.assertRaises(ValidationError):
            connection.full_clean()
