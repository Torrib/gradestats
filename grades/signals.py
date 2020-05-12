from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Grade
from .utils import update_course_stats


@receiver(post_save, sender=Grade)
def update_course_stats_from_grade(sender, instance: Grade, **kwargs):
    update_course_stats(instance.course)
