DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgres://user:pass@localhost/db_name'

SERVER_NAME = 'localhost:5000' # External server name

SECRET_KEY = 'your secret key' # Application secret key

HASHID_SALT = '3x4mpl3_s4Lt' # Salt used for creating snippet UUID
HASHID_LEN = 5 # Minimum length in chars for snippet UUID hash

SENDGRID_API_USER = 'sendgrid_username'
SENDGRID_API_KEY = 'sendgrid_password'

EMAIL_CONF_SALT = '3x4mpl3_s4Lt_2' # Salt used for generating email confirmation token
CONFIRM_EMAIL_EXP = 3600 # Time in seconds before confirmation expires

SNIPPETS_PER_PAGE = 10

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

