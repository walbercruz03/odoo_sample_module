from odoo import models, fields


class GetStartedModel(models.Model):
    """Esta classe tem como objetivo servir como ponto de início no tutorial
    de primeiros passos do Odoo.
    """

    # ----------------------------------------------------
    #
    # Model Definition
    #
    # ----------------------------------------------------

    _name = 'app.odoo_sample_module.get_started_model'

    # ----------------------------------------------------
    #
    # Fields
    #
    # ----------------------------------------------------

    name = fields.Char(
        string='Nome'
    )
