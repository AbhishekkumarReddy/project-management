from odoo import models, fields, api

from odoo.exceptions import ValidationError


class Phase(models.Model):
    _name = "subtask.phase"
    _description = "Phase"

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True)
    description = fields.Html(required=True, translate=True)
    end_phase = fields.Boolean(string='End Phase')
    active = fields.Boolean(default=True, help="If the active field is set to False, "
                                               "it will allow you to hide the phase without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Phases.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'There can be only one phase with this name!'),
    ]

    @api.constrains('end_phase')
    def end_phase_check(self):
        if self.end_phase:
            if self.search_count([('end_phase', '=', True)]) > 1:
                raise ValidationError("There can be only one end phase!")
