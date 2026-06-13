from datetime import date, timedelta

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "chrome_headless")
class TestCylinderTour(HttpCase):
    """
    Layer 3 JS tour — drives the OWL UI through a real browser session.

    Tagged 'chrome_headless': excluded from the default verify.sh run because
    it requires a working Chrome DevTools Protocol connection. Run explicitly:
      conda run -n odoo19 python odoo-bin -c odoo.conf --test-enable \
        -d odoo_dev --stop-after-init -u up5_nsvn_cylinder \
        --test-tags /up5_nsvn_cylinder/chrome_headless

    Why registry.cursor() instead of self.env.cr.commit():
      The test framework patches self.env.cr.commit/rollback to forbidden()
      to protect savepoint integrity. A fresh cursor from self.registry.cursor()
      is not patched and commits automatically on context-manager exit, making
      the tour data visible to the tour's separate DB session.
    """

    def test_cylinder_tour(self):
        lot_id = tmpl_id = partner_id = None

        # Create tour data in a separate committed cursor
        with self.registry.cursor() as cr:
            env = self.env(cr=cr)
            product = env["product.product"].create(
                {
                    "name": "Tour O2 Cylinder",
                    "type": "consu",
                    "tracking": "serial",
                    "is_cylinder": True,
                    "gas_type": "o2_industrial",
                },
            )
            partner = env["res.partner"].create(
                {"name": "Tour Test Hospital", "is_company": True},
            )
            # 40 days dispatched, 30-day rental → 10 days overdue
            lot = env["stock.lot"].create(
                {
                    "name": "TOUR-CYL-OVER",
                    "product_id": product.id,
                    "customer_id": partner.id,
                    "dispatch_date": date.today() - timedelta(days=40),
                    "rental_days": 30,
                    "cylinder_state": "at_customer",
                },
            )
            lot_id = lot.id
            tmpl_id = product.product_tmpl_id.id
            partner_id = partner.id
        # cr.__exit__ commits here → data visible to tour's DB session

        try:
            self.start_tour("/web", "up5_nsvn_cylinder_tour", login="admin")
        finally:
            with self.registry.cursor() as cr:
                env = self.env(cr=cr)
                env["stock.lot"].browse(lot_id).unlink()
                env["product.template"].browse(tmpl_id).unlink()
                env["res.partner"].browse(partner_id).unlink()
