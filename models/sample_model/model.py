from odoo import api, models, fields
from datetime import datetime

class SampleModelModel(models.Model):

    # ----------------------------------------------------
    # Model Definition
    # ----------------------------------------------------

    _name = 'app.odoo_sample_module.sample_model'
    _description = 'Modelo de Exemplo' # Adicionado para tirar o aviso do log
    _inherit = ['mail.thread']

    # ----------------------------------------------------
    # Fields Default's
    # ----------------------------------------------------

    @api.model
    def default_get(self, fields): # Removido o -> dict para evitar conflitos em versões antigas
        result = super(SampleModelModel, self).default_get(fields)
        result.update({
            'company_id': self.env.company.id,
            'user_id': self.env.user.id
        })
        # REMOVIDO: raise Exception(str(type(fields))) 
        # Esse raise travava o Odoo sempre que você tentava criar um registro novo!
        return result

    def _get_default_data(self):
        return fields.Date.today() # Forma mais simples e nativa do Odoo

    # ----------------------------------------------------
    # Fields (CORRIGIDOS: required e string)
    # ----------------------------------------------------

    name = fields.Char(
        string='Nome', 
        size=100, 
        required=True, # Corrigido de requrired
        help='Informa o nome do registro'
    )

    descricao = fields.Char(
        string='Descrição'
    )

    data = fields.Date(
        string='Data',
        required=True, # Corrigido de requrired
        default=_get_default_data
    )

    partner_id = fields.Many2one(
        string='Pessoa', # Corrigido de sttring
        comodel_name='res.partner',
        required=True # Corrigido de requrired
    )

    user_id = fields.Many2one(
        string='Usuário', # Corrigido de sttring
        comodel_name='res.users'
    )

    company_id = fields.Many2one(
        string='Empresa', # Corrigido de sttring
        comodel_name='res.company'
    )

    total = fields.Float(
        string='Valor Total',
        compute='_compute_total',
        store=True
    )

    numero_inteiro = fields.Integer(
        string='Número Inteiro',
        default=0
    )

    state = fields.Selection(
        string='Situação',
        selection=[
            ('pendente', 'Pendente'),
            ('concluido', 'Concluído'),
            ('cancelado', 'Cancelado'),
        ],
        help='''Indica o estado do registro:
            * Pendente: ...
            * Concluído: ...
            * Cancelado: ...
        ''',
        tracking=True
    )

    sample_item_model_ids = fields.One2many(
        string='Itens de Exemplo', # Corrigido de sttring
        comodel_name='app.odoo_sample_module.sample_item_model',
        inverse_name='sample_model_id'
    )

    # Adicione este método apenas para o campo 'total' não dar erro de falta de função
    @api.depends('sample_item_model_ids')
    def _compute_total(self):
        for record in self:
            record.total = 0 # Adicione sua lógica de soma aqui depois