from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_cylinder = fields.Boolean('Is Cylinder', default=False)
    gas_type = fields.Selection(
        selection=[
            ('o2_industrial', 'Oxygen — Industrial'),
            ('o2_medical', 'Oxygen — Medical'),
            ('n2', 'Nitrogen'),
            ('ar', 'Argon'),
            ('co2', 'CO₂'),
            ('h2', 'Hydrogen'),
            ('he', 'Helium'),
            ('mixed', 'Mixed Gas'),
            ('other', 'Other'),
        ],
        string='Gas Type',
    )
