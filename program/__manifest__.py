{
    'name': 'Program',
    'version': '1.0',
    'summary': 'Summary',
    'license': 'LGPL-3',
    'description': 'Program',
    'category': 'Project Management',
    'author': 'Abhishek Reddy',
    'depends': [
        'analytic',
        'base_setup',
        'mail',
        'portal',
        'rating',
        'resource',
        'web',
        'web_tour',
        'digest',
        'board',
    ],
    'data': [
        'security/program_security.xml',
        'security/ir.model.access.csv',
        'views/program_views.xml',
        'views/study_views.xml',
        'views/deliverable_views.xml',
        'views/task_views.xml',
        'views/sub_task_views.xml',
        'views/phase_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'program/static/src/**/*.scss'
        ],
        'web.qunit_suite_tests': [
            'program/static/tests/**/*',
            ('remove', 'program/static/tests/mobile/**/*'), # mobile test
        ],
        'web.qunit_mobile_suite_tests': [
            'program/static/tests/mobile/**/*',
        ],
        'web.assets_qweb': [
            'program/static/src/**/*.xml',
        ],
    },
}
