from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from infrastructure.models import Connection, Device, Interface, Site

_SUPERPASS = "AdminPass1!"
_USERPASS = "UserPass1!"


class ApiTestBase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.superuser = User.objects.create_superuser("admin_api", "", _SUPERPASS)
        self.regular_user = User.objects.create_user("regular_api", "", _USERPASS)
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

    def test_list_authenticated_user(self):
        self.login_regular_user()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

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

    def test_create_name_too_short_rejected(self):
        self.login_superuser()
        response = self.client.post(
            self.url, {"name": "ab", "status": Site.SITE_STATUS_PLANNED}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_name_too_long_rejected(self):
        self.login_superuser()
        long_name = "x" * 41
        response = self.client.post(
            self.url, {"name": long_name, "status": Site.SITE_STATUS_PLANNED}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

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

    def test_retrieve_authenticated_user(self):
        self.login_regular_user()
        response = self.client.get(self.get_url(self.site1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.site1.name)

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

    def test_list_authenticated(self):
        self.login_regular_user()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_unauthenticated_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_as_superuser(self):
        self.login_superuser()
        response = self.client.post(
            self.list_url,
            {"name": "New Device", "site": self.site1.pk, "serial_number": "SN-NEW"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Device")

    def test_create_requires_superuser(self):
        self.login_regular_user()
        response = self.client.post(
            self.list_url,
            {"name": "New Device", "site": self.site1.pk, "serial_number": "SN-NEW"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_as_superuser_soft_deletes(self):
        self.login_superuser()
        device = Device.objects.create(
            name="ToDelete", site=self.site1, serial_number="SN-DEL"
        )
        response = self.client.delete(self.detail_url(device.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Device.objects.filter(pk=device.pk).exists())
        self.assertTrue(Device.objects.with_deleted().filter(pk=device.pk).exists())


class TestInterfaceEndpoints(ApiTestBase):
    list_url = "/api/v1/interfaces/"

    def detail_url(self, pk):
        return f"/api/v1/interfaces/{pk}/"

    def test_list_authenticated(self):
        self.login_regular_user()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_unauthenticated_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_as_superuser(self):
        self.login_superuser()
        response = self.client.post(
            self.list_url,
            {"name": "eth1", "device": self.device1.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_requires_superuser(self):
        self.login_regular_user()
        response = self.client.post(
            self.list_url, {"name": "eth1", "device": self.device1.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_as_superuser_soft_deletes(self):
        self.login_superuser()
        iface = Interface.objects.create(name="eth2", device=self.device1)
        response = self.client.delete(self.detail_url(iface.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Interface.objects.filter(pk=iface.pk).exists())
        self.assertTrue(Interface.objects.with_deleted().filter(pk=iface.pk).exists())


class TestConnectionEndpoints(ApiTestBase):
    list_url = "/api/v1/connections/"

    def detail_url(self, pk):
        return f"/api/v1/connections/{pk}/"

    def test_list_authenticated(self):
        self.login_regular_user()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_unauthenticated_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_valid_connection_as_superuser(self):
        self.login_superuser()
        iface_new1 = Interface.objects.create(name="eth1", device=self.device1)
        iface_new2 = Interface.objects.create(name="eth1", device=self.device2)
        response = self.client.post(
            self.list_url,
            {
                "connection_id": "CONN-NEW",
                "name": "New Conn",
                "status": Connection.CONNECTION_STATUS_CONNECTED,
                "start_site": self.site1.pk,
                "start_device": self.device1.pk,
                "start_interface": iface_new1.pk,
                "end_site": self.site2.pk,
                "end_device": self.device2.pk,
                "end_interface": iface_new2.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_device_site_mismatch_rejected(self):
        self.login_superuser()
        response = self.client.post(
            self.list_url,
            {
                "connection_id": "CONN-BAD",
                "status": Connection.CONNECTION_STATUS_DISCONNECTED,
                "start_site": self.site1.pk,
                "start_device": self.device2.pk,
                "end_site": self.site2.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_requires_superuser(self):
        self.login_regular_user()
        response = self.client.post(
            self.list_url,
            {
                "connection_id": "CONN-UNAUTH",
                "status": Connection.CONNECTION_STATUS_DISCONNECTED,
                "start_site": self.site1.pk,
                "end_site": self.site2.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_trace_missing_id_returns_400(self):
        self.login_regular_user()
        response = self.client.get("/api/v1/connections/traced/?type=site")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_trace_nonexistent_object_returns_404(self):
        self.login_regular_user()
        response = self.client.get("/api/v1/connections/traced/?type=site&id=99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_trace_requires_authentication(self):
        response = self.client.get(self.traced_url("site", self.site1.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_trace_non_integer_id_returns_400(self):
        self.login_regular_user()
        response = self.client.get("/api/v1/connections/traced/?type=site&id=abc")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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
