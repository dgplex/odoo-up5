import json
from datetime import date, timedelta

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCylinderHttp(HttpCase):
    """
    Layer 3 smoke test — verifies the full HTTP stack:
    module installed → model fields exist → JSON-RPC accessible → action works.

    Data is created via RPC inside each test method because HttpCase requests
    run with a separate DB cursor: only *committed* data is visible.
    Records created in setUpClass live in an uncommitted savepoint and would
    return zero results. Creating through RPC commits each write automatically.
    """

    def _rpc(self, model, method, args=None, kwargs=None):
        """Call ORM method via JSON-RPC and return the result dict."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "id": 1,
            "params": {
                "model": model,
                "method": method,
                "args": args or [],
                "kwargs": kwargs or {},
            },
        }
        resp = self.url_open(
            "/web/dataset/call_kw",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotIn("error", body, msg=body.get("error"))
        return body["result"]

    def test_cylinder_fields_accessible_via_rpc(self):
        """Cylinder computed fields are readable over JSON-RPC."""
        self.authenticate("admin", "admin")

        partner_id = self._rpc(
            "res.partner",
            "create",
            args=[{"name": "HTTP Smoke Hospital", "is_company": True}],
        )
        product_id = self._rpc(
            "product.product",
            "create",
            args=[{
                "name": "HTTP Smoke O2 Cylinder",
                "type": "consu",
                "tracking": "serial",
                "is_cylinder": True,
                "gas_type": "o2_industrial",
            }],
        )

        overdue_id = self._rpc(
            "stock.lot",
            "create",
            args=[{
                "name": "HTTP-SMOKE-OVER",
                "product_id": product_id,
                "customer_id": partner_id,
                "dispatch_date": str(date.today() - timedelta(days=40)),
                "rental_days": 30,
                "cylinder_state": "at_customer",
            }],
        )
        ok_id = self._rpc(
            "stock.lot",
            "create",
            args=[{
                "name": "HTTP-SMOKE-OK",
                "product_id": product_id,
                "customer_id": partner_id,
                "dispatch_date": str(date.today() - timedelta(days=10)),
                "rental_days": 30,
                "cylinder_state": "at_customer",
            }],
        )

        records = self._rpc(
            "stock.lot",
            "search_read",
            args=[[("id", "in", [overdue_id, ok_id])]],
            kwargs={
                "fields": ["name", "is_overdue", "overdue_days", "days_at_customer"],
            },
        )
        self.assertEqual(len(records), 2)
        by_name = {r["name"]: r for r in records}

        overdue = by_name["HTTP-SMOKE-OVER"]
        self.assertTrue(overdue["is_overdue"])
        self.assertEqual(overdue["overdue_days"], 10)
        self.assertEqual(overdue["days_at_customer"], 40)

        ok = by_name["HTTP-SMOKE-OK"]
        self.assertFalse(ok["is_overdue"])
        self.assertEqual(ok["overdue_days"], 0)

    def test_cylinder_action_loads(self):
        """The Cylinders window action is installed and points to stock.lot."""
        self.authenticate("admin", "admin")
        actions = self._rpc(
            "ir.actions.act_window",
            "search_read",
            args=[[("res_model", "=", "stock.lot"), ("name", "=", "Cylinders")]],
            kwargs={"fields": ["name", "res_model", "view_mode"]},
        )
        self.assertTrue(len(actions) >= 1, "Cylinders action not found — module may not be installed")
        self.assertEqual(actions[0]["res_model"], "stock.lot")
        self.assertIn("list", actions[0]["view_mode"])

    def test_product_gas_type_readable_via_rpc(self):
        """product.template gas_type and is_cylinder are readable over RPC."""
        self.authenticate("admin", "admin")
        tmpl_id = self._rpc(
            "product.template",
            "create",
            args=[{
                "name": "HTTP Smoke Argon Cylinder",
                "type": "consu",
                "tracking": "serial",
                "is_cylinder": True,
                "gas_type": "ar",
            }],
        )
        records = self._rpc(
            "product.template",
            "read",
            args=[[tmpl_id], ["is_cylinder", "gas_type"]],
        )
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0]["is_cylinder"])
        self.assertEqual(records[0]["gas_type"], "ar")
