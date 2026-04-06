{
    "name": "Odoo Sample Module",
    "description": "Módulo de exemplo do Odoo - Integração VivaFit Studios.",
    "summary": "Gestão de alunos, turmas e créditos.",
    "category": "Sample",
    "version": "19.0.0.0",
    "author": "Eduardo Luiz",
    "website": "",
    "company": "e-Masters Tecnologia",
    "maintainer": "e-Masters Tecnologia",
    "license": "LGPL-3",
    
    "depends": [
        "base", 
        "mail", 
        "account"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/get_started_model_view.xml",
        "views/metodo_pagamento_view.xml",
        "views/sample_model_view.xml", 
        "views/app.xml",
        "views/clinica_view.xml"
    ],
    "assets": {},
    "qweb": [],
    "images": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}