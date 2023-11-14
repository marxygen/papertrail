"""
Contains methods to make requests to the Arxiv's API

See https://info.arxiv.org/help/api/user-manual.html
"""
from typing import Iterator, Optional, Union
from arxiv.paper_info import Author, PaperInfo
import atoma

from exceptions import NoPDFForPaper
from utils.web import make_request


def get_paper_by_id(arxiv_id: Optional[str]) -> Union[PaperInfo, None]:
    """
    Fetch paper metadata by its Arxiv ID

    :param arxiv_id: Arxiv ID of the paper
    :return: PaperInfo if the paper exists
    """
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    response = make_request(url)
    response.raise_for_status()

    content = atoma.parse_atom_bytes(response.content)

    if not content.entries:
        return None

    entry = content.entries[0]
    pdf_links = [
        l for l in entry.links if l.title == "pdf" and l.type_ == "application/pdf"
    ]
    if not pdf_links:
        raise NoPDFForPaper(arxiv_id)
    else:
        pdf_link = pdf_links[0].href

    return PaperInfo(
        arxiv_id=arxiv_id,
        category_codes=[cat.term for cat in entry.categories],
        title=entry.title.value,
        abstract=entry.summary.value.replace('\n', ' '),
        published=entry.published,
        updated=entry.updated,
        authors=[
            Author(name=author.name, email=author.email) for author in entry.authors
        ],
        pdf_link=pdf_link,
    )
