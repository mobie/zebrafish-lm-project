import os
import json
from glob import glob

import pandas as pd
from tqdm import tqdm

from create_project import MODALITIES

# all the tables come from this source:
# https://github.com/IDR/idr0079-hartmann-lateralline
ROOT = "/g/schwab/Kimberly/Publications/MoBIE_paper/Jonas_project/raw/idr_0079"
TABLE_ROOT = './idr0079-hartmann-lateralline/experimentA/idr0079_experimentA_extracted_measurements'


def samples_to_datasets():
    exp_dirs = glob(os.path.join(ROOT, '*'))

    sample_dict = {}
    for exp_dir in exp_dirs:
        exp_name = os.path.split(exp_dir)[1]
        exp_name = MODALITIES[exp_name]
        exp_samples = os.listdir(exp_dir)
        sample_dict.update({sample: exp_name for sample in exp_samples})

    return sample_dict


def load_image_dict(ds_name):
    image_dict = f'./data/{ds_name}/images/images.json'
    with open(image_dict, 'r') as f:
        image_dict = json.load(f)
    return image_dict


def copy_table(table_in, table_out):
    table = pd.read_csv(table_in, sep='\t')
    cols = list(table.columns)
    cols[cols.index('Cell ID')] = 'label_id'
    table.columns = cols
    table = table.drop(labels=['Source Name'], axis='columns')
    table.to_csv(table_out, sep='\t', index=False)


def add_tables():

    sample_dict = samples_to_datasets()
    samples = glob(os.path.join(TABLE_ROOT, '*'))
    for sample in tqdm(samples):
        if not os.path.isdir(sample):
            continue
        sample_name = os.path.split(sample)[1]
        ds_name = sample_dict[sample_name]
        image_dict = load_image_dict(ds_name)
        marker_name = 'lynEGFP_linUnmix' if ds_name == 'nuclei' else 'lynEGFP'
        seg_name = f'membrane-{sample_name}_{marker_name}_seg'
        try:
            table_folder = os.path.join('./data', ds_name, image_dict[seg_name]['tableFolder'])
        except KeyError:
            print(list(image_dict.keys()))
            raise KeyError
        assert os.path.exists(table_folder), table_folder
        table_files = glob(os.path.join(sample, '*.tsv'))
        for table_file in table_files:
            table_name = os.path.split(table_file)[1]
            table_name = '_'.join(table_name.split('_')[1:])
            table_out = os.path.join(table_folder, table_name.replace('.tsv', '.csv'))
            copy_table(table_file, table_out)


if __name__ == '__main__':
    add_tables()
