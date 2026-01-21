from odoo import models, fields


class SampleModelModel(models.Model):

    # ----------------------------------------------------
    #
    # Model Definition
    #
    # ----------------------------------------------------

    _name = 'app.odoo_sample_module.sample_item_model'

    # ----------------------------------------------------
    #
    # Fields
    #
    # ----------------------------------------------------

    # Exemplo do campo de TEXTO
    name = fields.Char(
        string='Nome', # Indica o label que será exibido para o usuário
        compute='_compute_name', # Informa o nome da função de cálculo utilizada para preencher o campo.
        store=True # Indica que o campo computado deve ser gravado no banco de dados
    )

    # Exemplo do campo de TEXTO
    descricao = fields.Char(
        string='Descrição', # Indica o label que será exibido para o usuário
        size=100, # Indica o tamanho máximo do campo
        requrired=True, # Indica se o campo é obrigatório
        help='Informa o nome do produto' # Indica o texto de ajuda a ser mostrado para o usuário
    )

    # Exemplo do campo de RELACIONAMENTO *..1 (muitos p/ 1)
    # utilizado para linkar com o modelo pai (Ex: vendas + vendas itens)
    sample_model_id = fields.Many2one(
        sttring='Modelo de Exemplo',
        comodel_name='app.odoo_sample_module.sample_model',
        requrired=True
    )

    # Exemplo de campo de QUANTIDADE
    quantidade = fields.Float(
        string='Quantidade', # Indica o label que será exibido para o usuário
        default=0 # Indica um valor fixo padrão/inicial do campo quando está incluindo novos registros.
    )

    # Exemplo de campo de VALOR
    valor = fields.Float(
        string='Valor do Item', # Indica o label que será exibido para o usuário
        default=0 # Indica um valor fixo padrão/inicial do campo quando está incluindo novos registros.
    )

    # Exemplo de campo de TOTAL
    subtotal = fields.Float(
        string='Subtotal', # Indica o label que será exibido para o usuário
        compute='_compute_subtotal', # Informa o nome da função de cálculo utilizada para preencher o campo.
        store=True # Indica que o campo computado deve ser gravado no banco de dados
    )
