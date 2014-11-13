from django import forms
from django.core.validators import RegexValidator


class AddTagForm(forms.Form):
    tag = forms.CharField(label="Tag text", max_length=32, min_length=2)


class SearchForm(forms.Form):
    query = forms.CharField(max_length=32, required=False)
    faculty_code = forms.IntegerField()


class ReportErrorForm(forms.Form):
    course_code = forms.CharField(
        label="Fagkode",
        max_length=16,
        validators=[RegexValidator(
                    regex=r'^[a-zA-Z\xc5K]{2,5}[\d]{2,4}$',
                    message="Invalid course code",
                    code='invalid_course_code')])
    semester_code = forms.CharField(
        label="Semester",
        max_length=5,
        validators=[RegexValidator(
                    regex=r'^[VHS]\d{4,4}$',
                    message="Invalid semester code",
                    code='invalid_semester_code')])
    description = forms.CharField(label="Beskrivelse")


