{
"name": "GESTION DES ADHERENT",
"version": "0.1",
"summary": """Gestion des adhérents/ Yaghmorasen Mediteranian GYM""",
"category":"rh",
"installable" : True,
'author': 'Sekkak oussama',
'email':'odoo.osk@gmail.com',
'website': 'odoo.osk@gmail.com',
'license': 'AGPL-3',
'depends':['base','report','hr','import_data','product','account','sale'],
"auto_install": False,
"application" : True,
"description" : """
            Ce module gere une association des handicape Yaghmorasen Mediteranian G.Y.M""",
"data": [
        'views/gym_view.xml',
        'views/ir_sequence.xml',
        'views/example_webpage.xml',
        'views/absence_view.xml',
        'views/diagno_view.xml',
        'views/handicap.xml',
        'views/partner_view.xml',
        'views/invoice_view.xml',
        'views/sale_order_view.xml',     
        'report/paper_format.xml',
        'report/report.xml',
        'report/scolarite.xml',
        'report/attestation.xml',
        'report/diagnostic.xml',
        'report/facturation.xml',
        'report/facturation_v2.xml',
        'security/gestion_adherent_security.xml',
        'security/ir.model.access.csv',
        'wizard/contact.xml',


    ] ,
    


    }
