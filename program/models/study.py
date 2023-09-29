import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Study(models.Model):
    _name = 'program.study'
    _description = "Study"

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True)
    code = fields.Char("Code", index=True, required=True, tracking=True, translate=True)
    description = fields.Html(required=True, translate=True)
    user_id = fields.Many2one('res.users', string='Study Manager', tracking=True, default=lambda self: self.env.user)
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
                                               "it will allow you to hide the study without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Studies.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    tag_ids = fields.Many2many('study.tags', relation='program_study_program_study_tags_rel', string='Tags')
    program_id = fields.Many2one('program.program', string='Program', tracking=True, check_company=True, required=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    deliverable_ids = fields.One2many('program.deliverable', 'study_id', string='Deliverables')

    @api.depends('deliverable_ids.planned_working_hours')
    def _compute_planned_working_hours(self):
        for study in self:
            study.planned_working_hours = sum(study.deliverable_ids.mapped('planned_working_hours'))

    @api.depends('deliverable_ids.effective_working_hours')
    def _compute_effective_working_hours(self):
        for study in self:
            study.effective_working_hours = sum(study.deliverable_ids.mapped('effective_working_hours'))

    @api.depends('planned_working_hours', 'effective_working_hours')
    def _compute_progress(self):
        for study in self:
            study.progress = sum(study.deliverable_ids.mapped('progress')) / len(
                study.deliverable_ids) if study.deliverable_ids else 0.0

    @api.depends('deliverable_ids.state')
    def _compute_state(self):
        ignored_study_states = ['cancel', 'hold']
        state_priority = {'planned': 0, 'in_progress': 1, 'done': 2, 'hold': 3, 'cancel': 4}
        for study in self:
            if study.state in ignored_study_states:
                continue
            if study.deliverable_ids:
                deliverable_states = [deliverable.state for deliverable in study.deliverable_ids]
                computed_state = max(deliverable_states,
                                     key=lambda state: state_priority[state]) if deliverable_states else 'planned'
                if computed_state != study.state:
                    _logger.info('Study %s state changed from %s to %s', study.name, study.state, computed_state)
                    study.state = computed_state


class StudyTags(models.Model):
    """ Tags of Study's tasks """
    _name = "program.study.tags"
    _description = "Study Tags"

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
