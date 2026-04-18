from __future__ import annotations

RULES = [
    {
        'id': 'feedback_visibility',
        'name': 'Feedback visibility',
        'weight': 1.2,
        'description': 'Users should get visible status and feedback during interaction.',
    },
    {
        'id': 'clear_structure',
        'name': 'Clear structure',
        'weight': 1.0,
        'description': 'Views should expose clear heading, title, and main landmarks.',
    },
    {
        'id': 'form_clarity',
        'name': 'Form clarity',
        'weight': 1.2,
        'description': 'Interactive forms should provide labels or accessible naming.',
    },
    {
        'id': 'consistency',
        'name': 'Consistency and standards',
        'weight': 1.0,
        'description': 'Area base templates should provide consistent navigation and shell affordances.',
    },
    {
        'id': 'error_recovery',
        'name': 'Error prevention and recovery',
        'weight': 1.1,
        'description': 'Views should expose alerts, status regions, or visible recovery affordances.',
    },
    {
        'id': 'accessibility',
        'name': 'Accessibility support',
        'weight': 1.4,
        'description': 'Views should expose accessibility signals such as labels, live regions, and landmarks.',
    },
    {
        'id': 'contract_alignment',
        'name': 'Contract alignment',
        'weight': 1.1,
        'description': 'UI surfaces should have discoverable relevant contracts or guidance.',
    },
    {
        'id': 'templatify_alignment',
        'name': 'Templatify alignment',
        'weight': 0.9,
        'description': 'Area shell information should align with templatify base block mappings where available.',
    },
]
