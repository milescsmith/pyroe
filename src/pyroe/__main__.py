#!/usr/bin/env python

import logging
from shutil import which


from pyroe.make_txome import make_splici_txome, make_spliceu_txome
from pyroe.fetch_processed_quant import fetch_processed_quant
from pyroe.convert import convert
from pyroe.id_to_name import id_to_name
from pyroe.pyroe_utils import FileFormats, OutputFormats, OutputStructure
from typing import Annotated

from pathlib import Path
from pyroe import __version__
from rich import print as rprint

import typer

app = typer.Typer(
    name="pyroe",
    help="The pyroe package provides useful functions to support alevin-fry ecosystem.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def version_callback(value: bool) -> None:  # noqa FBT001
    """Prints the version of the package."""
    if value:
        rprint(f"[yellow]{{MODULE}}[/] version: [bold blue]{__version__}[/]")
        raise typer.Exit()


@app.command(no_args_is_help=True)
def makeSplici(
    genome_path: Annotated[
        Path,
        typer.Argument(help="The path to a genome fasta file.", exists=True),
    ],
    gtf_path: Annotated[
        Path, typer.Argument(help="The path to a gtf file.", exists=True)
    ],
    read_length: Annotated[
        int,
        typer.Argument(
            help="The read length of the single-cell experiment being processed (determines flank size).",
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Argument(
            help="The output directory where splici reference files will be written.",
        ),
    ],
    filename_prefix: Annotated[
        str,
        typer.Option(
            "--filename-prefix",
            help="The file name prefix of the generated output files.",
        ),
    ] = "splici",
    flank_trim_length: Annotated[
        int,
        typer.Option(
            "--flank-trim-length",
            help="Determines the amount subtracted from the read length to get the flank length.",
        ),
    ] = 5,
    extra_spliced: Annotated[
        Path | None,
        typer.Option(
            "--extra-spliced",
            help="The path to an extra spliced sequence fasta file.",
        ),
    ] = None,
    extra_unspliced: Annotated[
        Path | None,
        typer.Option(
            "--extra-unspliced",
            help="The path to an extra unspliced sequence fasta file.",
        ),
    ] = None,
    bt_path: Annotated[
        Path | None,
        typer.Option(
            "--bt-path",
            help="The path to bedtools v2.30.0 or greater.",
        ),
    ] = None,
    no_bt: Annotated[
        bool,
        typer.Option(
            "--no-bt",
            help="A flag indicates whether bedtools will be used for generating splici reference files.",
        ),
    ] = False,
    dedup_seqs: Annotated[
        bool,
        typer.Option(
            "--dedup-seqs",
            help="A flag indicates whether identical sequences will be deduplicated.",
        ),
    ] = False,
    no_flanking_merge: Annotated[
        bool,
        typer.Option(
            "--no-flanking-merge",
            help="A flag indicates whether flank lengths will be considered when merging introns.",
        ),
    ] = False,
):
    """
    Make spliced + intronic reference
    """
    # parser_makeSplici.set_defaults(command="make-spliced+intronic")
    if not no_bt and bt_path is None:
        bt_path = which("bedtools")

    make_splici_txome(
        genome_path=genome_path,
        gtf_path=gtf_path,
        read_length=read_length,
        output_dir=output_dir,
        flank_trim_length=flank_trim_length,
        filename_prefix=filename_prefix,
        extra_spliced=extra_spliced,
        extra_unspliced=extra_unspliced,
        dedup_seqs=dedup_seqs,
        no_bt=no_bt,
        bt_path=bt_path,
        no_flanking_merge=no_flanking_merge,
    )


@app.command(no_args_is_help=True)
def makeSpliceu(
    # make-spliceu
    genome_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="The path to a genome fasta file.",
        ),
    ],
    gtf_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="The path to a gtf file.",
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Argument(
            file_okay=False,
            dir_okay=True,
            writable=True,
            help="The output directory where Spliceu reference files will be written.",
        ),
    ],
    filename_prefix: Annotated[
        str,
        typer.Option(
            "--filename-prefix",
            help="The file name prefix of the generated output files.",
        ),
    ] = "spliceu",
    extra_spliced: Annotated[
        Path | None,
        typer.Option(
            "--extra-spliced",
            readable=True,
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="The path to an extra spliced sequence fasta file.",
        ),
    ] = None,
    extra_unspliced: Annotated[
        Path | None,
        typer.Option(
            "--extra-unspliced",
            readable=True,
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="The path to an extra unspliced sequence fasta file.",
        ),
    ] = None,
    bt_path: Annotated[
        Path | None,
        typer.Option(
            readable=True,
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="The path to bedtools v2.30.0 or greater.",
        ),
    ] = None,
    no_bt: Annotated[
        bool,
        typer.Option(
            "--no-bt",
            help="A flag indicates whether bedtools will be used for generating Spliceu reference files.",
        ),
    ] = False,
    dedup_seqs: Annotated[
        bool,
        typer.Option(
            "--dedup-seqs",
            help="A flag indicates whether identical sequences will be deduplicated.",
        ),
    ] = False,
):
    """
    Make spliced + unspliced reference
    """
    make_spliceu_txome(
        genome_path=genome_path,
        gtf_path=gtf_path,
        output_dir=output_dir,
        filename_prefix=filename_prefix,
        extra_spliced=extra_spliced,
        extra_unspliced=extra_unspliced,
        dedup_seqs=dedup_seqs,
        no_bt=no_bt,
        bt_path=bt_path,
    )


