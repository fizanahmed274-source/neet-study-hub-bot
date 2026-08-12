import json


def load_pyqs():
    with open("pyq.json", "r", encoding="utf-8") as file:
        return json.load(file)["questions"]


def get_pyq_years():
    questions = load_pyqs()
    return sorted(
        list(set(q["year"] for q in questions)),
        reverse=True
    )


def get_pyqs_by_year(year):
    questions = load_pyqs()

    return [
        q for q in questions
        if str(q.get("year")) == str(year)
    ]


def get_pyqs_by_subject(year, subject):
    questions = get_pyqs_by_year(year)

    return [
        q for q in questions
        if q.get("subject") == subject
    ]


def get_pyqs_by_chapter(year, subject, chapter):
    questions = get_pyqs_by_subject(
        year,
        subject
    )

    return [
        q for q in questions
        if q.get("chapter") == chapter
    ]
