from mobie.metadata import add_grid_bookmark, read_dataset_metadata, read_project_metadata


def update_settings(settings, last_color, source_type, group_name):
    settings.pop('name', None)
    settings.pop('sources', None)
    if source_type == 'segmentation':
        return settings, last_color

    if group_name == 'membrane':
        settings['color'] = 'white'
        return settings, last_color
    else:
        if last_color is None:
            color = 'green'
        elif last_color == 'green':
            color = 'blue'
        elif last_color == 'blue':
            color = 'red'
        else:
            raise RuntimeError("Too many colors")
        settings['color'] = color
        return settings, color


def create_grid_bookmark(dataset, small):
    ds_folder = f'./data/{dataset}'
    ds_meta = read_dataset_metadata(ds_folder)
    sources = ds_meta['sources']

    grid_sources = []
    display_groups = {}
    display_group_settings = {}

    base_name_positions = []

    last_color = None
    for source_name, source in sources.items():
        source_type = list(source.keys())[0]
        view = source[source_type]['view']
        group_name = view['uiSelectionGroup']
        display_groups[source_name] = group_name
        if group_name not in display_group_settings:
            setting_key = 'imageDisplay' if source_type == 'image' else 'segmentationDisplay'
            settings = view['sourceDisplays'][0][setting_key]
            settings, last_color = update_settings(settings, last_color, source_type, group_name)
            display_group_settings[group_name] = settings

        base_name = source_name.split('_')[0]
        try:
            grid_id = base_name_positions.index(base_name)
            grid_sources[grid_id].append(source_name)
        except ValueError:
            n_pos = len(base_name_positions)
            if small and n_pos >= 2:
                continue
            base_name_positions.append(base_name)
            grid_sources.append([source_name])

    name = 'small-grid-view' if small else 'grid-view'
    add_grid_bookmark(ds_folder, name, grid_sources,
                      display_groups=display_groups,
                      display_group_settings=display_group_settings)


def create_grid_bookmarks(small=False):
    datasets = read_project_metadata('./data')['datasets']
    for ds in datasets:
        print(ds)
        create_grid_bookmark(ds, small=small)


if __name__ == '__main__':
    # create_grid_bookmarks()
    create_grid_bookmarks(small=True)
