from django.apps import AppConfig
from watson import search as watson


class GradesAppConfig(AppConfig):
    name = "grades"

    def ready(self):
        Course = self.get_model("Course")
        from .search_adapters import CourseSearchAdapter

        watson.register(
            Course,
            CourseSearchAdapter,
            fields=(
                "norwegian_name",
                "short_name",
                "code",
                "faculty_code",
                "exam_type",
                "grade_type",
                "place",
                "english_name",
                "course_level",
                "content",
                "learning_form",
                "learning_goal",
                "tags__tag",
            ),
        )
