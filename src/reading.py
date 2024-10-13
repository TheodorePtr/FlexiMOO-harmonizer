import pandas as pd


def drop_empty_days(df: pd.DataFrame) -> pd.DataFrame:
    # accroding to convention we agreed on
    # empty days would have the specififc set of columns empty
    return df.dropna(
        subset=[
            "day",
            "timeslot",
            "subject full name",
            "room",
            "lecture/practice/laboratory",
            "group",
        ]
    ).reset_index(drop=True)


def read_and_combine_sheets(excel_file_path: str):
    sheets = []
    with pd.ExcelFile(excel_file_path) as excel_file:
        for sheet_name in excel_file.sheet_names:
            sheet = excel_file.parse(sheet_name)
            sheet["sheet_name"] = sheet_name
            sheets.append(sheet)

    return pd.concat(sheets, ignore_index=True)
