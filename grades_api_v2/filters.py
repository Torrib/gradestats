from django_filters import filters, filterset
from watson import search as watson_search

from grades.models import Course, Grade


class WatsonFilter(filters.CharFilter):
    def filter(self, queryset, value):
        if value and value != "":
            queryset = watson_search.filter(queryset, value)
        return queryset


class CourseFilter(filterset.FilterSet):
    query = WatsonFilter()

    class Meta:
        model = Course
        fields = {
            "code": ["exact"],
            "faculty_code": ["exact"],
            "exam_type": ["exact"],
            "grade_type": ["exact"],
            "place": ["exact"],
            "have_had_digital_exam": ["exact"],
            "credit": ["exact", "lte", "gte"],
            "study_level": ["exact"],
            "taught_in_spring": ["exact"],
            "taught_in_autumn": ["exact"],
            "taught_in_english": ["exact"],
            "taught_from": ["exact", "lte", "gte"],
            "last_year_taught": ["exact", "lte", "gte"],
        }


class GradeFilter(filterset.FilterSet):
    attendee_count = filters.NumberFilter(field_name="attendee_count")
    attendee_count__lte = filters.NumberFilter(field_name="attendee_count", lookup_expr="lte")
    attendee_count__gte = filters.NumberFilter(field_name="attendee_count", lookup_expr="gte")

    class Meta:
        model = Grade
        fields = {
            "course": ["exact"],
            "average_grade": ["exact", "lte", "gte"],
            "digital_exam": ["exact"],
            "a": ["exact", "lte", "gte"],
            "b": ["exact", "lte", "gte"],
            "c": ["exact", "lte", "gte"],
            "d": ["exact", "lte", "gte"],
            "e": ["exact", "lte", "gte"],
            "f": ["exact", "lte", "gte"],
            "passed": ["exact", "lte", "gte"],
        }
