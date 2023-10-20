# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import logging

from ckanext.agesic.controllers.email import SendNotificationController

log = logging.getLogger(__name__)


def get_commands():
    return [agesic]


@click.group(short_help=u"AGESIC commands")
def agesic():
    pass


@agesic.command(short_help=u"Send notification email")
def send_notification_mail():
    log.info("Sending notification mail")
    SendNotificationController().send_notification_mail()


@agesic.command(short_help=u"Send test email")
def send_test_mail():
    log.info("Sending test mail")
    SendNotificationController().send_test_mail()
