import json
import os
import re
from glob import glob

from mobie import initialize_dataset, add_image_data, add_segmentation
from mobie.metadata import add_remote_project_metadata

ROOT = "/g/schwab/Kimberly/Publications/MoBIE_paper/Jonas_project/raw/idr_0079"
MODALITIES = {"experimentA": "membrane",
              "experimentB": "nuclei",
              "experimentC": "actin",
              "experimentD": "cisgolgi",
              "experimentE": "early_endosomes",
              "experimentF": "recycling_endosomes",
              "experimentG": "tgn_and_late_endosomes",
              "experimentH": "trans_golgi",
              "experimentI": "atoh1a",
              "experimentJ": "lysosomes"}


def add_sample(experiment, sample, sample_dir,
               is_default=False, dry_run=True, first_sample=False):
    pattern = re.compile(f"({sample}_8bit_)(\w+)")

    if experiment == 'nuclei':
        file_pattern = '*linUnmix.tif'
    else:
        file_pattern = '*lynEGFP.tif'

    unit = "micrometer"
    chunks = (64, 64, 64)
    scale_factors = 4 * [[2, 2, 2]]

    #
    # initialize the dataset with '...lynEGFP.tif'
    #
    im_path = glob(os.path.join(sample_dir, file_pattern))
    assert len(im_path) == 1
    im_path = im_path[0]
    im_name = os.path.split(im_path)[1]

    mobie_name = f'membrane-{sample}_' + pattern.match(im_name).group(2)

    txt_file = im_path.replace('.tif', '.txt')
    with open(txt_file) as f:
        res = f.readline().rstrip()
        res = list(map(float, res.split(',')))[::-1]

    if first_sample:
        if dry_run:
            print("Initialize dataset:")
            print(im_path)
            print(mobie_name, res)
        else:
            initialize_dataset(
                input_path=im_path,
                input_key='',
                root='./data',
                dataset_name=experiment,
                raw_name=mobie_name,
                resolution=res,
                scale_factors=scale_factors,
                chunks=chunks,
                unit=unit,
                target='local',
                max_jobs=16,
                is_default=is_default
            )
    else:
        if dry_run:
            print("Add image:")
            print(im_path)
            print(mobie_name, res)
        else:
            add_image_data(
                input_path=im_path,
                input_key='',
                root='./data',
                dataset_name=experiment,
                image_name=mobie_name,
                resolution=res,
                scale_factors=scale_factors,
                chunks=chunks,
                unit=unit,
                target='local',
                max_jobs=16
            )

    #
    # add the segmentation with '...lynEGFP_seg.tif'
    #
    seg_path = glob(os.path.join(sample_dir, '*seg.tif'))
    assert len(seg_path) == 1, f"{seg_path}"
    seg_path = seg_path[0]
    seg_name = os.path.split(seg_path)[1]
    mobie_name = f'membrane-{sample}_' + pattern.match(seg_name).group(2)

    txt_file = seg_path.replace('.tif', '.txt')
    with open(txt_file) as f:
        res = f.readline().rstrip()
        res = list(map(float, res.split(',')))[::-1]

    if dry_run:
        print("Add seg:")
        print(seg_path)
        print(mobie_name, res)
    else:
        add_segmentation(
            input_path=seg_path,
            input_key='',
            root='./data',
            dataset_name=experiment,
            segmentation_name=mobie_name,
            scale_factors=scale_factors,
            resolution=res,
            chunks=chunks,
            unit=unit,
            target='local',
            max_jobs=16
        )

    #
    # add all other images
    #
    additional_paths = glob(os.path.join(sample_dir, '*.tif'))
    for path in additional_paths:
        if path == im_path or path == seg_path:
            continue
        if experiment == 'nuclei' and 'lynEGFP' in path:
            continue

        image_name = os.path.split(path)[1]
        mobie_name = experiment + f'-{sample}_' + pattern.match(image_name).group(2)

        txt_file = seg_path.replace('.tif', '.txt')
        with open(txt_file) as f:
            res = f.readline().rstrip()
            res = list(map(float, res.split(',')))[::-1]

        if dry_run:
            print("Add additional image:")
            print(path)
            print(mobie_name, res)
        else:
            add_image_data(
                input_path=path,
                input_key='',
                root='./data',
                dataset_name=experiment,
                image_name=mobie_name,
                scale_factors=scale_factors,
                resolution=res,
                chunks=chunks,
                unit=unit,
                target='local',
                max_jobs=16
            )


def create_experiment(exp, exp_dir, is_default, dry_run):
    sample_names = os.listdir(exp_dir)
    if not all(os.path.isdir(os.path.join(exp_dir, sample)) for sample in sample_names):
        for sample in sample_names:
            if not os.path.isdir(os.path.join(exp_dir, sample)):
                print("Not a directory:", os.path.join(exp_dir, sample))
        raise RuntimeError

    sample_dir = os.path.join(exp_dir, sample_names[0])
    add_sample(exp, sample_names[0], sample_dir, first_sample=True, dry_run=dry_run)
    print()
    for sample in sample_names[1:]:
        sample_dir = os.path.join(exp_dir, sample)
        add_sample(exp, sample, sample_dir, dry_run=dry_run)
        print()


def create_project(dry_run):

    ds_path = './data/datasets.json'
    if os.path.exists(ds_path):
        with open(ds_path) as f:
            datasets = json.load(f)['datasets']
    else:
        datasets = []

    experiments = os.listdir(ROOT)
    is_default = True
    for exp in experiments:
        exp_dir = os.path.join(ROOT, exp)
        exp = MODALITIES[exp]
        if not os.path.isdir(exp_dir):
            print("Not a folder", exp_dir)
            continue

        # skip creating this experiment if it already exists
        if exp in datasets:
            print("Dataset", exp, "has already been created and is skipped")
            is_default = False
            continue

        print("Create dataset for experiment", exp)
        create_experiment(exp, exp_dir,
                          is_default=is_default, dry_run=dry_run)
        is_default = False


def prepare_upload():
    bucket_name = 'zebrafish-lm'
    service_endpoint = 'https://s3.embl.de'
    authentication = 'Anonymous'
    add_remote_project_metadata(
        'data', bucket_name,
        service_endpoint=service_endpoint,
        authentication=authentication
    )


if __name__ == '__main__':
    create_project(dry_run=False)
    prepare_upload()
