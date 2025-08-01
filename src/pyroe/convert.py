import logging
import json
from typing import Literal
from pathlib import Path

from pyroe.load_fry import load_fry
from pyroe.load_fry import process_output_format
from pyroe.pyroe_utils import OutputFormats


def validate_convert_args(
    output_format: Literal["gtf", "gff", "gff3"],
    geneid_to_name: str,
    output_structure: Literal["scRNA", "snRNA", "raw", "velocity"],
) -> None:
    """
    Perform validation of the arguments for the covert sub-command.
    This will e.g. make sure that the input exists, that the output
    format is supported, and that the `output-structure` option makes
    sense as parsed.
    """
    import ast
    import sys
    import pathlib

    if output_format not in OutputFormats:
        print(f"The output format {output_format} was invalid")
        sys.exit(1)

    if geneid_to_name is not None:
        p = pathlib.Path(geneid_to_name)
        if not (p.is_file() or p.is_fifo()):
            print(f"The path {geneid_to_name} doesn't point to a valid file")
            sys.exit(1)

    # if we don't have one of these, then attempt to covert
    # the string to a dictionary.
    out_struct = {}
    if output_structure in ["scRNA", "snRNA", "raw", "velocity"]:
        output_structure = process_output_format(output_structure, True)
    else:
        try:
            out_struct = ast.literal_eval(output_structure)
            output_structure = process_output_format(out_struct, True)
        except Exception:
            print(f"Could not parse {output_structure} argument to --output-structure")
            sys.exit(1)


def get_id_to_name_map(id_to_name_file):
    d = {}
    with open(id_to_name_file) as ifile:
        for line in ifile:
            toks = line.rstrip().split("\t")
            d[toks[0]] = toks[1]
    return d


def convert_id_to_name(adata, id_to_name):
    unmapped = adata.var_names[adata.var_names.map(id_to_name).isna()].tolist()
    # drop the unmappable names and covnert the rest
    adata = adata[:, ~adata.var_names.map(id_to_name).isna()]
    # make the names unique
    adata.var_names = adata.var_names.map(id_to_name)
    adata.var_names_make_unique()
    return (adata, unmapped)


def convert(
    quant_dir: Path,
    output: Path,
    output_structure: Literal["scRNA", "snRNA", "raw", "velocity"],
    output_format: Literal["gtf", "gff", "gff3"],
    geneid_to_name: str,
) -> None:
    # first make sure that the input is such that
    # the conversion makes sense
    validate_convert_args(
        output_format=output_format,
        geneid_to_name=geneid_to_name,
        output_structure=output_structure,
    )
    # offload the work of loading the input to `load_fry`
    A = load_fry(quant_dir, output_format=output_structure, quiet=True)

    id_to_name = geneid_to_name
    if id_to_name is not None:
        id_name_map = get_id_to_name_map(id_to_name)
        A, unmapped = convert_id_to_name(A, id_name_map)
        if len(unmapped) > 0:
            logging.info(f"There were {len(unmapped)} gene ids without a mapped name.")
            uout = f"{output}_unmapped_ids.json"
            logging.info(f"Writing them to {uout}.")
            udict = {"unmapped_geneids": unmapped}
            with open(uout, "w") as f:
                json.dump(udict, f, indent=4, sort_keys=True)

    # write the output in the requested format
    output_fn = {
        "h5ad": A.write,
        "loom": A.write_loom,
        "csvs": A.write_csvs,
        "zarr": A.write_zarr,
    }

    if output_format in output_fn:
        output_fn[output_format](output)
