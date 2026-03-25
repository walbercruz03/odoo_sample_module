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
    
    # Requisito: Visibilidade de créditos e validade 
    credit_count = fields.Integer(string="Saldo de Créditos", default=0)
    credit_expiration = fields.Date(string="Validade dos Créditos")
    
    # Requisito: Alunos corporativos e centro de custo 
    cost_center_id = fields.Many2one('account.analytic.account', string="Centro de Custo")

    # Requisito: Dados para Marketing (Churn/Retenção) 
    last_lesson_date = fields.Datetime(string="Última Aula", readonly=True)
    nps_avg = fields.Float(string="NPS Médio", compute="_compute_nps_avg")

    def _compute_nps_avg(self):
        # Lógica simplificada para fins de MVP
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
    
    # Requisito: Preço Dinâmico 
    credit_cost = fields.Integer(string="Custo em Créditos", default=1)
    
    capacity = fields.Integer(string="Capacidade Máxima", default=10)
    instructor_id = fields.Many2one('res.partner', string="Instrutor", domain=[('is_instructor', '=', True)])
    
    # Requisito: Multi-company 
    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.company)

    # Requisito: Lista de Espera Automática 
    registration_ids = fields.One2many('studio.class.registration', 'class_id', string="Inscrições")
    seats_occupied = fields.Integer(string="Vagas Ocupadas", compute="_compute_seats")

    @api.depends('registration_ids.state')
    def _compute_seats(self):
        for rec in self:
            rec.seats_occupied = len(rec.registration_ids.filtered(lambda r: r.state == 'confirmed'))

class StudioClassRegistration(models.Model):
    _name = 'studio.class.registration'
    _description = 'Registro de Inscrição'
    _order = 'sequence, id'

    # impede aluno duplicado na turma
    _sql_constraints = [
        (
            'unique_student_class',
            'unique(class_id, student_id)',
            'O aluno já está inscrito nesta turma!'
        )
    ]

    sequence = fields.Integer(default=10)

    class_id = fields.Many2one(
        'studio.class',
        string="Turma",
        required=True
    )

    student_id = fields.Many2one(
        'res.partner',
        string="Aluno",
        domain=[('is_student', '=', True)],
        required=True,
        ondelete='cascade'
    )

    state = fields.Selection([
        ('confirmed', 'Confirmado'),
        ('waiting', 'Lista de Espera')
    ],
    string="Status",
    compute="_compute_state",
    store=True
    )


    @api.depends('sequence', 'class_id.capacity')
    def _compute_state(self):
        for rec in self:
            prev_regs = self.search_count([
                ('class_id', '=', rec.class_id.id),
                ('sequence', '<', rec.sequence)
            ])
            rec.state = 'confirmed' if prev_regs < rec.class_id.capacity else 'waiting'

# =================================================================
# 3. AULA: CHECK-IN E REGRAS DE 4H 
# =================================================================
class StudioLesson(models.Model): 

    _name = 'studio.lesson'
    _description = 'Aula Realizada'

    class_id = fields.Many2one('studio.class', string="Turma", required=True, ondelete='cascade')
    date = fields.Datetime(string="Data da Aula", default=fields.Datetime.now)
    attendance_ids = fields.Many2many('res.partner', string="Check-in Realizado")
    state = fields.Selection([
        ('draft', 'Agendada'), ('done', 'Realizada'), ('cancel', 'Cancelada')
    ], default='draft', string="Status")

    def action_confirm_attendance(self):
        """ Requisito: Controle de créditos no Check-in """
        cost = self.class_id.credit_cost
        for student in self.attendance_ids:
            if student.credit_expiration and student.credit_expiration < fields.Date.today():
                raise ValidationError(_("Créditos do aluno %s estão expirados!") % student.name)
            if student.credit_count < cost:
                raise ValidationError(_("Saldo insuficiente para %s!") % student.name)
            
            student.credit_count -= cost
            student.last_lesson_date = fields.Datetime.now()
        self.state = 'done'

    def action_cancel_lesson(self):
        """ Requisito: Regra de cancelamento de 4h  """
        if self.state == 'cancel':
            return True
            
        limit_time = self.date - timedelta(hours=4)
        is_late = fields.Datetime.now() > limit_time
        
        if not is_late:
            # Requisito: Devolve crédito se > 4h 
            cost = self.class_id.credit_cost
            for student in self.attendance_ids:
                student.credit_count += cost
        
        self.state = 'cancel'

# =================================================================
# 4. FATURAMENTO E RELATÓRIO 
# =================================================================
class StudioBilling(models.Model):
    _name = 'studio.billing'
    _description = 'Base para Faturamento Corporativo'

    company_id = fields.Many2one('res.company', string="Empresa", required=True)
    period = fields.Char(string="Período (MM/AAAA)", required=True)
    cost_center_id = fields.Many2one('account.analytic.account', string="Centro de Custo")
    total_consumption = fields.Float(string="Total de Créditos Consumidos")
    report_details = fields.Text(string="Detalhamento por Aluno")

    def action_generate_report(self):

        lessons = self.env['studio.lesson'].search([
            ('state', '=', 'done')
        ])

        total = 0
        details = []

        for lesson in lessons:
            cost = lesson.class_id.credit_cost

            for student in lesson.attendance_ids:
                if student.cost_center_id == self.cost_center_id:
                    total += cost
                    details.append(f"{student.name} - {lesson.date}")

        self.total_consumption = total
        self.report_details = "\n".join(details)