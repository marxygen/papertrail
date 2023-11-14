from dataclasses import dataclass
from datetime import datetime
from typing import List

from pdf.parsing import get_references


@dataclass(kw_only=True)
class Author:
    name: str
    email: str


@dataclass(kw_only=True, slots=True)
class PaperInfo:
    arxiv_id: str
    category_codes: List[str]

    title: str
    abstract: str

    published: datetime
    updated: datetime
    authors: List[Author]

    pdf_link: str
    reference_ids: List[str] = None

    def load_references(self) -> None:
        self.reference_ids = get_references(self.pdf_link)

    @property
    def google_scholar_url(self) -> str:
        return f"https://scholar.google.com/scholar_lookup?arxiv_id={self.arxiv_id}"

    @property
    def arxiv_url(self) -> str:
        return f"https://arxiv.org/abs/{self.arxiv_id}"
