from os import environ

SESSION_CONFIGS = [
    dict(
        name='study_on_work',
        display_name="Study on Work",
        app_sequence=['instructions_consent', 'study'],
        num_demo_participants=10,
        participation_fee=11.0,
        work_length_seconds=120,
        use_browser_bots=False,
        set_treatment=False,
        treatment=False,
        prolific_completion_url='FILL THIS IN!',
        prolific_completion_code='FILL THIS IN!',
     ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.0015,
    participation_fee=0.0,
    doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ADMIN_USERNAME = 'admin'

# Security: ADMIN_PASSWORD must be set via environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
if not ADMIN_PASSWORD:
    import warnings
    warnings.warn(
        "OTREE_ADMIN_PASSWORD not set. Admin access may be unrestricted.",
        RuntimeWarning
    )

DEMO_PAGE_INTRO_HTML = """ """

# Security: SECRET_KEY must be set via environment variable in production
# Fallback provided for local development only
SECRET_KEY = environ.get('OTREE_SECRET_KEY', environ.get('SECRET_KEY'))
if not SECRET_KEY:
    import warnings
    warnings.warn(
        "OTREE_SECRET_KEY not set. Using insecure default for development only.",
        RuntimeWarning
    )
    SECRET_KEY = '1054327041868'
