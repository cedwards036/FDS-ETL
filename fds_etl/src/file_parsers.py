import csv


def csv_to_dict(filepath: str) -> dict:
    with open(filepath, encoding='utf-8') as f:
        next(f)  # skip header
        reader = csv.reader(f, skipinitialspace=True)
        return dict(reader)
