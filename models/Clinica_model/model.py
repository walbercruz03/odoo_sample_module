from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationErron 



class PerfilCliente(model.Model):
   _name = 'clinica.perfil.cliente'
   _description = 'Perfil do Cliente'

   name = filds.Char(
    string ='Descrição do Perfil',
    required=true
   )


# 1. 

class ResPartner (models.Model):
    _inherit = 'res.partner'


    primeiro_atendimento = fields.Boolean(string='Cliente novo', default=False)
    vip = fields.Boolean(string='Cliente Vip', default=False)
    convenio = fields.Boolean(string='Cliene convenio', default=False)


    perfil_cliente_id = Many2one(comodel_name='clinica.perfil.cliente' string='Perfil do cliente' ondelete='set null')

# ============================================================
# 3. PRODUTO (tabela produto do diagrama)
# ============================================================
class produto (models.Model):
    _name = 'clinica.produtos'
    _description = 'itens da clinica'

    name = filds.Char (string='Nome do produto/serviço', required=True)
    tipo_produto = filds.Selection(
        selection = [
            ('serviço', 'Serviço'),
            ('produto', 'Produto'),
        ],
        string= 'Tipo',
        required = True,
        default = 'serviço'

    )

    active = fields.Boolean(
        string='Ativo',
        default= True
    )



# ============================================================
# 4. PREÇO BASE (tabela preco_base do diagrama)
# ============================================================

class PrecoBase(models.Model):
    _name = 'cliica.preco.base'
    _description = 'Preç Base dos Produtos'


    produto_id = fields.Many2one(
        comodel_name='clinica.produto',
        string='Produto',
        required=True,
        ondelete='cascade'
    )

    valor = fields.Float(
        string='Valor (R$)',
        required=True,
        ondelete='cascade'
    )

    data_inicio = fields.Date(
        string='Valido a partir de',
        required=True
    )

    data_fim = fields.Date(
        string='Valido ate'
        # sem required=True pois pode ser sem data de fim (vigência aberta)
    )

    @api.constrains('data_inico', 'data_fim')
    def _validar_datas(self):
        for rec in self:
            if rec.data_fim and rec.data_fim < rec.data_inicio:
                raise ValidationError(
                    'A data fi não pode ser anterior a data de inicio'
                )
    

# ============================================================
# 5. REGRA DE PREÇO (tabela regra_preco do diagrama)
# ============================================================

class RegraPreco(models.Model):
    _name =' clinica.regra.preco'
    _description = 'Regras de desconto pro perfil'


    produto_id = fields.Many2one(
        comodel_name='clinica.produto',
        string='Perfil do Cliente',
        required=True,
        ondelete='cascade'
    )

    perfil_cliente_id = fieldsMany2one(
        comodel_name='clinica.perfil.cliente',
        string='Perfil do Cliente',
        required=True,
        ondelete='cascade'
    )
    
    quantidade_min = fields.Integer(
        string='Quantidade minima',
        default=1 # a partir de quantas unidades a regra se aplica
    )

    data_inicio = fields.Date(string='Valido a partir de', required=True)
    data_fim = fields.Date(string='Válido ate')

    tipo_regra = fields.Selection(
        selection=[
            ('percentual', 'Desconto em %'),
            ('fixo', 'Desconto Valor Fixo (R$)'),
        ],
        string='Tipo de Desconto',
        required=True

    )
    desconto = fields.Float(
        string='Desconto',
        required=True,
        help='Se percentual: ex 10 = 10%. Se fixo: ex 5.00 = R$5,00'
    )



