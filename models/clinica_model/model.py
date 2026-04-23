from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError 


class ClinicaDashboard(models.TransientModel):
    _name = 'clinica.dashboard'
    _description = 'Painel Visual de Boas-vindas'

    
    #campo de texto se quiser exibir mensagens dinâmicas.
    name = fields.Char(string="Título", default="Dashboard Clínica")


# ============================================================
# 1. PERFIL DO CLIENTE
# ============================================================
class PerfilCliente(models.Model):
    _name = 'clinica.perfil.cliente'
    _description = 'Perfil do Cliente'

    name = fields.Char(
        string='Descrição do Perfil',
        required=True
    )


# ============================================================
# 2. CLIENTE (via res.partner)
# ============================================================
class ResPartner(models.Model):
    _inherit = 'res.partner'

    primeiro_atendimento = fields.Boolean(string='Cliente Novo', default=False)
    vip = fields.Boolean(string='Cliente VIP', default=False)
    convenio = fields.Boolean(string='Cliente Convênio', default=False)

    perfil_cliente_id = fields.Many2one(
        comodel_name='clinica.perfil.cliente',
        string='Perfil do Cliente',
        ondelete='set null'
    )


# ============================================================
# 3. PRODUTO
# ============================================================
class Produto(models.Model):
    _name = 'clinica.produto'
    _description = 'Produtos e Serviços da Clínica'

    name = fields.Char(string='Nome do Produto/Serviço', required=True)

    tipo_produto = fields.Selection(
        selection=[
            ('servico', 'Serviço'),
            ('produto', 'Produto'),
        ],
        string='Tipo',
        required=True,
        default='servico'
    )

    active = fields.Boolean(string='Ativo', default=True)

    preco_base_ids = fields.One2many(
        comodel_name='clinica.preco.base',
        inverse_name='produto_id',
        string='Preços Base'
    )

    regra_preco_ids = fields.One2many(
        comodel_name='clinica.regra.preco',
        inverse_name='produto_id',
        string='Regras de Preço'
    )


# ============================================================
# 4. PREÇO BASE
# ============================================================
class PrecoBase(models.Model):
    _name = 'clinica.preco.base'
    _description = 'Preço Base dos Produtos'

    produto_id = fields.Many2one(
        comodel_name='clinica.produto',
        string='Produto',
        required=True,
        ondelete='cascade'
    )

    valor = fields.Float(string='Valor (R$)', required=True)
    data_inicio = fields.Date(string='Válido a partir de', required=True)
    data_fim = fields.Date(string='Válido até')

    @api.constrains('data_inicio', 'data_fim')
    def _validar_datas(self):
        for rec in self:
            if rec.data_fim and rec.data_fim < rec.data_inicio:
                raise ValidationError(
                    'A data fim não pode ser anterior à data de início.'
                )

    def action_tabela_precos(self):
        hoje = fields.Date.today()
        registros_vigentes = self.search([
            ('data_inicio', '<=', hoje),
            '|',
            ('data_fim', '=', False),
            ('data_fim', '>=', hoje),
        ])
        return self.env.ref('clinica.report_tabela_precos').report_action(registros_vigentes)




# ============================================================
# 5. REGRA DE PREÇO
# ============================================================
class RegraPreco(models.Model):
    _name = 'clinica.regra.preco'
    _description = 'Regras de Desconto por Perfil'

    produto_id = fields.Many2one(
        comodel_name='clinica.produto',
        string='Produto',
        required=True,
        ondelete='cascade'
    )

    perfil_cliente_id = fields.Many2one(
        comodel_name='clinica.perfil.cliente',
        string='Perfil do Cliente',
        required=True,
        ondelete='cascade'
    )

    quantidade_min = fields.Integer(string='Quantidade Mínima', default=1)
    data_inicio = fields.Date(string='Válido a partir de', required=True)
    data_fim = fields.Date(string='Válido até')

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

    @api.constrains('data_inicio', 'data_fim')
    def _validar_datas(self):
        for rec in self:
            if rec.data_fim and rec.data_fim < rec.data_inicio:
                raise ValidationError(
                    'A data fim não pode ser anterior à data de início.'
                )


