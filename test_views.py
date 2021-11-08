import mobie

DS = "./data/membrane"


def get_sources(n_sources=4):
    metadata = mobie.metadata.read_dataset_metadata(DS)
    im_sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == "image"]
    seg_sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == "segmentation"]
    assert len(im_sources) == len(seg_sources)
    sources = [[im, seg] for im, seg in zip(im_sources, seg_sources)][:n_sources]
    return sources


def add_merged_grid():
    view_name = "merged-grid"
    sources = get_sources()
    view = mobie.metadata.get_grid_view(DS, view_name, sources, use_transformed_grid=False, menu_name="test")
    mobie.metadata.add_view_to_dataset(DS, view_name, view, bookmark_file_name="test_views")


def get_crops(n_sources=4):
    metadata = mobie.metadata.read_dataset_metadata(DS)
    sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == "segmentation"]
    sources = sources[:n_sources]
    names_after_trafo = [source + "_cropped" for source in sources]

    shape = (130, 816, 1636)
    resolution = (0.22, 0.1, 0.1)
    shape = tuple(sh * re for sh, re in zip(shape, resolution))
    halo = (4.0, 12.0, 12.0)
    min_ = [sh // 2 - ha for sh, ha in zip(shape, halo)]
    max_ = [sh // 2 + ha for sh, ha in zip(shape, halo)]

    trafos = [
        mobie.metadata.get_crop_source_transform(sources, min_, max_, name="crop-trafo",
                                                 source_names_after_transform=names_after_trafo,
                                                 center_at_origin=True)
    ]
    return trafos


def add_transformed_grid():
    view_name = "transformed-grid"
    sources = get_sources()
    crops = get_crops()
    view = mobie.metadata.get_grid_view(DS, view_name, sources, use_transformed_grid=True, menu_name="test",
                                        additional_source_transforms=crops)
    mobie.metadata.add_view_to_dataset(DS, view_name, view, bookmark_file_name="test_views")


if __name__ == "__main__":
    # add_merged_grid()
    add_transformed_grid()
