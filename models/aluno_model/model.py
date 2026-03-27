from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# =================================================================
# 1. PARCEIROS: CRÉDITOS, VALIDADE E MARKETING
# =================================================================
class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean(string="É Aluno", default=False)
    is_instructor = fields.Boolean(string="É Instrutor", default=False)
    
    credit_count = fields.Integer(string="Saldo de Créditos", default=0)
    credit_expiration = fields.Date(string="Validade dos Créditos")
    cost_center_id = fields.Many2one('account.analytic.account', string="Centro de Custo")
    last_lesson_date = fields.Datetime(string="Última Aula", readonly=True)
    nps_avg = fields.Float(string="NPS Médio", compute="_compute_nps_avg")

    def _compute_nps_avg(self):
        for rec in self:
            rec.nps_avg = 9.0 

# =================================================================
# 2. TURMA: CAPACIDADE E LISTA DE ESPERA 
# =================================================================
class StudioClass(models.Model):
    _name = 'studio.class'
    _description = 'Turma Planejada'

    name = fields.Char(string="Código da Turma", required=True)
    modality = fields.Selection([
        ('yoga', 'Yoga'), ('pilates', 'Pilates'), ('fitness', 'Funcional')
    ], string="Modalidade", required=True)
    
    credit_cost = fields.Integer(string="Custo em Créditos", default=1)
    capacity = fields.Integer(string="Capacidade Máxima", default=10)
    instructor_id = fields.Many2one('res.partner', string="Instrutor", domain=[('is_instructor', '=', True)])
    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.company)
    registration_ids = fields.One2many('studio.class.registration', 'class_id', string="Inscrições")
    seats_occupied = fields.Integer(string="Vagas Ocupadas", compute="_compute_seats")

    @api.depends('registration_ids.state')
    def _compute_seats(self):
        for rec in self:
            rec.seats_occupied = len(rec.registration_ids.filtered(lambda r: r.state == 'confirmed'))

# =================================================================
#  REGISTRO: TURMA
# =================================================================            

class StudioClassRegistration(models.Model):
    _name = 'studio.class.registration'
    _description = 'Registro de Inscrição'
    _order = 'sequence, id'

    sql_constraints = [
        ('unique_student_class', 'unique(class_id, student_id)', 'O aluno já está inscrito!')
    ]

    sequence = fields.Integer(default=10)
    class_id = fields.Many2one('studio.class', string="Turma", required=True)
    student_id = fields.Many2one('res.partner', string="Aluno", domain=[('is_student', '=', True)], required=True, ondelete='cascade')
    state = fields.Selection([('confirmed', 'Confirmado'), ('waiting', 'Lista de Espera')], string="Status", compute="_compute_state")

    @api.constrains('student_id', 'class_id')
    def _check_unique_registration(self):
        for rec in self:
            # Busca se existe OUTRO registro (id diferente) com o mesmo aluno e turma
            duplicates = self.env['studio.class.registration'].search([
                ('id', '!=', rec.id),
                ('student_id', '=', rec.student_id.id),
                ('class_id', '=', rec.class_id.id)
            ])
            if duplicates:
                raise ValidationError("Atenção! O aluno %s já está inscrito nesta turma." % rec.student_id.name)

    @api.depends('sequence', 'class_id.capacity')
    def _compute_state(self):
        for rec in self:
            prev_regs = self.search_count([('class_id', '=', rec.class_id.id), ('sequence', '<', rec.sequence)])
            rec.state = 'confirmed' if prev_regs < rec.class_id.capacity else 'waiting'

