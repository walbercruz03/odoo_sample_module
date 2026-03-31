from odoo import models, fields, api
from datatime import timedelta
from oddo.exceptions import ValidationErron 


class ResPartner (models.Mdel):
    _inherit = 'res.partner'

    primeiro_atendimento = fiels.boolean(string='Cliente novo', default=False)
    vip = fields.boolean(string='Cliente Vip', default=False)
