"""Create validated document chunks from character ranges in source text."""

from typing import List

from .models import DocumentChunk, MinimalSource

import re
import ast


def _create_chunk(
    original_text: str,
    file_path: str,
    start: int,
    end: int,
    max_chunk_size: int = 2000,
) -> DocumentChunk:
    """Create a document chunk for a validated character range."""
    if max_chunk_size <= 0:
        raise ValueError("max_chunk_size must be greater than 0.")

    if start < 0:
        raise ValueError("start must be non-negative.")

    if end > len(original_text):
        raise ValueError(
            "end must not exceed the length of original_text."
        )

    if end <= start:
        raise ValueError("end must be greater than start.")

    if (end - start) > max_chunk_size:
        raise ValueError("end - start must not exceed max_chunk_size.")
    # Here we are slicing the text.
    passage_text = original_text[start:end]

    source = MinimalSource(
        file_path=file_path,
        first_character_index=start,
        last_character_index=end,
    )

    chunk = DocumentChunk(text=passage_text, source=source)
    return chunk


def chunk_markdown(
    original_text: str,
    file_path: str,
    max_chunk_size: int = 2000,
) -> List[DocumentChunk]:
    """Split Markdown into size-limited chunks while preserving sections."""
    if max_chunk_size <= 0:
        raise ValueError("max_chunk_size must be greater than 0.")

    if not file_path:
        raise ValueError("file_path must not be empty.")

    if not original_text:
        return []

    section_starts: List[int] = []

    markdown_heading = (
        r"^(#{1,6})[ \t]*(.*?)[ \t]*\n(.*?)(?=(?:^#{1,6}[ \t])|\Z)"
    )

    # Casting to re.RegexFlag satisfies strict type-checker requirements.
    combined_flags = re.RegexFlag(re.M | re.S)

    for match in re.finditer(
        markdown_heading, original_text, flags=combined_flags
    ):
        section_starts.append(match.start())
    if not section_starts or section_starts[0] != 0:
        section_starts.insert(0, 0)
    section_starts.append(len(original_text))

    chunks: List[DocumentChunk] = []

    for index in range(len(section_starts) - 1):
        section_start = section_starts[index]
        section_end = section_starts[index + 1]

        section_size = section_end - section_start
        if section_size <= max_chunk_size:
            chunk = _create_chunk(
                original_text,
                file_path,
                section_start,
                section_end,
                max_chunk_size,
            )
            chunks.append(chunk)
        else:
            current_start = section_start

            while section_end - current_start > max_chunk_size:
                furthest_allowed_position = current_start + max_chunk_size
                paragraph_boundary = original_text.rfind(
                    "\n\n", current_start, furthest_allowed_position
                )
                if paragraph_boundary != -1:
                    split_end = paragraph_boundary + 2
                else:
                    one_line = original_text.rfind(
                        "\n", current_start, furthest_allowed_position
                    )

                    if one_line != -1:
                        split_end = one_line + 1
                    else:
                        split_end = furthest_allowed_position
                chunk = _create_chunk(
                    original_text,
                    file_path,
                    current_start,
                    split_end,
                    max_chunk_size,
                )
                chunks.append(chunk)
                current_start = split_end
            if current_start < section_end:
                find_chunk = _create_chunk(
                    original_text,
                    file_path,
                    current_start,
                    section_end,
                    max_chunk_size,
                )
                chunks.append(find_chunk)
    return chunks


def chunk_python(
    original_text: str,
    file_path: str,
    max_chunk_size: int = 2000,
) -> List[DocumentChunk]:
    if max_chunk_size <= 0:
        raise ValueError("max_chunk_size must be greater than 0.")
    if not file_path:
        raise ValueError("file_path must not be empty.")
    if not original_text:
        return []
    try:
        syntax_tree = ast.parse(original_text)
    except SyntaxError as se:
        raise ValueError(f"Unable to parse Python file: {file_path}") from se

    # Each node represents one of these:
    # FunctionDef is a regular function.
    # AsyncFunctionDef is an async function.
    # ClassDef is a class.
    # syntax_tree.body contains top-level statements in source order.

    definition_nodes: List[
        ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
    ] = []
    for node in syntax_tree.body:
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            definition_nodes.append(node)

    line_starts: List[int] = [0]
    current_position: int = 0
    lines = original_text.splitlines(keepends=True)
    for line in lines:
        current_position += len(line)
        line_starts.append(current_position)
    return []
