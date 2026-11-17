"""Pydantic schemas for RAG questions, source passages, and result batches."""

from typing import List
import uuid

from pydantic import BaseModel, Field


class MinimalSource(BaseModel):
    """Locate a source passage by file path and character positions.

    The passage text is not stored here; the path and indices identify it
    in the source file.
    """

    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """Represent a question without an answer or supporting sources.

    If no question_id is supplied, generate a UUID string to identify the
    question and associate it with subsequent retrieval and answer results.
    """

    question: str
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class AnsweredQuestion(UnansweredQuestion):
    """Extend a question with its answer and supporting source passages.

    Inherit the question text and ID, including automatic ID generation.
    """

    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """Group answered and unanswered questions into a single dataset."""

    rag_questions: List[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """Record the source passages retrieved for one question.

    The question text and ID link these results to the original question.
    retrieved_sources contains passage locations, rather than passage text.
    """

    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """Extend a question's retrieval results with an answer."""

    answer: str


class StudentSearchResults(BaseModel):
    """Collect retrieval results for a batch of questions.

    k records the requested number of retrieved sources per question.
    This model does not enforce that each result contains exactly k sources.
    """

    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """Collect answers and their retrieval results for a batch of questions.

    Each entry includes the question, its ID, retrieved sources, and answer.
    k records the requested source count per question without enforcing it.
    """

    search_results: List[MinimalAnswer]
    k: int


class DocumentChunk(BaseModel):
    """Store a passage and its location in the original file."""
    text: str
    source: MinimalSource
