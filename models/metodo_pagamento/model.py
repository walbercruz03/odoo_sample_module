from odoo import models, fields


class MetodoPagamentoModel(models.Model):

    # ----------------------------------------------------
    #
    # Model Definition
    #
    # ----------------------------------------------------

    _name = 'app.odoo_sample_module.metodo_pagamento'

    # ----------------------------------------------------
    #
    # Fields
    #
    # ----------------------------------------------------

    name = fields.Char(
        string='Nome'
    )

    roupa = fields.Char(
        string="Roupa"
    )
