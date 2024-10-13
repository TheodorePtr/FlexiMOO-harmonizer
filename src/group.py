import pandas as pd

from src.config import SHEET_NAME_PATTERN
from src.course_stage_semester_specialty import (
    create_course_id,
    get_course_stage_semester_specialty,
)


def extract_group_names(groups: str):
    groups_processed = str(groups)

    # split groups
    group_names = str(groups_processed).split("\n")

    # replace nans in group names by L + positional index
    for i, group in enumerate(group_names):
        if group == "nan":
            group_names[i] = f"L{i}"
    return group_names


def correct_group_input_error(groups: str):
    # correct input errors
    correction_dict = {"L88": "L8", "nan": "L1"}

    for correct_input_error in correction_dict:
        groups = groups.replace(
            correct_input_error, correction_dict[correct_input_error]
        )
    return groups


def preprocess_groups(groups: str):
    groups = str(groups)
    groups = correct_group_input_error(groups)
    group_names = extract_group_names(groups)
    return group_names


def create_group_id(groups_dim: pd.DataFrame):
    group_id = (
        create_course_id(groups_dim)
        + "_"
        + groups_dim["stage_name"]
        + "_"
        + groups_dim["semester_num"]
        + "_"
        + groups_dim["group_name"]
    )
    return group_id.rename("group_id")


def create_groups_dim(timetables_combined: pd.DataFrame):
    groups = timetables_combined["group"].apply(preprocess_groups).rename("group_name")
    cst = pd.DataFrame(
        timetables_combined["sheet_name"]
        .apply(get_course_stage_semester_specialty)
        .tolist(),
        columns=SHEET_NAME_PATTERN,
    )

    groups_dim = (
        cst.join(groups).explode("group_name", ignore_index=True).drop_duplicates()
    )

    return groups_dim.set_index(create_group_id(groups_dim), drop=True)
