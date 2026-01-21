from odoo import api, models, fields, tools, _
from odoo.exceptions import ValidationError


class SampleItemModelBusinessLogic(models.Model):

    # ----------------------------------------------------
    #
    # Model Definition
    #
    # ----------------------------------------------------

    _name = 'app.odoo_sample_module.sample_item_model'
    _inherit = ['app.odoo_sample_module.sample_item_model']

    # ----------------------------------------------------
    #
    # Fields Compute
    #
    # ----------------------------------------------------

    @api.depends('name')
    def _compute_name(self):
        for record in self:
            record.name = record.descricao

    @api.depends('valor', 'quantidade')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.valor * record.quantidade

    # ----------------------------------------------------
    #
    # Fields Onchange
    #
    # ----------------------------------------------------

    # ...

    # ----------------------------------------------------
    #
    # Fields Checks and Constraints
    #
    # ----------------------------------------------------

    # ...

    # ----------------------------------------------------
    #
    # Model Overrides Methods
    #
    # ----------------------------------------------------

    # ...

    # ----------------------------------------------------
    #
    # Code Actions
    #
    # ----------------------------------------------------

    # ...

    # ----------------------------------------------------
    #
    # View Actions
    #
    # ----------------------------------------------------

    # ...