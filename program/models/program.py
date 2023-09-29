import logging
from random import randint

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class Program(models.Model):
    _name = 'program.program'
    _description = "Program"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = "sequence, name, id"
    _check_company_auto = True

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True)
    code = fields.Char("Code", index=True, required=True, tracking=True, translate=True)
    description = fields.Html(required=True, translate=True)
    partner_id = fields.Many2one('res.partner', string='Customer', auto_join=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    user_id = fields.Many2one('res.users', string='Program Manager', tracking=True, default=lambda self: self.env.user)
    date_start = fields.Date(string='Start Date', index=True, tracking=True)
    date = fields.Date(string='Expiration Date', index=True, tracking=True)
    planned_working_hours = fields.Float(string='Planned Working Hours', compute='_compute_planned_working_hours',
                                         store=True)
    effective_working_hours = fields.Float(string='Effective Working Hours', compute='_compute_effective_working_hours',
                                           store=True)
    progress = fields.Float(string='Progress', compute='_compute_progress', store=True, group_operator="avg")
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
                                               "it will allow you to hide the program without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Projects.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    study_ids = fields.One2many('program.study', 'program_id', string='Studies')
    tag_ids = fields.Many2many('program.tags', relation='program_program_program_tags_rel', string='Tags')

    _sql_constraints = [
        ('program_name_uniq', 'unique (name)', "Tag name already exists!"),
        ('program_code_uniq', 'unique (code)', "Tag code already exists!")
    ]

    def action_view_tasks(self):
        action = self.env.ref('project.action_view_task').read()[0]
        action['domain'] = [('program_id', '=', self.id)]
        return action

    def action_view_studies(self):
        action = self.env.ref('program.action_program_study').read()[0]
        action['domain'] = [('program_id', '=', self.id)]
        return action

    @api.depends('study_ids.planned_working_hours')
    def _compute_planned_working_hours(self):
        for program in self:
            program.planned_working_hours = sum(program.study_ids.mapped('planned_working_hours'))

    @api.depends('study_ids.effective_working_hours')
    def _compute_effective_working_hours(self):
        for program in self:
            program.effective_working_hours = sum(program.study_ids.mapped('effective_working_hours'))

    @api.depends('planned_working_hours', 'effective_working_hours')
    def _compute_progress(self):
        for program in self:
            program.progress = sum(program.study_ids.mapped('progress')) / len(
                program.study_ids) if program.study_ids else 0.0

    @api.depends('study_ids.state')
    def _compute_state(self):
        ignored_program_states = ['cancel', 'hold']
        state_priority = {'planned': 0, 'in_progress': 1, 'done': 2, 'hold': 3, 'cancel': 4}
        for program in self:
            if program.state in ignored_program_states:
                continue
            if program.study_ids:
                study_states = [study.state for study in program.study_ids]
                computed_state = max(study_states,
                                     key=lambda state: state_priority[state]) if study_states else 'planned'
                if computed_state != program.state:
                    _logger.info('Program %s state changed from %s to %s', program.name, program.state, computed_state)
                    program.state = computed_state


def _get_default_color():
    return randint(1, 11)


class ProgramTags(models.Model):
    """ Tags of Program's tasks """
    _name = "program.tags"
    _description = "Program Tags"

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('tag_name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
