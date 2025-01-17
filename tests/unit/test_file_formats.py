from pathlib import Path

import pytest

from ehrql.file_formats import ValidationError, get_file_extension, read_dataset
from ehrql.file_formats.arrow import ArrowDatasetReader
from ehrql.file_formats.csv import CSVDatasetReader, CSVGZDatasetReader


@pytest.mark.parametrize(
    "filename,extension",
    [
        (None, ".csv"),
        (Path("a/b.c/file.txt"), ".txt"),
        (Path("a/b.c/file.txt.foo"), ".foo"),
        (Path("a/b.c/file.txt.gz"), ".txt.gz"),
        (Path("a/b.c/file"), ""),
    ],
)
def test_get_file_extension(filename, extension):
    assert get_file_extension(filename) == extension


def test_read_dataset_rejects_unsupported_file_types():
    with pytest.raises(ValidationError, match="Unsupported file type: .xyz"):
        read_dataset(Path("some_file.xyz"), {})


def test_read_dataset_raises_error_for_missing_files():
    missing_file = Path(__file__).parent / "no_such_file.csv"
    with pytest.raises(ValidationError, match=f"Missing file: {missing_file}"):
        read_dataset(missing_file, {})


@pytest.mark.parametrize(
    "reader_class",
    [
        CSVDatasetReader,
        CSVGZDatasetReader,
        ArrowDatasetReader,
    ],
)
def test_dataset_reader_constructor_rejects_non_path(reader_class):
    with pytest.raises(ValidationError, match="must be a pathlib.Path instance"):
        reader_class("some/string/path", {})
