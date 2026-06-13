{
    'name': 'NSVN Cylinder Tracking',
    'version': '19.0.1.0.0',
    'summary': 'Cylinder lifecycle tracking for Nippon Sanso Vietnam',
    'description': """
        Tracks industrial and medical gas cylinders throughout their lifecycle:
        dispatch to customer, overdue detection, physical specifications.
        Quick-win MVP for NSVN — Phase 1 of the gas industry Odoo rollout.
    """,
    'category': 'Inventory',
    'author': 'UP5 TECH',
    'depends': ['stock', 'product'],
    'data': [
        'views/product_template_views.xml',
        'views/stock_lot_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo_cylinders.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
