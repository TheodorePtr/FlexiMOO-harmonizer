import re

import pandas as pd


def standardize_hall_prefix(room: str):
    # Regex to match 'hall', 's.', 'sala' at the beginning of the string (case-insensitive)
    pattern = r"(hall|s\.|sala|sale:)\s*"

    return re.sub(pattern, "hall ", room, flags=re.IGNORECASE)


def format_lab_prefixes(room: str):

    # Replace 'lab ' with 'lab.'
    room = room.replace("lab", "lab.")

    # Replace 'l' with lab.
    room = room.replace("l.", "lab.")

    # Ensure there's exactly one dot after 'lab'
    room = re.sub(r"^(lab)\.{2,}", r"lab.", room)

    # Ensure there is exactly one space after 'lab.'
    room = re.sub(r"(lab\.*+)", r"lab. ", room)

    return room


def handle_big_l(room: str):
    # Check if 'L' is in the string
    if "L" in room:
        # If the string starts with 'hall', remove 'L'
        if room.startswith("hall"):
            return room.replace("L", "")
        else:
            # If it doesn't start with 'hall', add 'hall' as prefix and remove 'L'
            return "hall " + room.replace("L", "")
    # If 'L' is not in the string, return the original string
    return room


def preprocess_room(room: str):
    room = room.strip()
    room = standardize_hall_prefix(room)
    room = format_lab_prefixes(room)
    room = handle_big_l(room)
    # Clean up multiple spaces
    room = re.sub(r"\s+", " ", room)
    room = room.strip()

    room = map_special_cases(room)
    return room


def preprocess_rooms(rooms: pd.Series):
    rooms = rooms.str.replace("\n", "")
    rooms = rooms.str.split(",")
    rooms = rooms.explode()
    rooms = rooms.apply(preprocess_room)

    return rooms


def map_special_cases(room: str):
    special_cases_mapping = {
        # hall 8 CW
        "8 CW": "hall 8 CW",  # occured in input as lab
        "lab. 8 CW": "hall 8 CW",
        # 108 WE
        "108 WE": "lab. 108 WE",  # assumption
        # 508 WE
        "508k WE": "lab. 508k WE",  # occuredf as lab
        # lab. 1.6.22 BT
        "1.6.22 BT": "lab. 1.6.22 BT",
        "lab. 1.6.23": "lab. 1.6.23 BT",
        "1.6.23 BT": "lab. 1.6.23 BT",
        "hall 1.6.23": "lab. 1.6.23 BT",  # should be lab
        # lab. 1.3.16
        "hall 1.3.16": "lab. 1.3.16",  # should be lab
        # lab. 2.7.16 BT
        "lab. 2.7.16": "lab. 2.7.16 BT",
        "2.7.16 BT": "lab. 2.7.16 BT",
        "2.7.16 hall": "lab. 2.7.16 BT",
        # lab. 143 CW
        "lab. 143": "lab. 143 CW",
        "hall 143": "lab. 143 CW",
        "142/143 CW": "lab. 143 CW",
        # hall 13 CW
        "13 CW": "hall 13 CW",
        # lab. 2.7.6 BT
        "lab. 2.7.6": "lab. 2.7.6 BT",
        # hall 103C AP
        "hall 103C": "hall 103C AP",
        # hall 301c WTCh
        "301C WTCh": "hall 301c WTCh",
        "301c WTCh": "hall 301c WTCh",
        # hall 126 BT
        "hall 126 BT w": "hall 126 BT",
        # lab. 44 CW
        "44 CW": "lab. 44 CW",
        "43/44 CW": "lab. 44 CW",
        "lab. 43/44 CW": "lab. 44 CW",
        "lab. 44": "lab. 44 CW",
        # lab. 1.6.22 BT
        "lab. 1.6.22": "lab. 1.6.22 BT",
        # lab. 144 CW
        "144 CW": "lab. 144 CW",
        # lab. 2.6.21 BT
        "hall 2.6.21": "lab. 2.6.21 BT",
        "lab. 2.6.21": "lab. 2.6.21 BT",
        "hall 2.6.21 BT": "lab. 2.6.21 BT",
        # lab. 507 WE
        "hall 507 WE": "lab. 507 WE",
        "lab. 507": "lab. 507 WE",
        # lab. A3-110
        "A3-110": "lab. A3-110",
        # lab. PO20
        "PO20": "lab. PO20",
        # lab. 45 CW
        "45 CW": "lab. 45 CW",
        "lab. 45": "lab. 45 CW",
        # lab. WE537
        "lab. WE537": "lab. 537 WE",
        # hall 116 WE
        "116 WE": "hall 116 WE",
        # lab. 43 CW
        "43 CW": "lab. 43 CW",
        # lab. 1.6.20 BT
        "lab. 1.6.20": "lab. 1.6.20 BT",
        "1.6.20 BT": "lab. 1.6.20 BT",
        # lab. 142 CW
        "142 CW": "lab. 142 CW",
        "hall 142": "lab. 142 CW",
        # lab. 2.6.22 BT
        "lab. 2.6.22": "lab. 2.6.22 BT",
        "lab. 2.6.22 s": "lab. 2.6.22 BT",
        "hall 2.6.22": "lab. 2.6.22 BT",
        "2.6.22 BT": "lab. 2.6.22 BT",
        # lab. 1.6.16
        "lab. 1.6.16": "lab. 1.6.16 BT",  # assumption
        # 'hall 12 A22',
        "A22 hall 12": "hall 12 A22",
        # lab. 1.6.21 BT
        "lab. 1.6.21": "lab. 1.6.21 BT",
        "1.6.21 BT": "lab. 1.6.21 BT",
        # hall 6 CW
        "6 CW": "hall 6 CW",
        # lab. 1 BM
        "1 BM": "lab. 1 BM",
    }

    mapped_room = special_cases_mapping.get(room)
    if mapped_room:
        return mapped_room
    return room


def create_room_dim(rooms: list[str]):
    return pd.DataFrame(rooms, columns=["room_name"])
