import os
import mobie

DS = "./data/membrane"


def get_split_sources(n_sources=4):
    metadata = mobie.metadata.read_dataset_metadata(DS)
    im_sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == "image"]
    seg_sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == "segmentation"]
    assert len(im_sources) == len(seg_sources)
    return im_sources[:n_sources], seg_sources[:n_sources]


def add_merged_grid():
    view_name = "test-merged-grid"
    im_sources, seg_sources = get_split_sources()

    trafos = [
        mobie.metadata.get_merged_grid_source_transform(
            im_sources[:2], "images-well1", name="well1-images"
        ),
        mobie.metadata.get_merged_grid_source_transform(
            seg_sources[:2], "segs-well1", name="well1-segmentations"
        ),
        mobie.metadata.get_merged_grid_source_transform(
            im_sources[2:], "images-well2", name="well2-images"
        ),
        mobie.metadata.get_merged_grid_source_transform(
            seg_sources[2:], "segs-well2", name="well2-segmentations"
        ),
        mobie.metadata.get_merged_grid_source_transform(
            ["images-well1", "images-well2"], "all-images", name="images"
        ),
        mobie.metadata.get_merged_grid_source_transform(
            ["segs-well1", "segs-well2"], "all-segs", name="segmentations"
        )
    ]

    site_sources = {
        "well1_0": [im_sources[0], seg_sources[0]],
        "well1_1": [im_sources[1], seg_sources[1]],
        "well2_0": [im_sources[2], seg_sources[2]],
        "well2_1": [im_sources[3], seg_sources[3]],
    }
    tab_path = os.path.join(DS, "tables", "sites", "default.tsv")
    mobie.tables.compute_source_annotation_table(["well1_0", "well1_1", "well2_0", "well2_1"], tab_path,
                                                 wells=["well1", "well1", "well2", "well2"])
    site_table_data = {"tsv": {"relativePath": "tables/sites"}}

    well_sources = {"well1": ["images-well1", "segs-well1"], "well2": ["images-well2", "segs-well2"]}
    tab_path = os.path.join(DS, "tables", "wells", "default.tsv")
    mobie.tables.compute_source_annotation_table(["well1", "well2"], tab_path, wells=["well1", "well2"])
    well_table_data = {"tsv": {"relativePath": "tables/wells"}}

    displays = [
        mobie.metadata.get_image_display("images", ["all-images"]),
        mobie.metadata.get_segmentation_display("segmentations", ["all-segs"], tables=["default.tsv"]),
        mobie.metadata.get_source_annotation_display(
            "sites", sources=site_sources, table_data=site_table_data, tables=["default.tsv"]
        ),
        mobie.metadata.get_source_annotation_display(
            "wells", sources=well_sources, table_data=well_table_data, tables=["default.tsv"]
        ),
    ]

    view = {
        "isExclusive": True,
        "sourceDisplays": displays,
        "sourceTransforms": trafos,
        "uiSelectionGroup": "test"
    }
    mobie.metadata.add_view_to_dataset(DS, view_name, view, bookmark_file_name="test_views")


def get_sources(n_sources=4):
    metadata = mobie.metadata.read_dataset_metadata(DS)
    im_sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == "image"]
    seg_sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == "segmentation"]
    assert len(im_sources) == len(seg_sources)
    sources = [[im, seg] for im, seg in zip(im_sources, seg_sources)][:n_sources]
    return sources


def get_crops(source_type, n_sources=4):
    metadata = mobie.metadata.read_dataset_metadata(DS)
    sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == source_type]
    sources = sources[:n_sources]
    names_after_trafo = [source + "_cropped" for source in sources]

    shape = (130, 816, 1636)
    resolution = (0.22, 0.1, 0.1)
    shape = tuple(sh * re for sh, re in zip(shape, resolution))
    halo = (4.0, 12.0, 12.0)
    min_ = [sh // 2 - ha for sh, ha in zip(shape, halo)]
    max_ = [sh // 2 + ha for sh, ha in zip(shape, halo)]

    return mobie.metadata.get_crop_source_transform(sources, min_, max_, name=f"crops-{source_type}",
                                                    source_names_after_transform=names_after_trafo,
                                                    center_at_origin=True)


def add_transformed_grid():
    view_name = "test-transformed-grid"
    sources = get_sources()
    crops = [get_crops("image"), get_crops("segmentation")]
    grid_sources = [[name + "_cropped" for name in names] for names in sources]
    view = mobie.metadata.get_grid_view(DS, view_name, sources,
                                        use_transformed_grid=True, menu_name="test",
                                        grid_sources=grid_sources,
                                        additional_source_transforms=crops)
    mobie.metadata.add_view_to_dataset(DS, view_name, view, bookmark_file_name="test_views")


if __name__ == "__main__":
    add_merged_grid()
    # add_transformed_grid()
