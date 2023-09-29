import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Deliverable(models.Model):
    _name = 'program.deliverable'
    _description = "Deliverable"

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True)
    description = fields.Html(required=True, translate=True)
    user_id = fields.Many2one('res.users', string='Deliverable Manager', tracking=True,
                              default=lambda self: self.env.user)
    date_start = fields.Date(string='Start Date', index=True, tracking=True)
    date = fields.Date(string='Expiration Date', index=True, tracking=True)
    planned_working_hours = fields.Float(string='Planned Working Hours', compute='_compute_planned_working_hours',
                                         store=True)
    effective_working_hours = fields.Float(string='Effective Working Hours', compute='_compute_effective_working_hours',
                                           store=True)
    progress = fields.Float(string='Progress', compute='_compute_progress', group_operator="avg", store=True)
    state = fields.Selection([
        ('planned', 'Yet to Start'), ('in_progress', 'In Progress'),
        ('done', 'Done'), ('hold', 'On Hold'),
        ('cancel', 'Cancelled')], string='Status',
        copy=False, default='planned', index=True, tracking=True, required=True,
        help="* Yet to Start: The Program is yet to begin.\n"
             "* In Progress: The Program is currently being worked on by the team.\n"
             "* Done: When work on the project is finished, and all deliverables/tasks have been completed, "
             "the state is \'Done\'."
             "* On Hold:  The program has not finished, and work on the program has been temporarily suspended.\n"
             "* Cancelled: The Program has not finished, and work on the program will not continue.\n",
        compute='_compute_state', store=True
    )

    active = fields.Boolean(default=True, help="If the active field is set to False, "
                                               "it will allow you to hide the deliverable without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Deliverables.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    study_id = fields.Many2one('program.study', string='Study', tracking=True, check_company=True, required=True,
                               domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    task_ids = fields.One2many('program.task', 'deliverable_id', string='Tasks')
    program_id = fields.Many2one('program.program', string='Program', related='study_id.program_id', store=True,
                                 readonly=True)

    @api.depends('task_ids.planned_working_hours')
    def _compute_planned_working_hours(self):
        for deliverable in self:
            deliverable.planned_working_hours = sum(deliverable.task_ids.mapped('planned_working_hours'))

    @api.depends('task_ids.effective_working_hours')
    def _compute_effective_working_hours(self):
        for deliverable in self:
            deliverable.effective_working_hours = sum(deliverable.task_ids.mapped('effective_working_hours'))

    @api.depends('planned_working_hours', 'effective_working_hours')
    def _compute_progress(self):
        for deliverable in self:
            deliverable.progress = sum(deliverable.task_ids.mapped('progress')) / len(
                deliverable.task_ids) if deliverable.task_ids else 0.0

    @api.depends('task_ids.state')
    def _compute_state(self):
        ignored_deliverable_states = ['cancel', 'hold']
        state_priority = {'planned': 0, 'in_progress': 1, 'done': 2, 'hold': 3, 'cancel': 4}
        for deliverable in self:
            if deliverable.state in ignored_deliverable_states:
                continue
            if deliverable.task_ids:
                task_states = [task.state for task in deliverable.task_ids]
                computed_state = max(task_states, key=lambda state: state_priority[state]) if task_states else 'planned'
                if computed_state != deliverable.state:
                    _logger.info('Deliverable %s state changed from %s to %s', deliverable.name, deliverable.state,
                                 computed_state)
                    deliverable.state = computed_state
