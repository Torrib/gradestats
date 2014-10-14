from django.db import models
from django.db.models import permalink

class Course(models.Model):
    name = models.CharField("Name", max_length=100)
    short_name = models.CharField("Short name", max_length=50)
    code = models.CharField("Code", max_length=15)

    def __unicode__(self):
        return self.code
    
    @permalink
    def get_absolute_url(self):
        return ('course', None, {'course_id': self.id,}) 

class Grade(models.Model):
    course = models.ForeignKey(Course)
    semester_code = models.CharField("Semester", max_length=10)

    a = models.SmallIntegerField(default = 0)
    b = models.SmallIntegerField(default = 0)
    c = models.SmallIntegerField(default = 0)
    d = models.SmallIntegerField(default = 0)
    e = models.SmallIntegerField(default = 0)
    f = models.SmallIntegerField(default = 0)

    def __unicode__(self):
        return self.semester_code
