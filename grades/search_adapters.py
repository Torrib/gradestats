from watson.search import SearchAdapter

from .models import Course


class CourseSearchAdapter(SearchAdapter):
    def get_title(self, course: Course):
        """
        Returns the title of this search result. This is given high priority in search result ranking.
        You can access the title of the search result as `result.title` in your search results.
        The default implementation returns `unicode(obj)`.
        """
        return f"{course.norwegian_name} {course.english_name} {course.code}"

    def get_description(self, course: Course):
        """
        Returns the description of this search result. This is given medium priority in search result ranking.

        You can access the description of the search result as `result.description` in your search results. Since
        this should contains a short description of the search result, it's excellent for providing a summary
        in your search results.

        The default implementation returns `u""`.
        """
        return f"{' '.join(course.tags.all().values_list('tag', flat=True))}"
