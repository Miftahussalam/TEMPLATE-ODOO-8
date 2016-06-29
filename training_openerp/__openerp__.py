{
    "name":"Training OpenERP",
    "version":"1.0",
    "author":"RADIO RODJA 756 AM",
    "website":"http://radiorodja.com",
    "category":"Custom Modules",
    "description": """
        Training OpenERP
    """,
    "depends":["base"],
    "init_xml":[],
    "demo_xml":[],
    "data":[
        "training_openerp_report.xml",
        "training_openerp_view.xml",
        "training_openerp_workflow.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
    ],
    "active":False,
    "installable":True
}