import logging

from odoo import models, fields, api

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SubTask(models.Model):
    _name = 'program.sub_task'
    _description = "Sub Task"

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True)
    description = fields.Html(required=True, translate=True)
    user_id = fields.Many2one('res.users', string='Sub Task Manager', tracking=True, default=lambda self: self.env.user)
    date_start = fields.Date(string='Start Date', index=True, tracking=True)
    date = fields.Date(string='Expiration Date', index=True, tracking=True)
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
        compute='_compute_state', store=True)

    active = fields.Boolean(default=True, help="If the active field is set to False, "
                                               "it will allow you to hide the task without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Tasks.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    task_id = fields.Many2one('program.task', string='Task', tracking=True, check_company=True, required=True,
                              domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    sub_task_phase_ids = fields.One2many('program.sub_task.phase', 'sub_task_id',
                                         string='Sub Task Phases')
    deliverable_id = fields.Many2one('program.deliverable', string='Deliverable', related='task_id.deliverable_id',
                                     store=True, readonly=True)
    study_id = fields.Many2one('program.study', string='Study', related='deliverable_id.study_id', store=True,
                               readonly=True)
    program_id = fields.Many2one('program.program', string='Program', related='study_id.program_id', store=True,
                                 readonly=True)

    @api.model
    def create(self, vals):
        res = super(SubTask, self).create(vals)
        subtask_phases = self.env['subtask.phase'].search([])
        for phase in subtask_phases:
            self.env['program.sub_task.phase'].create({
                'name': phase.name,
                'description': phase.description,
                'sequence': phase.sequence,
                'sub_task_id': res.id,
                'phase_id': phase.id,
                'user_id': res.user_id.id,
                'status': 'planned'
            })
        return res

    @api.depends('sub_task_phase_ids.status')
    def _compute_state(self):
        ignored_task_states = ['cancel', 'hold']
        state_priority = {'in_progress': 1, 'planned': 2, 'done': 3, 'na': 4}
        for sub_task in self:
            if sub_task.state in ignored_task_states:
                continue
            if sub_task.sub_task_phase_ids:
                state = sorted(sub_task.sub_task_phase_ids.mapped('status'), key=lambda x: state_priority[x])[0]
                if sub_task.state != state:
                    sub_task.state = 'hold' if state == 'na' else state
                    _logger.info("Sub Task %s: state changed from %s to %s", sub_task.name, sub_task.state, state)


class SubTaskPhase(models.Model):
    """ Phases of Sub Task """
    _name = "program.sub_task.phase"
    _description = "Sub Task Phase"

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True,
                       compute='_compute_name', readonly=True)
    description = fields.Html(required=True, translate=True)
    comment = fields.Text('Comments')
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Phases.")
    sub_task_id = fields.Many2one('program.sub_task', string='Sub Task', tracking=True,
                                  check_company=True, required=True,
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    phase_id = fields.Many2one('subtask.phase', string='Phase', tracking=True,
                               check_company=True, required=True,
                               domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    user_id = fields.Many2one('res.users', string='Responsible', required=True,
                              tracking=True, default=lambda self: self.env.user)
    status = fields.Selection([('planned', 'Yet to Start'),
                               ('in_progress', 'In Progress'),
                               ('done', 'Done'), ('na', 'N/A')], string='Status',
        copy=False, default='planned', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def _compute_name(self):
        for phase in self:
            phase.name = phase.sub_task_id.name + ' - ' + phase.phase_id.name

    @api.constrains('status')
    def _check_status(self):
        for phase in self:
            if phase.phase_id.end_phase and phase.status == 'done':
                if phase.sub_task_id.sub_task_phase_ids.filtered(lambda p: p.status != 'done' and p.id != phase.id):
                    raise ValidationError("You cannot close the phase as it is an end phase and "
                                          "there are other phases which are not yet completed")
