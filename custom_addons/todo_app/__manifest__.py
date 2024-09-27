{
    'name': "To-Do App",
    'author': "Mustafa Sobhi",
    'category': '',
    'version': '17.0.0.1.0',
    'depends': ['base'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'reports/todo_report.xml',  # <-- Ensure this path is correct and points to your menu XML file
        'views/base_menu.xml',  # <-- Ensure this path is correct and points to your menu XML file
        'views/todo_view.xml',  # <-- Ensure this path is correct and points to your menu XML file
        'views/res_partner_view.xml',  # <-- Ensure this path is correct and points to your menu XML file
        'data/sequence.xml',  # <-- Ensure this path is correct and points to your menu XML file
    ],

    'application': True,
}