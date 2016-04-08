{
    'name': 'Stock Delivery Note',
    'version': '1.0',
    'category': 'Warehouse',
    'description': 
    """
    Stock delivery note report
    
    This modules creates reports for deliveries that will be exported and printed for the customer.
    
    2 reports:
        - Delivery note report: contains the list of the products that the customer picks
        - Order form report: contains the list of the products of the current purchase orders of the customer.
    
    This module has been developed by Valentin THIRION and Bernard DELHEZ, intern @ AbAKUS it-solutions.
    """,
    'depends': ['stock'],
    'data': [
        'wizard/stock_delivery_note_view.xml',
        'report/stock_delivery_note_report.xml',
        'report/stock_order_form_report.xml'
    ],
    'installable': True,
    'author': "Valentin THIRION and Bernard DELHEZ, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
}
