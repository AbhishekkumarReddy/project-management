import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Task(models.Model):
    _name = 'program.task'
    _description = "Task"

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True)
    description = fields.Html(required=True, translate=True)
    user_id = fields.Many2one('res.users', string='Task Manager', tracking=True, default=lambda self: self.env.user)
    date_start = fields.Date(string='Start Date', index=True, tracking=True)
    date = fields.Date(string='Expiration Date', index=True, tracking=True)
    planned_working_hours = fields.Float(string='Planned Working Hours', default=0.0)
    effective_working_hours = fields.Float(string='Effective Working Hours', default=0.0)
    progress = fields.Float(string='Progress', compute='_compute_progress', group_operator="avg",
                            readonly=True, store=True)
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
                                               "it will allow you to hide the task without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Tasks.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    deliverable_id = fields.Many2one('program.deliverable', string='Deliverable', tracking=True,
                                     check_company=True, required=True,
                                     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    sub_task_ids = fields.One2many('program.sub_task', 'task_id', string='Sub Tasks')
    study_id = fields.Many2one('program.study', string='Study', related='deliverable_id.study_id', store=True,
                               readonly=True)
    program_id = fields.Many2one('program.program', string='Program', related='study_id.program_id', store=True,
                                 readonly=True)

    @api.depends('planned_working_hours', 'effective_working_hours')
    def _compute_progress(self):
        for task in self:
            task.progress = task.effective_working_hours / task.planned_working_hours * 100 \
                if task.planned_working_hours else 0.0

    @api.depends('sub_task_ids.state')
    def _compute_state(self):
        ignored_task_states = ['cancel', 'hold']
        state_priority = {'planned': 0, 'in_progress': 1, 'done': 2, 'hold': 3, 'cancel': 4}
        for task in self:
            if task.state in ignored_task_states:
                continue
            if task.sub_task_ids:
                sub_task_states = [sub_task.state for sub_task in task.sub_task_ids]
                computed_state = max(sub_task_states, key=lambda x: state_priority[x])
                if computed_state != task.state:
                    _logger.info('Task %s state changed from %s to %s', task.name, task.state, computed_state)
                    task.state = computed_state
