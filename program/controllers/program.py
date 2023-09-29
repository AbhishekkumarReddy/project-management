import json

from odoo import http

from odoo.http import request, Response


class ProgramController(http.Controller):

    # api route to recompute the statuses
    @http.route('/program/status/recompute', auth='public', type='http', website=True, methods=['GET'])
    def recompute_status(self, **kw):
        programs = request.env['program.program'].search([])
        state_field = request.env['program.program']._fields['state']
        request.env.add_to_compute(state_field, programs)
        return Response(json.dumps({'status': 'recomputed'}), content_type='application/json')

    # api route to recompute the statuses of study
    @http.route('/study/status/recompute', auth='public', type='http', website=True, methods=['GET'])
    def recompute_study_status(self, **kw):
        studies = request.env['program.study'].search([])
        state_field = request.env['program.study']._fields['state']
        request.env.add_to_compute(state_field, studies)
        return Response(json.dumps({'status': 'recomputed'}), content_type='application/json')

    # api route to recompute the statuses of deliverable
    @http.route('/deliverable/status/recompute', auth='public', type='http', website=True, methods=['GET'])
    def recompute_deliverable_status(self, **kw):
        deliverables = request.env['program.deliverable'].search([])
        state_field = request.env['program.deliverable']._fields['state']
        request.env.add_to_compute(state_field, deliverables)
        return Response(json.dumps({'status': 'recomputed'}), content_type='application/json')

    # api route to recompute the statuses of task
    @http.route('/task/status/recompute', auth='public', type='http', website=True, methods=['GET'])
    def recompute_task_status(self, **kw):
        tasks = request.env['program.task'].search([])
        state_field = request.env['program.task']._fields['state']
        request.env.add_to_compute(state_field, tasks)
        return Response(json.dumps({'status': 'recomputed'}), content_type='application/json')

    # api route to recompute the statuses of sub task
    @http.route('/sub_task/status/recompute', auth='public', type='http', website=True, methods=['GET'])
    def recompute_sub_task_status(self, **kw):
        sub_tasks = request.env['program.sub_task'].search([])
        state_field = request.env['program.sub_task']._fields['state']
        request.env.add_to_compute(state_field, sub_tasks)
        return Response(json.dumps({'status': 'recomputed'}), content_type='application/json')
