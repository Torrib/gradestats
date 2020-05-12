from .models import Course


def calculate_average_grade(course: Course):
    grades = course.grades.all()
    average = 0
    attendees = 0
    for grade in grades:
        attendees += grade.get_num_attendees()
        average += grade.average_grade * grade.get_num_attendees()
    if attendees == 0:
        return 0.0
    else:
        average /= attendees
        return average


def calculate_total_attendees(course: Course):
    grades = course.grades.all()
    attendees = 0
    for grade in grades:
        attendees += grade.attendee_count

    return attendees


def update_course_stats(course: Course):
    average = calculate_average_grade(course)
    course.average = average

    attendee_count = calculate_total_attendees(course)
    course.attendee_count = attendee_count

    course.save()
