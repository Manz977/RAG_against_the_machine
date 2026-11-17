"""Create validated document chunks from character ranges in source text."""

from typing import List

from sympy import continued_fraction


from .models import DocumentChunk, MinimalSource

import re


def _create_chunk(
    original_text: str,
    file_path: str,
    start: int,
    end: int,
    max_chunk_size: int = 2000,
) -> DocumentChunk:
    """Create a document chunk for a validated character range."""
    if max_chunk_size <= 0:
        raise ValueError("A max size of zero or less is invalid.")

    if start < 0:
        raise ValueError("The start position is in the negative.")

    if end > len(original_text):
        raise ValueError(
            "The end position of the text is greater than the original text."
        )

    if end <= start:
        raise ValueError(
            "The end position shouldn't be less than or equal to the start "
            "position."
        )

    if (end - start) > max_chunk_size:
        raise ValueError(
            "The end minus the start shouldn't be greater than the max "
            "chunk/character count"
        )
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
    if max_chunk_size <= 0:
        raise ValueError(
            "The chunk size shouldn't be zero or a negative number."
        )

    if not file_path:
        raise ValueError("File path is empty, provide or check the file path.")

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
#string.rfind(value, start, end)
            while section_end - current_start > max_chunk_size:
                furthest_allowed_position = current_start + max_chunk_size
                paragraph_boundary = original_text.rfind("\n\n", current_start, furthest_allowed_position)
                if paragraph_boundary != -1: 
                    split_end = paragraph_boundary + 2
                else:
                    one_line = original_text.rfind("\n", current_start,
                    furthest_allowed_position)
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
                
                
            return chunks