# ============================================================
# 6. COMBINAÇÃO DE PRODUTO
# ============================================================
class CombinacaoProduto(models.Model):
    _name = 'clinica.combinacao.produto'
    _description = 'Combinação de Produtos com Desconto'

    produto_principal_id = fields.Many2one(
        comodel_name='clinica.produto',
        string='Produto Principal',
        required=True,
        ondelete='cascade'
    )

    produto_relacionado_id = fields.Many2one(
        comodel_name='clinica.produto',
        string='Produto Relacionado',
        required=True,
        ondelete='cascade'
    )

    tipo_desconto = fields.Selection(
        selection=[
            ('percentual', 'Desconto em %'),
            ('fixo', 'Desconto Valor Fixo (R$)'),
        ],
        string='Tipo de Desconto',
        required=True
    )

   

    valor_final = fields.Float(string='Valor Final (R$)', required=True)


# ============================================================
# 7. PEDIDO
# ============================================================
class Pedido(models.Model):
    _name = 'clinica.pedido'
    _description = 'Pedido do Cliente'

    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        required=True,
        ondelete='restrict'
    )

    data_hora = fields.Datetime(
        string='Data e Hora',
        required=True,
        default=fields.Datetime.now
    )

    item_ids = fields.One2many(
        comodel_name='clinica.item.pedido',
        inverse_name='pedido_id',
        string='Itens do Pedido'
    )

    valor_total = fields.Float(
        string='Valor Total (R$)',
        compute='_compute_valor_total',
        store=True
    )

    @api.depends('item_ids.valor_final')
    def _compute_valor_total(self):
        for rec in self:
            rec.valor_total = sum(rec.item_ids.mapped('valor_final'))

    @api.constrains('item_ids')
    def _validar_bundles(self):
        for pedido in self:
            produtos_no_pedido = pedido.item_ids.mapped('produto_id')
            for item in pedido.item_ids:
                bundles = self.env['clinica.combinacao.produto'].search([
                    ('produto_principal_id', '=', item.produto_id.id)
                ])
                

    def action_imprimir_comprovante(self):
            # Garante que o usuário está olhando apenas um registro
            self.ensure_one()
            # Chama a ação definida no XML
            return self.env.ref('odoo_sample_module.action_report_comprovante_pedido').report_action(self)