# =================================================================
# 3. AULA: CHECK-IN E REGRAS DE 4H 
# =================================================================
class StudioLesson(models.Model): 
    _name = 'studio.lesson'
    _description = 'Aula Realizada'

    # TRAVA: Impede criar dois registros para a mesma turma e horário
    _sql_constraints = [
        ('unique_lesson_per_class_date', 
         'unique(class_id, date)', 
         'Já existe um registro de aula para esta turma nesta data e hora!')
    ]

    class_id = fields.Many2one('studio.class', string="Turma", required=True, ondelete='cascade')
    date = fields.Datetime(string="Data da Aula", default=fields.Datetime.now)
    attendance_ids = fields.Many2many('res.partner', string="Check-in Realizado")
    state = fields.Selection([
        ('draft', 'Agendada'), ('done', 'Realizada'), ('cancel', 'Cancelada')
    ], default='draft', string="Status")

    # Memória para o faturamento saber se o cancelamento foi pago
    is_late_cancel = fields.Boolean(string="Cobrar Cancelamento", default=False, readonly=True)

    def action_confirm_attendance(self):
        """ Requisito: Controle de créditos no Check-in """
        cost = self.class_id.credit_cost
        for student in self.attendance_ids:
            if student.credit_expiration and student.credit_expiration < fields.Date.today():
                raise ValidationError("Créditos de %s expirados!" % student.name)
            if student.credit_count < cost:
                raise ValidationError("Saldo insuficiente para %s!" % student.name)
            
            student.credit_count -= cost
            student.last_lesson_date = fields.Datetime.now()
        self.state = 'done'

    def action_cancel_lesson(self):
        """ Regra de cancelamento de 4h (Executa em qualquer lugar do sistema) """
        # Se já estiver cancelada, interrompe para não devolver crédito duas vezes
        if self.state == 'cancel':
            return True
            
        # 1. Calcula o limite de 4 horas antes da aula
        limit_time = self.date - timedelta(hours=4)
        is_early = fields.Datetime.now() < limit_time
        
        # 2. Se for CEDO (is_early), devolve o crédito sempre (independente do status anterior)
        if is_early:
            cost = self.class_id.credit_cost
            for student in self.attendance_ids:
                student.credit_count += cost
            self.is_late_cancel = False 
        else:
            # 3. Se for TARDE, não devolve e marca para cobrar da empresa no faturamento
            self.is_late_cancel = True
        
        # 4. Muda o status para cancelado
        self.state = 'cancel'
        
# =================================================================
# 4. FATURAMENTO E RELATÓRIO 
# =================================================================
class StudioBilling(models.Model):
    _name = 'studio.billing'
    _description = 'Base para Faturamento Corporativo'

    company_id = fields.Many2one('res.company', string="Empresa", required=True)
    # Substituindo o Char por Date para permitir o intervalo
    date_from = fields.Date(string="Data Início", required=True)
    date_to = fields.Date(string="Data Fim", required=True)
    
    cost_center_id = fields.Many2one('account.analytic.account', string="Centro de Custo")
    total_consumption = fields.Float(string="Total de Créditos Consumidos")
    report_details = fields.Text(string="Detalhamento por Aluno")

    def action_generate_report(self):
        # Criamos um domínio que filtra pelo intervalo de datas e status
        domain = [
            ('state', 'in', ['done', 'cancel']),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to)
        ]
        
        lessons = self.env['studio.lesson'].search(domain)
        total = 0
        details = []

        for lesson in lessons:
            for student in lesson.attendance_ids:
                # Filtra pelo centro de custo do aluno se houver um definido no relatório
                if not self.cost_center_id or student.cost_center_id == self.cost_center_id:
                    # Fatura se: Aula concluída OU Cancelamento tardio
                    if lesson.state == 'done' or lesson.is_late_cancel:
                        total += lesson.class_id.credit_cost
                        status_str = "Presença" if lesson.state == 'done' else "Late Cancel (Pago)"
                        date_str = lesson.date.strftime('%d/%m/%Y %H:%M')
                        details.append(f"{student.name} - {date_str} ({status_str})")

        self.total_consumption = total
        self.report_details = "\n".join(details) if details else "Nenhum registro encontrado para este período."