from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    is_student = fields.Boolean(string="E Aluno", default=False)


model = ResPartner

