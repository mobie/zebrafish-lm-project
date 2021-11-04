from mobie.migration.migrate_v2 import migrate_project


def parse_menu_name(source_type, source_name):
    modality = source_name.split('-')[0]
    menu_name = modality if source_type == 'image' else f'{modality}-segmentation'
    return menu_name


def parse_source_name(name):
    name = name.split('-')[1]
    return name


migrate_project('./data', parse_menu_name=parse_menu_name, parse_source_name=parse_source_name)
