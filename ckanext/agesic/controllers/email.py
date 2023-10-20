import smtplib
import logging
from email.mime.text import MIMEText

from ckan.common import config
from ckan.lib.mailer import mail_recipient
from ckan.model import Session, User, Member, Package
from ckan.lib.base import render

log = logging.getLogger(__name__)


class SendNotificationController:

    def __send(self, agesic_email):
        try:
            log.debug('Sending email to %s' % agesic_email.get('recipient_email'))
            mail_recipient(**agesic_email)
            log.debug('Sent mail to %s' % agesic_email.get('recipient_email'))
            return
        except smtplib.SMTPRecipientsRefused:
            log.error("ERROR: SMTPRecipientsRefused")
        except smtplib.SMTPServerDisconnected:
            log.error("ERROR: SMTPServerDisconnected")
        except Exception as e:
            log.error("ERROR: SMTP %s" % str(e))
        raise Exception("Something wrong sending mail")

    def send_notification_mail(self):
        recipients = set()
        for user in Session.query(User).join(
                Member, User.id == Member.table_id).filter(
                User.state == 'active', Member.state == 'active').all():
            if user.email:
                recipients.add(user.email.strip())
        for p in Session.query(Package).filter(Package.type == 'dataset'):
            # ignore private and deleted datasets
            if p.private or p.state == 'deleted':
                continue
            if p.author_email:
                recipients.add(p.author_email.strip())
            if p.maintainer_email:
                recipients.add(p.maintainer_email.strip())

        for email in recipients:
            try:
                attach = MIMEText(open('ckanext/agesic/templates/emails/send_notifications.html').read(),
                                  'html', 'utf-8')
                agesic_email = {'recipient_name': '',
                                'recipient_email': email,
                                'subject': 'Indisponibilidad del Catálogo Nacional de Datos Abiertos.',
                                'body': '',
                                'headers': {},
                                'attachment': attach}
                self.__send(agesic_email)
            except Exception as e:
                log.error("ERROR: %s" % str(e))

    def send_test_mail(self):
        try:
            email = config.get('agesic.administrator_email')
            log.info('Sending test email to %s' % email)
            agesic_email = {'recipient_name': '',
                            'recipient_email': email,
                            'subject': 'Correo de pruebas de Catálogo de Datos.',
                            'body': 'Borrar este mensaje',
                            'headers': {}}
            self.__send(agesic_email)
            log.info("Sent test mail to %s" % email)
        except Exception as e:
            log.error("ERROR: %s" % str(e))

    def send_package_create_notification(self, extra_vars):
        body = render('emails/package_create_notification.txt', extra_vars)
        body_html = render('emails/package_create_notification.html', extra_vars)
        try:
            agesic_email = {'recipient_name': '',
                            'recipient_email': config.get('agesic.administrator_email'),
                            'subject': 'Aviso de conjunto de datos creado',
                            'body': body,
                            'body_html': body_html,
                            'headers': {}}
            self.__send(agesic_email)
        except Exception as e:
            log.error("ERROR: %s" % str(e))

    def send_package_update_notification(self, extra_vars):
        body_html = render('emails/package_update_notification.html', extra_vars)
        try:
            agesic_email = {'recipient_name': '',
                            'recipient_email': config.get('agesic.administrator_email'),
                            'subject': 'Aviso de conjunto de datos actualizado',
                            'body': '',
                            'body_html': body_html,
                            'headers': {}}
            self.__send(agesic_email)
        except Exception as e:
            log.error("ERROR: %s" % str(e))
