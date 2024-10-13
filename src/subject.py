import re
from typing import Literal

import pandas as pd

from src.config import SHEET_NAME_PATTERN
from src.course_stage_semester_specialty import (
    create_course_id,
    get_course_stage_semester_specialty,
)


def map_subject(subject: str):
    subjects_map = {
        "jezyk angielski": "język angielski",
        "język angielsk": "język angielski",
        "pre diploma seminar": "pre-diploma seminar",
        "scientific & technical writing": "scientific and technical writing",
        "analiza danych wysokoprzep": "analiza danych wysokoprzepustowych",
        "wprowadzenie do chemii organiczne": "wprowadzenie do chemii organicznej",
        "usługi biblioteczne i informcyjne": "usługi biblioteczne i informacyjne",
        "materiały do zastosowań biomedycznyc": "materiały do zastosowań biomedycznych",
        "introduction to artifical intelligence": "introduction to artificial intelligence",
        "praktyka i teoria szeregowania zada": "praktyka i teoria szeregowania zadań",
        "scientific technical writing": "scientific and technical writing",
        "biokrystalografia": "biokrystalografia makromolekularna",
        "systemy wbudowane embedded systems": "systemy wbudowane",
        "embedded systems": "systemy wbudowane",
        "problem classes i artificial intelligence": "problem classes 1 artificial intelligence",
        "problem classes": "problem classes 1 artificial intelligence",
        "przedmiot obieralny 1 produkt cyfrowy": "produkt cyfrowy",
    }
    if subject in subjects_map:
        return subjects_map[subject]

    return subject


def clean_subject(subject: str):
    # Define the regular expression pattern
    pattern = r"[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\']+"

    # Replace sequences of characters that are not in the allowed set with a single space
    purified_subject = re.sub(pattern, " ", subject)

    # Replace multiple spaces with a single space
    purified_subject = re.sub(r"\s+", " ", purified_subject)

    # Strip leading and trailing spaces
    purified_subject = purified_subject.strip()

    return purified_subject


def preprocess_subject(subject: str):
    subject = subject.lower()
    subject = clean_subject(subject)
    return map_subject(subject)


def prepare_type_indicators(hours_and_teachers_combined: pd.DataFrame):
    has_lecture = (
        hours_and_teachers_combined["Lecture hours"].notna()
        & hours_and_teachers_combined["Lecture hours"]
        > 0
    ).rename("has_lecture")
    has_practice = (
        hours_and_teachers_combined["Practice hours"].notna()
        & hours_and_teachers_combined["Practice hours"]
        > 0
    ).rename("has_practice")
    has_laboratory = (
        hours_and_teachers_combined["Laboratory hours"].notna()
        & hours_and_teachers_combined["Laboratory hours"]
        > 0
    ).rename("has_laboratory")
    has_project = (
        hours_and_teachers_combined["Project hours"].notna()
        & hours_and_teachers_combined["Project hours"]
        > 0
    ).rename("has_project")

    return pd.concat([has_lecture, has_practice, has_laboratory, has_project], axis=1)


def derrive_subject_type_to_array(type_indicator: pd.Series):
    types = []
    if type_indicator["has_lecture"]:
        types.append("Lecture")
    if type_indicator["has_practice"]:
        types.append("Practice")
    if type_indicator["has_laboratory"]:
        types.append("Laboratory")
    if type_indicator["has_project"]:
        types.append("Project")

    if len(types) == 0:
        print(type_indicator.name)
        types.append("self-study")

    return types


def create_subject_id(subject_dim: pd.DataFrame):
    subject_id = (
        create_course_id(subject_dim)
        + "_"
        + subject_dim["stage_name"]
        + "_"
        + subject_dim["semester_num"]
        + "_"
        + subject_dim["subject_full_name"].str.replace(" ", "-")
        + "_"
        + subject_dim["subject_type"]
    )
    return subject_id.rename("subject_id")


def create_subjects_dim(
    df: pd.DataFrame, source: Literal["timetable", "hours_and_teachers"]
):
    subjects = (
        df["subject full name"].apply(preprocess_subject).rename("subject_full_name")
    )
    cst = pd.DataFrame(
        df["sheet_name"].apply(get_course_stage_semester_specialty).tolist(),
        columns=SHEET_NAME_PATTERN,
    )

    if source == "hours_and_teachers":
        type_indicators = prepare_type_indicators(df)
        subject_type = type_indicators.apply(
            derrive_subject_type_to_array, axis=1
        ).rename("subject_type")

    else:
        subject_type = df["lecture/practice/laboratory"].rename("subject_type")

    subject_dim = (
        cst.join(subjects).join(subject_type).explode("subject_type").drop_duplicates()
    )

    return subject_dim.set_index(create_subject_id(subject_dim), drop=True)
