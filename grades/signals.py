from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Grade, Report
from .utils import update_course_stats, send_report


@receiver(post_save, sender=Grade)
def update_course_stats_from_grade(sender, instance: Grade, **kwargs):
    update_course_stats(instance.course)


@receiver(post_save, sender=Report)
def send_mail_for_created_report(sender, instance: Report, created=False, **kwargs):
    if created:
        send_report(instance)
