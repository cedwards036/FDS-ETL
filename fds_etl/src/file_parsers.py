import csv


def csv_to_dict(filepath: str, skip_header=True) -> dict:
    with open(filepath, encoding='utf-8') as f:
        if skip_header:
            next(f)
        reader = csv.reader(f, skipinitialspace=True)
        return dict(reader)
