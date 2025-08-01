from enum import StrEnum


class FileFormats(StrEnum):
    gtf = "gtf"
    gff = "gff"
    gff3 = "gff3"


class OutputFormats(StrEnum):
    h5ad = "h5ad"
    loom = "loom"
    csvs = "csvs"
    zarr = "zarr"


class OutputStructure(StrEnum):
    scrna = "scRNA"
    snrna = "snRNA"
    raw = "raw"
    velocity = "velocity"
    sa = "S+A"
    all_types = "all"
    usa = "U+S+A"


def say(quiet, words):
    if not quiet:
        print(words)


def check_dataset_ids(n_ds, dataset_ids):
    # check the validity of dataset_ids
    invalid_ids = []
    for idx, dataset_id in enumerate(dataset_ids):
        if isinstance(dataset_id, int):
            if dataset_id > n_ds or dataset_id < 1:
                print(f"Found invalid dataset id '{dataset_id}', ignored.")
                invalid_ids.append(idx)
        else:
            print(f"Found invalid dataset id '{dataset_id}', ignored.")
            invalid_ids.append(idx)

    if invalid_ids:
        for i in reversed(invalid_ids):
            del dataset_ids[i]

    return dataset_ids
