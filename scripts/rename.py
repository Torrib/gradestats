# -*- coding: utf-8 -*-
import os
import django
import json
import requests
from grades.models import Course

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gradestats.settings")
django.setup()

base_url = "http://www.ime.ntnu.no/api/course/"

courses = Course.objects.all()

print("Renaming....")

for course in courses:
    resp = requests.get(base_url + course.code)
    if not resp:
        continue
    data = json.loads(resp.text)

    if not data["course"]:
        continue

    print("Checking " + course.code)

    if data["course"]["norwegianName"] != course.norwegian_name:
        print(
            "Renaming "
            + course.norwegian_name
            + " to "
            + data["course"]["norwegianName"]
        )
        course.norwegian_name = data["course"]["norwegianName"]
        course.save()
