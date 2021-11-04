import json
import os
import numpy as np
import pandas as pd


def update_grid_tables(dataset_folder):
    table_names = ['grid-view', 'small-grid-view']
    for table_name in table_names:
        table_path = os.path.join(dataset_folder, 'tables', table_name, 'default.tsv')
        table = pd.read_csv(table_path, sep='\t')

        n_pos = table.shape[0]
        modality = os.path.split(dataset_folder)[1]
        if modality == 'membrane':
            extra_cols = pd.DataFrame(
                data=np.ones((n_pos, 1)),
                columns=['membrane']
            )
        else:
            extra_cols = pd.DataFrame(
                data=np.ones((n_pos, 2)),
                columns=['membrane', modality]
            )

        table = pd.concat([table, extra_cols], axis=1)
        table.to_csv(table_path, sep='\t', index=False)


def update_all_tables():
    with open('./data/project.json') as f:
        datasets = json.load(f)['datasets']

    for ds in datasets:
        update_grid_tables(os.path.join('./data', ds))


if __name__ == '__main__':
    update_all_tables()
