import os
import mobie
from glob import glob

import pandas as pd


def fix_column_names(table_folder):
    merge_columns = {"label_id"}

    tables = glob(os.path.join(table_folder, "*.tsv"))
    column_names = []

    for table_path in tables:
        table = pd.read_csv(table_path, sep="\t")
        this_columns = list(set(table.columns) - merge_columns)
        duplicate_columns = list(set(column_names).intersection(set(this_columns)))

        if duplicate_columns:
            prefix = os.path.splitext(os.path.basename(table_path))[0]
            rename_columns = {col: f"{col}_{prefix}" for col in duplicate_columns}
            table.rename(columns=rename_columns, inplace=True)
            this_columns = [rename_columns.get(col, col) for col in this_columns]
            table.to_csv(table_path, sep="\t", index=False)

        column_names.extend(this_columns)


def fix_dataset(dataset_name):
    table_folders = glob(os.path.join("data", dataset_name, "tables", "*"))
    for table_folder in table_folders:
        fix_column_names(table_folder)


def main():
    datasets = mobie.metadata.get_datasets("data")
    for dataset in datasets:
        fix_dataset(dataset)


if __name__ == "__main__":
    main()
