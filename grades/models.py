from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Concat
from django.db.models import ExpressionWrapper, F, Case, When, Value
from collections import OrderedDict
from django.urls import reverse


User = get_user_model()


class CourseManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(attendee_count__gt=4)
            .annotate(watson_rank=models.Value(1.0, output_field=models.FloatField()))
        )
        return queryset.distinct()


class Course(models.Model):
    objects = CourseManager()

    norwegian_name = models.CharField("Norwegian Name", max_length=255)
    short_name = models.CharField("Short name", max_length=50)
    code = models.CharField("Code", max_length=15, unique=True)
    faculty_code = models.IntegerField("Faculty Code", default=0)
    exam_type = models.CharField("Exam Type", max_length=255, default="")
    grade_type = models.CharField("Grade Type", max_length=255, default="")
    place = models.CharField("Place", max_length=255, default="")
    has_had_digital_exam = models.BooleanField(default=False)

    english_name = models.CharField("English name", max_length=255)
    credit = models.FloatField("Credit", default=7.5)
    study_level = models.SmallIntegerField(default=0)
    taught_in_spring = models.BooleanField(default=False)
    taught_in_autumn = models.BooleanField(default=False)
    taught_from = models.IntegerField(default=0)
    taught_in_english = models.BooleanField(default=False)
    last_year_taught = models.IntegerField(default=0)

    content = models.TextField()
    learning_form = models.TextField()
    learning_goal = models.TextField()

    average = models.FloatField(default=0)
    attendee_count = models.IntegerField(default=0)

    department = models.ForeignKey(
        to="Department", related_name="courses", on_delete=models.SET_NULL, null=True
    )

    watson_rank = 0.0

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


class Semester(models.TextChoices):
    SPRING = "SPRING", "Vår"
    SUMMER = "SUMMER", "Sommer"
    AUTUMN = "AUTUMN", "Høst"


class GradeManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(course__attendee_count__gt=4)
            .annotate(
                attendee_count=ExpressionWrapper(
                    F("a") + F("b") + F("c") + F("d") + F("e") + F("f") + F("passed"),
                    output_field=models.IntegerField(),
                )
            )
            .annotate(
                semester_letter=Case(
                    When(semester=Semester.SPRING, then=Value("V")),
                    When(semester=Semester.SUMMER, then=Value("S")),
                    When(semester=Semester.AUTUMN, then=Value("H")),
                    output_field=models.CharField(),
                )
            )
            .annotate(
                semester_code=Concat(
                    F("semester_letter"), F("year"), output_field=models.CharField(),
                )
            )
        )


class Grade(models.Model):
    objects = GradeManager()

    course = models.ForeignKey(Course, related_name="grades", on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField("År")
    semester = models.CharField("Semester", max_length=32, choices=Semester.choices)

    average_grade = models.FloatField()
    digital_exam = models.BooleanField(default=False)

    passed = models.IntegerField(default=0)
    a = models.SmallIntegerField(default=0)
    b = models.SmallIntegerField(default=0)
    c = models.SmallIntegerField(default=0)
    d = models.SmallIntegerField(default=0)
    e = models.SmallIntegerField(default=0)
    f = models.SmallIntegerField(default=0)

    @property
    def _semester_letter(self):
        lookup = {
            str(Semester.SPRING): "V",
            str(Semester.SUMMER): "S",
            str(Semester.AUTUMN): "H",
        }
        return lookup[self.semester]

    def __unicode__(self):
        return f"{self._semester_letter}{self.year}"

    def __str__(self):
        return f"{self._semester_letter}{self.year}"

    def get_num_attendees(self):
        return self.a + self.b + self.c + self.d + self.e + self.f

    class Meta:
        default_manager_name = "objects"
        unique_together = (("course", "semester", "year",),)


class Tag(models.Model):
    courses = models.ManyToManyField(Course, related_name="tags", through="CourseTag")
    tag = models.CharField("Tag text", max_length=32)

    def __unicode__(self):
        return self.tag

    def __str__(self):
        return self.tag


class CourseTag(models.Model):
    course = models.ForeignKey(
        to=Course, related_name="course_tags", on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        to=Tag, related_name="course_tags", on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        to=User,
        related_name="created_tags",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )

    class Meta:
        unique_together = (("course", "tag",),)


class Favourite(models.Model):
    user = models.ForeignKey(
        User, related_name="favourite_courses", on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course, related_name="user_favourites", on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} ★ {self.course.code}"

    class Meta:
        unique_together = (("user", "course"),)
        ordering = ("-created_date",)


class Report(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(default="")
    course = models.ForeignKey(
        to=Course,
        related_name="reports",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    contact_email = models.EmailField(null=True, blank=True)

    @property
    def subject(self):
        if self.course:
            return f"Ny rapport i emnet {self.course.code} fra grades.no"
        return f"Ny rapport fra grades.no"

    @property
    def email_description(self):
        description_text = f"""
{self.contact_email if self.contact_email else "En anonym bruker"} har sendt inn en feilrapport for grades.no.

Emne: {self.course.code if self.course else "Ikke oppgitt"}.

Beskrivelse:
{self.description}

        """
        return description_text

    def __str__(self):
        if self.course:
            return f"{self.created_date} - {self.course.code}"
        return f"{self.course.code}"

    class Meta:
        ordering = ("-created_date",)


class InstitutionalUnit(models.Model):
    acronym = models.CharField("Akronym", max_length=32)
    norwegian_name = models.CharField("Norsk navn", max_length=256)
    english_name = models.CharField("Engelsk navn", max_length=256, default="")
    organization_unit_id = models.IntegerField("OuID", unique=True, help_text="NTNU ID")
    nsd_code = models.CharField("Code fra NSD", max_length=32)

    def __str__(self):
        return self.norwegian_name

    class Meta:
        abstract = True


class Faculty(InstitutionalUnit):
    faculty_id = models.PositiveIntegerField("FakultetsID", unique=True)

    class Meta:
        verbose_name = "Fakultet"
        verbose_name_plural = "Fakulteter"
        ordering = ("norwegian_name",)


class Department(InstitutionalUnit):
    faculty = models.ForeignKey(
        to=Faculty, related_name="departments", on_delete=models.CASCADE, null=True,
    )
    department_id = models.PositiveIntegerField("InstituttsID")

    class Meta:
        verbose_name = "Institutt"
        verbose_name_plural = "Institutter"
        ordering = ("norwegian_name",)


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
        faculties["60"] = "(ØK) Fakultet for økonomi"
        faculties["61"] = "(AD) Fakultet for arkitektur og design"
        faculties["62"] = "(HF) Det humanistiske fakultet"
        faculties["63"] = "(IE) Fakultet for informasjonsteknologi og elektroteknikk "
        faculties["64"] = "(IV) Fakultet for ingeniørvitenskap"
        faculties["65"] = "(MH) Fakultet for medisin og helsevitenskap"
        faculties["66"] = "(NV) Fakultet for naturvitenskap"
        faculties["67"] = "(SU) Fakultet for samfunns- og utdanningsvitenskap"
        return faculties
