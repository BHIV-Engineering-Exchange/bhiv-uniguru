from dataclasses import dataclass


@dataclass(frozen=True)
class Provenance:
    source_text: str
    chapter: str = ""
    verse: str = ""
    commentary: str = ""
    author: str = ""
    edition: str = ""
    translator: str = ""
    validation_status: str = "UNVERIFIED"
