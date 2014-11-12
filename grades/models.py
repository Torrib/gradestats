from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_init

class Course(models.Model):
    norwegian_name = models.CharField("Norwegian Name", max_length=100)
    short_name = models.CharField("Short name", max_length=50)
    code = models.CharField("Code", max_length=15)
    faculty_code = models.IntegerField("Faculty Code");

    english_name = models.CharField("English name", max_length=100)
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

    def __unicode__(self):
        return self.code
    
    @permalink
    def get_absolute_url(self):
        return 'course', None, {'course_code': self.code, }


class Grade(models.Model):
    course = models.ForeignKey(Course)
    semester_code = models.CharField("Semester", max_length=10)
    
    average_grade = models.FloatField()

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


def get_average_grade(**kwargs):
        course = kwargs.get('instance')
        grades = course.grade_set.all()
        course.average = 0
        attendees = 0
        for grade in grades:
            attendees += grade.get_num_attendees()
            course.average += (grade.average_grade * grade.get_num_attendees())
        if attendees == 0:
            return
        else:
            course.average /= attendees
            return

post_init.connect(get_average_grade, Course)
