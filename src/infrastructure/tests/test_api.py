from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from infrastructure.models import Connection, Device, Interface, Site


class ApiTestBase(TestCase):
    """
    Shared test fixtures for all API tests.

    Each test creates its own users and data in setUp so tests are fully
    isolated and deterministic.

    Note: a proof-of-concept data migration creates an ``admin``/``admin123``
    superuser for local/demo convenience, but tests never rely on that account.
    It is not guaranteed to exist in all environments, so each test class
    creates its own superuser via ``User.objects.create_superuser``.
    """

    def setUp(self):
        self.client = APIClient()
        self.superuser = User.objects.create_superuser("admin_api", "", "AdminPass1!")
        self.regular_user = User.objects.create_user("regular_api", "", "UserPass1!")
        self.site1 = Site.objects.create(
            name="Site One", description="First site", status=Site.SITE_STATUS_ACTIVE
        )
        self.site2 = Site.objects.create(
            name="Site Two", description="Second site", status=Site.SITE_STATUS_ACTIVE
        )
        self.device1 = Device.objects.create(
            name="Device Alpha", site=self.site1, serial_number="SN-001"
        )
        self.device2 = Device.objects.create(
            name="Device Beta", site=self.site2, serial_number="SN-002"
        )
        self.iface1 = Interface.objects.create(name="eth0", device=self.device1)
        self.iface2 = Interface.objects.create(name="eth0", device=self.device2)
        self.conn1 = Connection.objects.create(
            connection_id="CONN-001",
            name="Test Connection",
            status=Connection.CONNECTION_STATUS_CONNECTED,
            start_site=self.site1,
            start_device=self.device1,
            start_interface=self.iface1,
            end_site=self.site2,
            end_device=self.device2,
            end_interface=self.iface2,
        )

    def login_superuser(self):
        self.client.force_login(self.superuser)

    def login_regular_user(self):
        self.client.force_login(self.regular_user)