"""
    # parse available datasets
    available_datasets = fetch_processed_quant()
    epilog = "\n".join(
        [
            "".join([f"{idx+1}", ". ", dataset_name])
            for (idx, dataset_name) in zip(
                range(available_datasets.shape[0]),
                available_datasets["dataset_name"].tolist(),
            )
        ]
    )
    epilog = "\n".join(["Index of the available datasets:", epilog])
"""


@app.command(no_args_is_help=True)
def fetchQuant(
    dataset_ids: Annotated[
        list[int],
        typer.Argument(
            help="The ids of the datasets to fetch",
        ),
    ],
    fetch_dir: Annotated[
        Path,
        typer.Option(
            "--fetch-dir",
            help="The path to a directory for storing fetched datasets.",
            writable=True,
        ),
    ] = Path.cwd().joinpath("processed_quant"),
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="A flag indicates whether existing datasets will be redownloaded by force.",
        ),
    ] = False,
    delete_tar: Annotated[
        bool,
        typer.Option(
            "--delete-tar",
            help="A flag indicates whether fetched tar files stored in the quant_tar directory under the provided fetch_dir should be deleted.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="A flag indicates whether help messaged should not be printed.",
        ),
    ] = False,
):
    """
    Fetch processed quant results
    """
    fetch_processed_quant(
        dataset_ids=dataset_ids,
        fetch_dir=fetch_dir,
        force=force,
        delete_tar=delete_tar,
        quiet=quiet,
    )


@app.command(no_args_is_help=True)
def parser_id_to_name(
    gtf_file: Annotated[
        Path,
        typer.Argument(
            help="The GTF input file.",
            exists=True,
            readable=True,
            file_okay=True,
            dir_okay=False,
        ),
    ],
    output: Annotated[
        Path,
        typer.Argument(
            help="The path to where the output tsv file will be written.",
            writable=True,
        ),
    ],
    file_format: Annotated[
        FileFormats | None,
        typer.Option(
            "--format",
            help="The input format of the file (must be either GTF or GFF3). This will be inferred from the filename, but if that fails it can be provided explicitly.",
        ),
    ] = None,
):
    """
    Generate a gene id to gene name mapping file from a GTF.
    """
    id_to_name(
        gtf_file=gtf_file,
        output=output,
        file_format=file_format,
    )


@app.command(no_args_is_help=True, name="convert")
def convert_cli(
    quant_dir: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=True,
            file_okay=False,
            readable=True,
            help="The input quantification directory containing the matrix to be converted.",
        ),
    ],
    output: Annotated[
        Path,
        typer.Argument(
            help="The output name where the quantification matrix should be written. For `csvs` output format, this will be a directory. For all others, it will be a file.",
            writable=True,
        ),
    ],
    output_structure: Annotated[
        OutputStructure,
        typer.Option(
            "--output-structure",
            help="The structure that U,S and A counts should occupy in the output matrix.",
        ),
    ],
    output_format: Annotated[
        OutputFormats,
        typer.Option(
            "--output-format",
            help="The format in which the output should be written.",
        ),
    ] = OutputFormats.h5ad,
    geneid_to_name: Annotated[
        str | None,
        typer.Option(
            "--geneid-to-name",
            help="A 2 column tab-separated list of gene ID to gene name mappings. Providing this file will project gene IDs to gene names in the output.",
        ),
    ] = None,
):
    """
    Convert alevin-fry quantification result to another format.
    """
    convert(
        quant_dir=quant_dir,
        output=output,
        output_structure=output_structure,
        output_format=output_format,
        geneid_to_name=geneid_to_name,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()
