# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import ExpressionWrapper, F
from django.db.models.signals import post_init
from collections import OrderedDict
from django.urls import reverse


class CourseManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.distinct()


class Course(models.Model):
    objects = CourseManager()

    norwegian_name = models.CharField("Norwegian Name", max_length=255)
    short_name = models.CharField("Short name", max_length=50)
    code = models.CharField("Code", max_length=15)
    faculty_code = models.IntegerField("Faculty Code", default=0)
    exam_type = models.CharField("Exam Type", max_length=255, default="")
    grade_type = models.CharField("Grade Type", max_length=255, default="")
    place = models.CharField("Place", max_length=255, default="")
    have_had_digital_exam = models.BooleanField(default=False)

    english_name = models.CharField("English name", max_length=255)
    credit = models.FloatField("Credit", default=7.5)
    study_level = models.SmallIntegerField()
    taught_in_spring = models.BooleanField(default=False)
    taught_in_autumn = models.BooleanField(default=False)
    taught_from = models.IntegerField()
    taught_in_english = models.BooleanField(default=False)
    last_year_taught = models.IntegerField(default=0)

    content = models.TextField()
    learning_form = models.TextField()
    learning_goal = models.TextField()

    average = 0
    watson_rank = 0.0
    attendee_count = 0

    def course_level(self):
        if self.study_level < 300:
            return "Grunnleggende"
        elif self.study_level < 500:
            return "Videregående"
        elif self.study_level < 900:
            return "Avansert"
        else:
            return "Doktorgrad"

    def __unicode__(self):
        return self.code

    def __str__(self):
        return self.code

    # FIX Permalink depercated
    def get_absolute_url(self):
        return reverse("course", kwargs={"course_code": self.code})


class GradeManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                attendee_count=ExpressionWrapper(
                    F("a") + F("b") + F("c") + F("d") + F("e") + F("f") + F("passed"),
                    output_field=models.IntegerField(),
                )
            )
        )


class Grade(models.Model):
    objects = GradeManager()

    course = models.ForeignKey(Course, related_name="grades", on_delete=models.CASCADE)
    semester_code = models.CharField("Semester", max_length=10)

    average_grade = models.FloatField()
    digital_exam = models.BooleanField(default=False)

    passed = models.IntegerField(default=0)
    a = models.SmallIntegerField(default=0)
    b = models.SmallIntegerField(default=0)
    c = models.SmallIntegerField(default=0)
    d = models.SmallIntegerField(default=0)
    e = models.SmallIntegerField(default=0)
    f = models.SmallIntegerField(default=0)

    def __unicode__(self):
        return self.semester_code

    def get_num_attendees(self):
        return self.a + self.b + self.c + self.d + self.e + self.f

    class Meta:
        default_manager_name = 'objects'


class Tag(models.Model):
    courses = models.ManyToManyField(Course, related_name="tags")
    tag = models.CharField("Tag text", max_length=32)

    def __unicode__(self):
        return self.tag


class NavbarItems(object):
    @staticmethod
    def get_items():
        items = OrderedDict(
            [
                ("index", "Fag"),
                ("about", "Om siden"),
                ("report", "Rapporter feil"),
                ("api", "API"),
            ]
        )
        return items


class Faculties(object):
    @staticmethod
    def get_faculties():
        faculties = dict()
        faculties["60"] = u"(ØK) Fakultet for økonomi"
        faculties["61"] = u"(AD) Fakultet for arkitektur og design"
        faculties["62"] = u"(HF) Det humanistiske fakultet"
        faculties["63"] = u"(IE) Fakultet for informasjonsteknologi og elektroteknikk "
        faculties["64"] = u"(IV) Fakultet for ingeniørvitenskap"
        faculties["65"] = u"(MH) Fakultet for medisin og helsevitenskap"
        faculties["66"] = u"(NV) Fakultet for naturvitenskap"
        faculties["67"] = u"(SU) Fakultet for samfunns- og utdanningsvitenskap"
        return faculties


def get_average_grade(**kwargs):
    course = kwargs.get("instance")
    grades = course.grades.all()
    course.average = 0
    attendees = 0
    for grade in grades:
        attendees += grade.get_num_attendees()
        course.average += grade.average_grade * grade.get_num_attendees()
    if attendees == 0:
        return
    else:
        course.average /= attendees
        return


post_init.connect(get_average_grade, Course)
