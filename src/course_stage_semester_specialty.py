import pandas as pd


def get_course_stage_semester_specialty(sheet_name: str) -> list[str]:
    components = sheet_name.split("_")
    # no sub_course
    if len(components) == 3:
        # if specialty is not given, it's set to default
        return [components[0], "default", components[1], components[2][-1]]
    # in case of sub_course string appended
    elif len(components) == 4:
        return [components[0], components[3], components[1], components[2][-1]]


def create_course_id(courses: pd.DataFrame) -> pd.Series:
    return (courses["course_name"] + "_" + courses["specialty"]).rename("course_id")
