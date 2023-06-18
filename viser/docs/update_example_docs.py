"""Helper script for updating the auto-generated examples pages in the documentation."""

from __future__ import annotations

import dataclasses
import pathlib
import shutil
from typing import Iterable

import m2r2
import tyro


@dataclasses.dataclass
class ExampleMetadata:
    index: str
    index_with_zero: str
    source: str
    title: str
    description: str

    @staticmethod
    def from_path(path: pathlib.Path) -> ExampleMetadata:
        # 01_functions -> 01, _, functions.
        index, _, _ = path.stem.partition("_")

        # 01 -> 1.
        index_with_zero = index
        index = str(int(index))

        source = path.read_text().strip()

        docstring = source.split('"""')[1].strip()

        title, _, description = docstring.partition("\n")

        return ExampleMetadata(
            index=index,
            index_with_zero=index_with_zero,
            source=source.partition('"""')[2].partition('"""')[2].strip(),
            title=title,
            description=description.strip(),
        )


def get_example_paths(examples_dir: pathlib.Path) -> Iterable[pathlib.Path]:
    return filter(
        lambda p: not p.name.startswith("_"), sorted(examples_dir.glob("*.py"))
    )


REPO_ROOT = pathlib.Path(__file__).absolute().parent.parent


def main(
    examples_dir: pathlib.Path = REPO_ROOT / "examples",
    sphinx_source_dir: pathlib.Path = REPO_ROOT / "docs" / "source",
) -> None:
    example_doc_dir = sphinx_source_dir / "examples"
    shutil.rmtree(example_doc_dir)
    example_doc_dir.mkdir()

    for path in get_example_paths(examples_dir):
        ex = ExampleMetadata.from_path(path)

        relative_dir = path.parent.relative_to(examples_dir)
        target_dir = example_doc_dir / relative_dir
        target_dir.mkdir(exist_ok=True, parents=True)

        (target_dir / f"{path.stem}.rst").write_text(
            "\n".join(
                [
                    (
                        ".. Comment: this file is automatically generated by"
                        " `update_example_docs.py`."
                    ),
                    "   It should not be modified manually.",
                    "",
                    f"{ex.title}",
                    "==========================================",
                    "",
                    m2r2.convert(ex.description),
                    "",
                    "",
                    ".. code-block:: python",
                    "        :linenos:",
                    "",
                    "",
                    "\n".join(
                        f"        {line}".rstrip() for line in ex.source.split("\n")
                    ),
                    "",
                ]
            )
        )


if __name__ == "__main__":
    tyro.cli(main, description=__doc__)
