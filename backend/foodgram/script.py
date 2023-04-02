import csv

from recipes.models import Ingredients


def run():
    with open("ingredients.csv", encoding='utf-8') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        for row in file_reader:
            try:
                Ingredients.objects.create(
                    name=row[0], measurement_unit=row[1]
                )
            except Exception:
                ...
