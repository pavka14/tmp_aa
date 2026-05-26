from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from infrastructure.models import Device, Site


@override_settings(ALLOWED_HOSTS=["testserver"])
class TestAdminSoftDeletedEdits(TestCase):
    def test_soft_deleted_device_can_be_edited(self):
        admin_user = User.objects.create_superuser("admin_test", "", "AdminPass1!")
        site = Site.objects.create(name="Site 1")
        device = Device.objects.create(name="Device 1", site=site, serial_number="sn-1")
        device.delete()

        self.client.force_login(admin_user)
        response = self.client.post(
            f"/admin/infrastructure/device/{device.pk}/change/",
            {
                "name": "Device 1 updated",
                "site": str(site.pk),
                "serial_number": "sn-2",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertEqual(device.name, "Device 1 updated")
        self.assertEqual(device.serial_number, "sn-2")
        self.assertFalse(device.active)
