from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import sendgrid
from app import app

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


def generateToken(email):
    return serializer.dumps(email, salt=app.config['EMAIL_CONF_SALT'])


def decodeToken(token):
    email = serializer.loads(
        token,
        salt = app.config['EMAIL_CONF_SALT'],
        max_age = app.config['CONFIRM_EMAIL_EXP']
    )
    return email


def sendEmail(to_email, subject, body):
    """Use sendgrid's api to send email from noreply@snip.space"""
    sg = sendgrid.SendGridClient(
        app.config['SENDGRID_API_USER'],
        app.config['SENDGRID_API_KEY']
    )
    message = sendgrid.Mail()
    message.add_to(to_email)
    message.set_from('noreply@snip.space')
    message.set_subject(subject)
    message.set_html(body)

    sg.send(message)