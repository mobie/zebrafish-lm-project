import json
import os
import pandas as pd


#
# TODO update to new spec and implement convenience function in mobie-utils
#

def create_image_table(table_path, source_names):
    modalities = ["segmentation" if "seg" in name else name.split('-')[0] for name in source_names]
    data = [
        [name, modal] for name, modal in zip(source_names, modalities)
    ]
    table = pd.DataFrame(data, columns=['source_name', 'modality'])
    table.to_csv(table_path, sep='\t', index=False)


def create_grid_bookmark(experiment):
    ds_folder = f'./data/{experiment}'
    with open(os.path.join(ds_folder, 'images', 'images.json')) as f:
        image_dict = json.load(f)
    image_names = list(image_dict.keys())
    samples_to_images = {}
    for name in image_names:
        sample = name.split('-')[1]
        sample = sample.split('_')[0]
        if sample in samples_to_images:
            samples_to_images[sample].append(name)
        else:
            samples_to_images[sample] = [name]

    bookmark_name = "overview"
    grid = [sample_images for sample_images in samples_to_images.values()]
    table_dir = os.path.join(ds_folder, "tables", bookmark_name)
    os.makedirs(table_dir, exist_ok=True)
    source_table_path = os.path.join(table_dir, "default.csv")
    create_image_table(source_table_path, image_names)
    bookmark = {
        # we don't have any special settings for the layers
        "layers": {name: {} for name in image_names},
        "layouts": {
            "gridView": {
                "layers": grid,
                "layoutType": "AutoGrid",
                "sourceTable": source_table_path
            }
        }
    }

    bookmark_file = os.path.join(ds_folder, 'misc/bookmarks/default.json')
    with open(bookmark_file) as f:
        bookmarks = json.load(f)

    bookmarks.update({bookmark_name: bookmark})

    with open(bookmark_file, 'w') as f:
        json.dump(bookmarks, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    create_grid_bookmark('membrane')
