import re

import pandas as pd


def split_teachers(teachers: str):
    return re.split(r"[\n,]", str(teachers))


def get_all_teachers(hours_and_teachers_combined: pd.DataFrame):
    lecturers = (
        hours_and_teachers_combined["lecturers with titles"]
        .apply(split_teachers)
        .explode()
        .unique()
    )
    practioners = (
        hours_and_teachers_combined["practice/lab teachers with titles"]
        .apply(split_teachers)
        .explode()
        .unique()
    )

    all_teachers = (
        pd.concat(
            [
                pd.Series(lecturers, name="teacher"),
                pd.Series(practioners, name="teacher"),
            ],
            ignore_index=True,
        )
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return all_teachers


def get_title(teacher: str):
    pattern = r"^(prof\.dr hab\.inż\.|prof\. dr hab\. inż\.|prof\.dr hab\.|prof\. dr hab\.|dr hab\. inż\.|dr hab\.inż\.|dr hab\.|dr hab\.|dr inż\.|dr inż\.|mgr inż\.|mgr inż\.|mgr|dr|prof\. PP)\s*(.+)$"
    match = re.match(pattern, teacher)
    if match:
        title, name = match.groups()
        return title.strip(), name.strip()
    return None, teacher


def replace_artifacts_in_name(teacher: str):
    artifacts_map = {"prof. PP": "", "prof.PP": "", "nan": ""}
    for artifact, replacement in artifacts_map.items():
        teacher = teacher.replace(artifact, replacement)
    return teacher


def correct_titles(title: str):
    title_map = {"prof.dr hab.inż.": "prof. dr hab. inż."}

    if title in title_map:
        return title_map[title]

    return title


def map_teacher_names(teacher: str) -> str:
    teacher_map = {
        "Michał Apolinarsk": "Michał Apolinarski",
        "Marek Michalsk": "Marek Michalski",
        "Paweł T. Wojciechowski": "Paweł Wojciechowski",
        "Centre of Languages and Communication PUT": "Centrum Języków i Komunikacji PP",
        "P.Śniatała": "Paweł Śniatała",
        "J.Jezierski": "Juliusz Jezierski",
        "T.Kobus": "Tadeusz Kobus",
        "M.Kokociński": "Maciej Kokociński",
        "Centre of Languages and Communication": "Centrum Języków i Komunikacji PP",
        "Sports Centre PUT": "Centrum Sportu PP",
    }
    if teacher in teacher_map:
        return teacher_map[teacher]
    return teacher


def correct_teacher_and_title_conditionally(title: str | None, name: str):
    if name == "Bogdan Wyrwas":
        return "dr hab. inż.", "Bogdan Wyrwas"
    if title is None:
        return "department", name

    return title, name


def preprocess_teacher(teacher: str):
    teacher = teacher.strip()
    title, name = get_title(teacher)
    name = map_teacher_names(name)
    name = replace_artifacts_in_name(name)

    title = correct_titles(title)

    title = title.strip() if title else None
    name = name.strip()

    title, name = correct_teacher_and_title_conditionally(title, name)
    return title, name


def create_teacher_id(teachers_dim: pd.DataFrame):
    teacher_id = (
        teachers_dim["title"].str.replace(" ", "-")
        + "_"
        + teachers_dim["full_name"].str.replace(" ", "-")
    )
    return teacher_id.rename("teacher_id")


def create_teachers_dim(all_teachers: pd.Series):
    teachers_dim = pd.DataFrame(
        all_teachers.apply(preprocess_teacher).drop_duplicates().tolist(),
        columns=["title", "full_name"],
    )

    teachers_dim = teachers_dim[teachers_dim["full_name"].str.len() > 0]

    return teachers_dim.set_index(create_teacher_id(teachers_dim), drop=True)
