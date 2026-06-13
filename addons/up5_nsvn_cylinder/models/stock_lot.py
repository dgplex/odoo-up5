from datetime import timedelta

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = 'stock.lot'

    # Physical specifications of this cylinder unit
    cylinder_capacity = fields.Float('Capacity (L)', digits=(10, 2))
    cylinder_pressure_rating = fields.Float('Pressure Rating (bar)', digits=(10, 1))
    cylinder_manufacture_year = fields.Integer('Manufacture Year')
    cylinder_next_inspection = fields.Date('Next Inspection Date')

    # Operational state (manually set; auto-sync with moves is out of scope for MVP)
    cylinder_state = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('at_customer', 'At Customer'),
            ('filling', 'Being Filled'),
            ('maintenance', 'Under Maintenance'),
            ('retired', 'Retired'),
        ],
        string='Cylinder State',
        default='available',
    )

    # Customer tracking
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        ondelete='restrict',
        domain=[('is_company', '=', True)],
    )
    dispatch_date = fields.Date('Dispatch Date')
    # How many days the customer is allowed to keep the cylinder before return is overdue
    rental_days = fields.Integer('Rental Period (days)', default=30)

    # Computed — stored so they are searchable/filterable in list views
    expected_return_date = fields.Date(
        'Expected Return Date',
        compute='_compute_overdue_status',
        store=True,
    )
    days_at_customer = fields.Integer(
        'Days at Customer',
        compute='_compute_overdue_status',
        store=True,
    )
    is_overdue = fields.Boolean(
        'Overdue',
        compute='_compute_overdue_status',
        store=True,
    )
    overdue_days = fields.Integer(
        'Overdue Days',
        compute='_compute_overdue_status',
        store=True,
    )

    @api.depends('dispatch_date', 'rental_days', 'customer_id')
    def _compute_overdue_status(self):
        today = fields.Date.today()
        for lot in self:
            if lot.dispatch_date and lot.customer_id:
                expected = lot.dispatch_date + timedelta(days=lot.rental_days or 30)
                lot.expected_return_date = expected
                lot.days_at_customer = max(0, (today - lot.dispatch_date).days)
                lot.is_overdue = today > expected
                lot.overdue_days = max(0, (today - expected).days) if lot.is_overdue else 0
            else:
                lot.expected_return_date = False
                lot.days_at_customer = 0
                lot.is_overdue = False
                lot.overdue_days = 0
