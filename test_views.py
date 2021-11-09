import mobie

DS = "./data/membrane"


def get_sources(n_sources=4):
    metadata = mobie.metadata.read_dataset_metadata(DS)
    im_sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == "image"]
    seg_sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == "segmentation"]
    assert len(im_sources) == len(seg_sources)
    sources = [[im, seg] for im, seg in zip(im_sources, seg_sources)][:n_sources]
    return sources


def get_trafos(source_type, n_sources=4):
    from elf.transformation import affine_matrix_3d, native_to_bdv

    metadata = mobie.metadata.read_dataset_metadata(DS)
    sources = [name for name, source in metadata["sources"].items() if list(source.keys())[0] == source_type]
    sources = sources[:n_sources]
    names_after_trafo = [source + "_transformed" for source in sources]

    params = affine_matrix_3d(rotation=(45.0, 0.0, 0.0))
    params = native_to_bdv(params)

    return mobie.metadata.get_affine_source_transform(
        sources, params, name=f"trafos-{source_type}",
        source_names_after_transform=names_after_trafo
    )


def add_transformed_grid():
    view_name = "test-transformed-grid"
    sources = get_sources()
    trafos = [get_trafos("image"), get_trafos("segmentation")]
    grid_sources = [[name + "_transformed" for name in names] for names in sources]
    view = mobie.metadata.get_grid_view(DS, view_name, sources,
                                        use_transformed_grid=True, menu_name="test",
                                        grid_sources=grid_sources,
                                        additional_source_transforms=trafos)
    mobie.metadata.add_view_to_dataset(DS, view_name, view, bookmark_file_name="test_views")


if __name__ == "__main__":
    add_transformed_grid()
