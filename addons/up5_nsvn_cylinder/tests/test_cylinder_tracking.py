from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestCylinderTracking(TransactionCase):
    """Layer 2 tests for cylinder overdue compute logic on stock.lot."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test O2 Cylinder',
            'type': 'consu',
            'tracking': 'serial',
            'is_cylinder': True,
            'gas_type': 'o2_industrial',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Hospital NSVN',
            'is_company': True,
        })

    def _make_lot(self, name, *, dispatch_days_ago=None, rental_days=30, customer=True):
        vals = {
            'name': name,
            'product_id': self.product.id,
            'rental_days': rental_days,
        }
        if customer and dispatch_days_ago is not None:
            vals['customer_id'] = self.partner.id
            vals['dispatch_date'] = fields.Date.today() - timedelta(days=dispatch_days_ago)
        return self.env['stock.lot'].create(vals)

    # --- Happy path ---

    def test_overdue_cylinder(self):
        """Cylinder dispatched 40 days ago with 30-day rental is overdue by 10 days."""
        lot = self._make_lot('CYL-OVER-001', dispatch_days_ago=40, rental_days=30)
        self.assertTrue(lot.is_overdue)
        self.assertEqual(lot.overdue_days, 10)
        self.assertEqual(lot.days_at_customer, 40)
        self.assertEqual(lot.expected_return_date,
                         fields.Date.today() - timedelta(days=10))

    def test_not_overdue_cylinder(self):
        """Cylinder dispatched 10 days ago with 30-day rental is not yet overdue."""
        lot = self._make_lot('CYL-OK-001', dispatch_days_ago=10, rental_days=30)
        self.assertFalse(lot.is_overdue)
        self.assertEqual(lot.overdue_days, 0)
        self.assertEqual(lot.days_at_customer, 10)

    def test_just_dispatched_not_overdue(self):
        """Cylinder dispatched today is not overdue."""
        lot = self._make_lot('CYL-NEW-001', dispatch_days_ago=0, rental_days=30)
        self.assertFalse(lot.is_overdue)
        self.assertEqual(lot.days_at_customer, 0)

    # --- Failure / edge-case scenarios ---

    def test_no_customer_no_overdue(self):
        """Cylinder with no customer and no dispatch date must never be overdue."""
        lot = self._make_lot('CYL-NOCU-001', customer=False)
        self.assertFalse(lot.is_overdue)
        self.assertEqual(lot.days_at_customer, 0)
        self.assertFalse(lot.expected_return_date)
        self.assertEqual(lot.overdue_days, 0)

    def test_dispatch_date_without_customer_no_overdue(self):
        """Dispatch date set but customer cleared → should not trigger overdue."""
        lot = self.env['stock.lot'].create({
            'name': 'CYL-NOCU-002',
            'product_id': self.product.id,
            'dispatch_date': fields.Date.today() - timedelta(days=40),
            'rental_days': 30,
            # customer_id intentionally absent
        })
        self.assertFalse(lot.is_overdue)
        self.assertEqual(lot.days_at_customer, 0)
        self.assertFalse(lot.expected_return_date)

    def test_gas_type_and_is_cylinder_on_product(self):
        """Product template fields is_cylinder and gas_type are readable."""
        tmpl = self.product.product_tmpl_id
        self.assertTrue(tmpl.is_cylinder)
        self.assertEqual(tmpl.gas_type, 'o2_industrial')

    def test_rental_days_default_is_thirty(self):
        """New lots get rental_days=30 by default."""
        lot = self.env['stock.lot'].create({
            'name': 'CYL-DEF-001',
            'product_id': self.product.id,
        })
        self.assertEqual(lot.rental_days, 30)