# ============================================================
# 8. ITEM DO PEDIDO
# ============================================================
class ItemPedido(models.Model):
    _name = 'clinica.item.pedido'
    _description = 'Itens do Pedido'

    pedido_id = fields.Many2one(
        comodel_name='clinica.pedido',
        string='Pedido',
        required=True,
        ondelete='cascade'
    )

    produto_id = fields.Many2one(
        comodel_name='clinica.produto',
        string='Produto/Serviço',
        required=True,
        ondelete='restrict'
    )

    quantidade = fields.Integer(string='Quantidade', required=True, default=1)

    desconto_aplicado = fields.Float(
    string='Desconto Aplicado (R$)',
    compute='_compute_desconto_aplicado',
    store=True
    )

    valor_final = fields.Float(
        string='Valor Final (R$)',
        compute='_compute_valor_final',   # agora é computado, não manual
        store=True
    )

    preco_unitario = fields.Float(
    string='Preço Unitário (R$)',
    compute='_compute_preco_unitario',
    store=True
    )  

    @api.depends('produto_id', 'pedido_id.cliente_id.perfil_cliente_id', 'quantidade')
    def _compute_preco_unitario(self):
        hoje = fields.Date.today()
        for item in self:
            preco_base = self.env['clinica.preco.base'].search([
                ('produto_id', '=', item.produto_id.id),
                ('data_inicio', '<=', hoje),
                '|',
                ('data_fim', '=', False),
                ('data_fim', '>=', hoje),
            ], order='data_inicio desc', limit=1)
            item.preco_unitario = preco_base.valor if preco_base else 0.0


    @api.depends('produto_id', 'quantidade', 'preco_unitario', 'pedido_id.cliente_id.perfil_cliente_id', 'pedido_id.item_ids.produto_id')
    def _compute_desconto_aplicado(self):
        hoje = fields.Date.today()
        for item in self:
            desconto = 0.0
            
            # 1. TENTA APLICAR A REGRA DE COMBINAÇÃO (BUNDLE)
            produtos_no_pedido = item.pedido_id.item_ids.mapped('produto_id').ids
            combinacao = self.env['clinica.combinacao.produto'].search([
                ('produto_principal_id', '=', item.produto_id.id),
                ('produto_relacionado_id', 'in', produtos_no_pedido)
            ], limit=1)

            if combinacao:
                # AGORA O CÓDIGO VAI LER SE É PERCENTUAL OU FIXO
                if combinacao.tipo_desconto == 'percentual':
                    # Calcula o percentual sobre o preço unitário
                    desconto = item.preco_unitario * (combinacao.valor_final / 100)
                else:
                    # Aplica o valor fixo (o que você estava fazendo antes)
                    desconto = combinacao.valor_final
            
            # 2. SE NÃO HOUVER COMBINAÇÃO, USA A REGRA DE PERFIL
            else:
                perfil_id = item.pedido_id.cliente_id.perfil_cliente_id.id
                if perfil_id and item.preco_unitario:
                    regra = self.env['clinica.regra.preco'].search([
                        ('produto_id', '=', item.produto_id.id),
                        ('perfil_cliente_id', '=', perfil_id),
                        ('quantidade_min', '<=', item.quantidade),
                        ('data_inicio', '<=', hoje),
                        '|',
                        ('data_fim', '=', False),
                        ('data_fim', '>=', hoje),
                    ], order='quantidade_min desc', limit=1)
                    if regra:
                        if regra.tipo_regra == 'percentual':
                            desconto = item.preco_unitario * (regra.desconto / 100)
                        else:
                            desconto = regra.desconto
            
            # Garantimos que o desconto é positivo
            item.desconto_aplicado = abs(desconto)

    @api.depends('preco_unitario', 'quantidade', 'desconto_aplicado')
    def _compute_valor_final(self):
        for item in self:
            # A CONTA É: PREÇO - DESCONTO
            # 10.00 - 5.00 = 5.00 (Valor de uma unidade)
            valor_unidade_com_desconto = item.preco_unitario - item.desconto_aplicado
            item.valor_final = valor_unidade_com_desconto * item.quantidade


class RelatorioPrecoWizard(models.TransientModel):
    _name = 'clinica.relatorio.preco.wizard'
    _description = 'Wizard de Relatório de Preços'

    data_inicio = fields.Date(string='Data Início', required=True, default=fields.Date.today)
    data_fim = fields.Date(string='Data Fim', required=True, default=fields.Date.today)

    def imprimir_relatorio(self):
            self.ensure_one() # Segurança para garantir que rodamos em um único wizard
            
            data_inicio_fmt = self.data_inicio.strftime('%d/%m/%Y')
            data_fim_fmt = self.data_fim.strftime('%d/%m/%Y')

            # Busca os preços vigentes no período
            precos = self.env['clinica.preco.base'].search([
                ('data_inicio', '<=', self.data_fim),
                '|',
                ('data_fim', '=', False),
                ('data_fim', '>=', self.data_inicio),
            ], order='produto_id, data_inicio desc')

            # 2. Passa as strings já formatadas para o dicionário 'data'
            data = {
                'ids': self.ids,
                'model': self._name,
                'form': {
                    'data_inicio': data_inicio_fmt, 
                    'data_fim': data_fim_fmt,
                },
                'precos': precos.ids,
            }
            
            return self.env.ref('odoo_sample_module.action_report_tabela_precos').report_action(self, data=data)