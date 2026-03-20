from odoo import api, models, fields

class SampleItemModel(models.Model):

    # ----------------------------------------------------
    # Model Definition
    # ----------------------------------------------------

    _name = 'app.odoo_sample_module.sample_item_model'
    _description = 'Itens do Modelo de Exemplo'

    # ----------------------------------------------------
    # Fields (CORRIGIDOS: required e string)
    # ----------------------------------------------------

    # Exemplo do campo de TEXTO computado
    name = fields.Char(
        string='Nome',
        compute='_compute_name',
        store=True
    )

    descricao = fields.Char(
        string='Descrição',
        size=100,
        required=True, # Corrigido de requrired
        help='Informa o nome do produto'
    )

    # Relacionamento com o Modelo Pai
    sample_model_id = fields.Many2one(
        string='Modelo de Exemplo', # Corrigido de sttring
        comodel_name='app.odoo_sample_module.sample_model',
        required=True # Corrigido de requrired
    )

    quantidade = fields.Float(
        string='Quantidade',
        default=0
    )

    valor = fields.Float(
        string='Valor do Item',
        default=0
    )

    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True
    )

    # ----------------------------------------------------
    # Business Logic (Funções de Cálculo)
    # ----------------------------------------------------

    @api.depends('descricao')
    def _compute_name(self):
        """Define o nome baseado na descrição."""
        for record in self:
            record.name = record.descricao or "Novo Item"

    @api.depends('quantidade', 'valor')
    def _compute_subtotal(self):
        """Calcula o subtotal: quantidade * valor."""
        for record in self:
            record.subtotal = record.quantidade * record.valor