class TestSiteList(ApiTestBase):
    url = "/api/v1/sites/"

    def test_list_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_anonymous_returns_403(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authenticated_user(self):
        self.login_regular_user()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_create_anonymous_returns_403(self):
        response = self.client.post(self.url, {"name": "New Site"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_requires_superuser(self):
        self.login_regular_user()
        response = self.client.post(self.url, {"name": "New Site"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_as_superuser(self):
        self.login_superuser()
        response = self.client.post(
            self.url,
            {"name": "Valid Name", "status": Site.SITE_STATUS_PLANNED},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Valid Name")
        self.assertTrue(Site.objects.filter(name="Valid Name").exists())

    def test_create_name_too_short_rejected(self):
        self.login_superuser()
        response = self.client.post(
            self.url, {"name": "ab", "status": Site.SITE_STATUS_PLANNED}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"],
            ["Ensure this field has at least 4 characters."],
        )

    def test_create_name_too_long_rejected(self):
        self.login_superuser()
        long_name = "x" * 41
        response = self.client.post(
            self.url, {"name": long_name, "status": Site.SITE_STATUS_PLANNED}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"],
            ["Ensure this field has no more than 40 characters."],
        )

    def test_create_name_at_min_boundary_accepted(self):
        self.login_superuser()
        response = self.client.post(
            self.url, {"name": "abcd", "status": Site.SITE_STATUS_PLANNED}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_name_at_max_boundary_accepted(self):
        self.login_superuser()
        response = self.client.post(
            self.url, {"name": "x" * 40, "status": Site.SITE_STATUS_PLANNED}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestSiteDetail(ApiTestBase):
    def get_url(self, pk):
        return f"/api/v1/sites/{pk}/"

    def test_retrieve_anonymous_returns_403(self):
        response = self.client.get(self.get_url(self.site1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_authenticated_user(self):
        self.login_regular_user()
        response = self.client.get(self.get_url(self.site1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.site1.name)

    def test_update_anonymous_returns_403(self):
        response = self.client.patch(
            self.get_url(self.site1.pk), {"description": "Updated"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_requires_superuser(self):
        self.login_regular_user()
        response = self.client.patch(
            self.get_url(self.site1.pk), {"description": "Updated"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_as_superuser(self):
        self.login_superuser()
        response = self.client.patch(
            self.get_url(self.site1.pk), {"description": "Updated description"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Updated description")
        self.site1.refresh_from_db()
        self.assertEqual(self.site1.description, "Updated description")

    def test_delete_anonymous_returns_403(self):
        response = self.client.delete(self.get_url(self.site1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_requires_superuser(self):
        self.login_regular_user()
        response = self.client.delete(self.get_url(self.site1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_as_superuser_soft_deletes(self):
        self.login_superuser()
        site = Site.objects.create(name="ToDelete", status=Site.SITE_STATUS_PLANNED)
        response = self.client.delete(self.get_url(site.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Site.objects.filter(pk=site.pk).exists())
        self.assertTrue(Site.objects.with_deleted().filter(pk=site.pk).exists())

    def test_retrieve_unauthenticated_returns_403(self):
        response = self.client.get(self.get_url(self.site1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestDeviceEndpoints(ApiTestBase):
    list_url = "/api/v1/devices/"

    def detail_url(self, pk):
        return f"/api/v1/devices/{pk}/"

    def test_list_anonymous_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authenticated(self):
        self.login_regular_user()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_unauthenticated_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_anonymous_returns_403(self):
        response = self.client.get(self.detail_url(self.device1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_anonymous_returns_403(self):
        response = self.client.post(
            self.list_url,
            {"name": "New Device", "site": self.site1.pk, "serial_number": "SN-NEW"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_as_superuser(self):
        self.login_superuser()
        response = self.client.post(
            self.list_url,
            {"name": "New Device", "site": self.site1.pk, "serial_number": "SN-NEW"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Device")
        self.assertTrue(Device.objects.filter(name="New Device").exists())

    def test_create_requires_superuser(self):
        self.login_regular_user()
        response = self.client.post(
            self.list_url,
            {"name": "New Device", "site": self.site1.pk, "serial_number": "SN-NEW"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_as_superuser(self):
        self.login_superuser()
        response = self.client.patch(
            self.detail_url(self.device1.pk), {"serial_number": "SN-UPDATED"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["serial_number"], "SN-UPDATED")
        self.device1.refresh_from_db()
        self.assertEqual(self.device1.serial_number, "SN-UPDATED")

    def test_update_requires_superuser(self):
        self.login_regular_user()
        response = self.client.patch(
            self.detail_url(self.device1.pk), {"serial_number": "SN-BLOCKED"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_anonymous_returns_403(self):
        response = self.client.patch(
            self.detail_url(self.device1.pk), {"serial_number": "SN-ANON"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_authenticated(self):
        self.login_regular_user()
        response = self.client.get(self.detail_url(self.device1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.device1.name)

    def test_delete_as_superuser_soft_deletes(self):
        self.login_superuser()
        device = Device.objects.create(
            name="ToDelete", site=self.site1, serial_number="SN-DEL"
        )
        response = self.client.delete(self.detail_url(device.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Device.objects.filter(pk=device.pk).exists())
        self.assertTrue(Device.objects.with_deleted().filter(pk=device.pk).exists())

    def test_delete_requires_superuser(self):
        self.login_regular_user()
        response = self.client.delete(self.detail_url(self.device1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_anonymous_returns_403(self):
        response = self.client.delete(self.detail_url(self.device1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestInterfaceEndpoints(ApiTestBase):
    list_url = "/api/v1/interfaces/"

    def detail_url(self, pk):
        return f"/api/v1/interfaces/{pk}/"

    def test_list_anonymous_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authenticated(self):
        self.login_regular_user()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_unauthenticated_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_anonymous_returns_403(self):
        response = self.client.get(self.detail_url(self.iface1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_anonymous_returns_403(self):
        response = self.client.post(
            self.list_url, {"name": "eth1", "device": self.device1.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_as_superuser(self):
        self.login_superuser()
        response = self.client.post(
            self.list_url,
            {"name": "eth1", "device": self.device1.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Interface.objects.filter(name="eth1", device=self.device1).exists()
        )

    def test_create_requires_superuser(self):
        self.login_regular_user()
        response = self.client.post(
            self.list_url, {"name": "eth1", "device": self.device1.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_as_superuser(self):
        self.login_superuser()
        response = self.client.patch(self.detail_url(self.iface1.pk), {"name": "eth9"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "eth9")
        self.iface1.refresh_from_db()
        self.assertEqual(self.iface1.name, "eth9")

    def test_delete_as_superuser_soft_deletes(self):
        self.login_superuser()
        iface = Interface.objects.create(name="eth2", device=self.device1)
        response = self.client.delete(self.detail_url(iface.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Interface.objects.filter(pk=iface.pk).exists())
        self.assertTrue(Interface.objects.with_deleted().filter(pk=iface.pk).exists())

    def test_create_with_speed_and_status(self):
        self.login_superuser()
        response = self.client.post(
            self.list_url,
            {
                "name": "eth3",
                "device": self.device1.pk,
                "speed": 10000,
                "status": Interface.INTERFACE_STATUS_DOWN,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["speed"], 10000)
        self.assertEqual(response.data["status"], Interface.INTERFACE_STATUS_DOWN)
        iface = Interface.objects.get(name="eth3", device=self.device1)
        self.assertEqual(iface.speed, 10000)
        self.assertEqual(iface.status, Interface.INTERFACE_STATUS_DOWN)

    def test_create_defaults_speed_null_status_up(self):
        self.login_superuser()
        response = self.client.post(
            self.list_url,
            {"name": "eth4", "device": self.device1.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["speed"])
        self.assertEqual(response.data["status"], Interface.INTERFACE_STATUS_UP)
        iface = Interface.objects.get(name="eth4", device=self.device1)
        self.assertIsNone(iface.speed)
        self.assertEqual(iface.status, Interface.INTERFACE_STATUS_UP)

    def test_update_speed_and_status(self):
        self.login_superuser()
        response = self.client.patch(
            self.detail_url(self.iface1.pk),
            {"speed": 100, "status": Interface.INTERFACE_STATUS_MAINTENANCE},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.iface1.refresh_from_db()
        self.assertEqual(self.iface1.speed, 100)
        self.assertEqual(self.iface1.status, Interface.INTERFACE_STATUS_MAINTENANCE)


class TestConnectionEndpoints(ApiTestBase):
    list_url = "/api/v1/connections/"

    def detail_url(self, pk):
        return f"/api/v1/connections/{pk}/"

    def _valid_payload(self):
        iface_new1 = Interface.objects.create(name="eth1", device=self.device1)
        iface_new2 = Interface.objects.create(name="eth1", device=self.device2)
        return (
            {
                "connection_id": "CONN-NEW",
                "name": "New Conn",
                "status": Connection.CONNECTION_STATUS_CONNECTED,
                "start": {
                    "site": self.site1.pk,
                    "device": self.device1.pk,
                    "interface": iface_new1.pk,
                },
                "end": {
                    "site": self.site2.pk,
                    "device": self.device2.pk,
                    "interface": iface_new2.pk,
                },
            },
        )

    def test_list_anonymous_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authenticated(self):
        self.login_regular_user()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_unauthenticated_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_anonymous_returns_403(self):
        response = self.client.get(self.detail_url(self.conn1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_anonymous_returns_403(self):
        (payload,) = self._valid_payload()
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_valid_connection_as_superuser(self):
        self.login_superuser()
        iface_new1 = Interface.objects.create(name="eth1", device=self.device1)
        iface_new2 = Interface.objects.create(name="eth1", device=self.device2)
        payload = {
            "connection_id": "CONN-NEW",
            "name": "New Conn",
            "status": Connection.CONNECTION_STATUS_CONNECTED,
            "start": {
                "site": self.site1.pk,
                "device": self.device1.pk,
                "interface": iface_new1.pk,
            },
            "end": {
                "site": self.site2.pk,
                "device": self.device2.pk,
                "interface": iface_new2.pk,
            },
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["connection_id"], "CONN-NEW")
        conn = Connection.objects.get(connection_id="CONN-NEW")
        self.assertEqual(conn.start_site, self.site1)
        self.assertEqual(conn.start_device, self.device1)
        self.assertEqual(conn.start_interface, iface_new1)
        self.assertEqual(conn.end_site, self.site2)
        self.assertEqual(conn.end_device, self.device2)
        self.assertEqual(conn.end_interface, iface_new2)

    def test_create_site_only_endpoints_accepted(self):
        self.login_superuser()
        payload = {
            "connection_id": "CONN-SITE-ONLY",
            "status": Connection.CONNECTION_STATUS_DISCONNECTED,
            "start": {"site": self.site1.pk},
            "end": {"site": self.site2.pk},
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conn = Connection.objects.get(connection_id="CONN-SITE-ONLY")
        self.assertIsNone(conn.start_device)
        self.assertIsNone(conn.end_device)

    def test_create_invalid_device_site_mismatch_rejected(self):
        self.login_superuser()
        payload = {
            "connection_id": "CONN-BAD",
            "status": Connection.CONNECTION_STATUS_DISCONNECTED,
            "start": {"site": self.site1.pk, "device": self.device2.pk},
            "end": {"site": self.site2.pk},
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["start_device"],
            ["Start device must belong to the selected site."],
        )

    def test_create_soft_deleted_site_rejected(self):
        self.login_superuser()
        deleted_site = Site.objects.create(
            name="Deleted Site", status=Site.SITE_STATUS_ACTIVE
        )
        deleted_site.delete()
        payload = {
            "connection_id": "CONN-DEL-SITE",
            "status": Connection.CONNECTION_STATUS_DISCONNECTED,
            "start": {"site": deleted_site.pk},
            "end": {"site": self.site2.pk},
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start", response.data)

    def test_create_requires_superuser(self):
        self.login_regular_user()
        payload = {
            "connection_id": "CONN-UNAUTH",
            "status": Connection.CONNECTION_STATUS_DISCONNECTED,
            "start": {"site": self.site1.pk},
            "end": {"site": self.site2.pk},
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_authenticated(self):
        self.login_regular_user()
        response = self.client.get(self.detail_url(self.conn1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["connection_id"], self.conn1.connection_id)

    def test_update_as_superuser(self):
        self.login_superuser()
        response = self.client.patch(
            self.detail_url(self.conn1.pk),
            {"name": "Updated Connection"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Connection")
        self.conn1.refresh_from_db()
        self.assertEqual(self.conn1.name, "Updated Connection")

    def test_update_requires_superuser(self):
        self.login_regular_user()
        response = self.client.patch(
            self.detail_url(self.conn1.pk),
            {"name": "Blocked Update"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_anonymous_returns_403(self):
        response = self.client.patch(
            self.detail_url(self.conn1.pk),
            {"name": "Anon Update"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_invalid_hierarchy_rejected(self):
        """PATCH that changes start.device to a device on a different site is rejected."""
        self.login_superuser()
        response = self.client.patch(
            self.detail_url(self.conn1.pk),
            {
                "start": {
                    "site": self.site1.pk,
                    "device": self.device2.pk,
                }
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["start_device"],
            ["Start device must belong to the selected site."],
        )

    def test_delete_as_superuser_soft_deletes(self):
        self.login_superuser()
        conn = Connection.objects.create(
            connection_id="CONN-DEL",
            status=Connection.CONNECTION_STATUS_DISCONNECTED,
            start_site=self.site1,
            end_site=self.site2,
        )
        response = self.client.delete(self.detail_url(conn.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Connection.objects.filter(pk=conn.pk).exists())
        self.assertTrue(Connection.objects.with_deleted().filter(pk=conn.pk).exists())

    def test_delete_anonymous_returns_403(self):
        response = self.client.delete(self.detail_url(self.conn1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_requires_superuser(self):
        self.login_regular_user()
        response = self.client.delete(self.detail_url(self.conn1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestTracedConnections(ApiTestBase):
    def traced_url(self, traced_type, traced_id):
        return f"/api/v1/connections/traced/?type={traced_type}&id={traced_id}"

    def test_trace_by_site_returns_connections(self):
        self.login_regular_user()
        response = self.client.get(self.traced_url("site", self.site1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["traced_object"]["type"], "site")
        self.assertEqual(response.data["traced_object"]["id"], self.site1.pk)
        self.assertEqual(response.data["connections_count"], 1)
        self.assertEqual(len(response.data["connections"]), 1)

    def test_trace_by_device_returns_connections(self):
        self.login_regular_user()
        response = self.client.get(self.traced_url("device", self.device1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["connections_count"], 1)

    def test_trace_by_interface_returns_connections(self):
        self.login_regular_user()
        response = self.client.get(self.traced_url("interface", self.iface1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["connections_count"], 1)

    def test_connection_response_has_nested_targets(self):
        self.login_regular_user()
        response = self.client.get(self.traced_url("site", self.site1.pk))
        conn = response.data["connections"][0]
        self.assertIn("start_target", conn)
        self.assertIn("end_target", conn)
        self.assertEqual(conn["start_target"]["site"]["id"], self.site1.pk)
        self.assertEqual(conn["end_target"]["site"]["id"], self.site2.pk)

    def test_trace_with_no_connections_returns_empty(self):
        self.login_regular_user()
        site3 = Site.objects.create(name="Lonely Site", status=Site.SITE_STATUS_ACTIVE)
        response = self.client.get(self.traced_url("site", site3.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["connections_count"], 0)
        self.assertEqual(response.data["connections"], [])

    def test_trace_invalid_type_returns_400(self):
        self.login_regular_user()
        response = self.client.get(
            f"/api/v1/connections/traced/?type=invalid&id={self.site1.pk}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "'type' must be one of: site, device, interface."
        )

    def test_trace_missing_id_returns_400(self):
        self.login_regular_user()
        response = self.client.get("/api/v1/connections/traced/?type=site")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "'id' query parameter is required.")

    def test_trace_non_integer_id_returns_400(self):
        self.login_regular_user()
        response = self.client.get("/api/v1/connections/traced/?type=site&id=abc")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "'id' must be a positive integer.")

    def test_trace_non_positive_id_returns_400(self):
        self.login_regular_user()
        for bad_id in ("0", "-1"):
            with self.subTest(id=bad_id):
                response = self.client.get(
                    f"/api/v1/connections/traced/?type=site&id={bad_id}"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(
                    response.data["detail"], "'id' must be a positive integer."
                )

    def test_trace_nonexistent_object_returns_404(self):
        self.login_regular_user()
        response = self.client.get("/api/v1/connections/traced/?type=site&id=99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Site with id=99999 not found.")

    def test_trace_requires_authentication(self):
        response = self.client.get(self.traced_url("site", self.site1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestSchemaEndpoints(ApiTestBase):
    def test_schema_download_renders(self):
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_swagger_ui_renders(self):
        response = self.client.get("/api/schema/swagger/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_ui_renders(self):
        response = self.client.get("/api/schema/redoc/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
