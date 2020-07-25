#!/usr/bin/env python3

"""Tool to extract code snippets from the README into separate files."""

import argparse
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional

ignored_flake8_rules = {
    "D100",  # missing module-level docstring
}


class SnippetFormat(metaclass=ABCMeta):
    """A format for code snippets."""

    def __init__(self, start_line: str) -> None:
        self.start_line = start_line

    @classmethod
    def attempt_start(cls, line: str) -> Optional['SnippetFormat']:
        """Attempt to start a code block."""
        return cls(line) if cls.is_start(line) else None

    @classmethod
    @abstractmethod
    def is_start(cls, line: str) -> bool:
        """Check if a line is the start of the code block."""
        raise NotImplementedError

    @abstractmethod
    def is_end(self, line: str) -> bool:
        """Check if a line is the end of the code block."""
        raise NotImplementedError

    @abstractmethod
    def is_unchecked(self) -> bool:
        """Check if the code block should be checked."""
        raise NotImplementedError


class PythonMarkdownFormat(SnippetFormat):
    """
    Python snippets in markdown.
    
    Code snippets begin with a line starting with "```python" and end at a line
    starting with "```".
    """

    @classmethod
    def is_start(cls, line: str) -> bool:
        """Check if a line is the start of the code block."""
        return line.startswith("```python")

    def is_end(self, line: str) -> bool:
        """Check if a line is the end of the code block."""
        return line.startswith("```")

    def is_unchecked(self) -> bool:
        """Check if the code block should be checked."""
        return "unchecked" in self.start_line


FORMATS = [PythonMarkdownFormat]


class SnippetWriter:
    """Writes files with sequentially increasing numbers into a directory."""

    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.next_num = 0

    def write(self, contents: str) -> None:
        """Write the next file using the given contents."""
        contents = f"# noqa: {','.join(ignored_flake8_rules)}\n{contents}"
        path = self.output_path / f"snippet{self.next_num:04d}.py"
        with open(path, "w") as file:
            file.write(contents)
        self.next_num += 1


def extract(input_path: Path, snippet_writer: SnippetWriter) -> None:
    """Look for code snippets in input_path and send them to the snippet_writer."""
    current_code_block = None
    current_block_format: Optional[SnippetFormat] = None
    with open(input_path, "r") as input_file:
        for line in input_file:
            if current_code_block is not None:
                if current_block_format is None:
                    raise Exception("Unreachable code.")
                else:
                    if current_block_format.is_end(line):
                        # end code block
                        if not current_block_format.is_unchecked():
                            snippet_writer.write(current_code_block)
                        current_code_block = None
                        current_block_format = None
                    else:
                        # line inside a code block
                        current_code_block += line
            else:
                for snippet_format in FORMATS:
                    attempt = snippet_format.attempt_start(line)
                    if attempt is not None:
                        # start code block
                        current_code_block = ""
                        current_block_format = attempt
                        break


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    extract(args.input_file, SnippetWriter(args.output_dir))


if __name__ == "__main__":
    main()
