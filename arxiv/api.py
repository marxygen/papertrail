"""
Contains methods to make requests to the Arxiv's API

See https://info.arxiv.org/help/api/user-manual.html
"""
from typing import Iterator, List, Optional, Union
from arxiv.paper_info import Author, PaperInfo
import atoma

from exceptions import NoPDFForPaper
from utils.web import make_request


def parse_entry(entry: atoma.atom.AtomEntry, load_references: bool = False) -> PaperInfo:
    """
    Parse an entry into a `PaperInfo` object

    :param entry:
    :param load_references: If `True`, this paper will be downloaded and the extracted list of references will be added to the resulting `PaperInfo` object
    :return: A `PaperInfo` object
    """
    arxiv_id = "".join([s for s in entry.id_.split('/') if s.isdigit() or s == '.'])
    pdf_links = [
        l for l in entry.links if l.title == "pdf" and l.type_ == "application/pdf"
    ]
    if not pdf_links:
        raise NoPDFForPaper(arxiv_id)
    else:
        pdf_link = pdf_links[0].href

    pi = PaperInfo(
        arxiv_id=arxiv_id,
        category_codes=[cat.term for cat in entry.categories],
        title=entry.title.value.replace('\n', ' '),
        abstract=entry.summary.value.replace('\n', ' '),
        published=entry.published,
        updated=entry.updated,
        authors=[
            Author(name=author.name, email=author.email) for author in entry.authors
        ],
        pdf_link=pdf_link,
    )
    if load_references:
        pi.load_references()

    return pi


def get_paper_by_id(arxiv_id: Optional[str], load_references: bool = False) -> Union[PaperInfo, None]:
    """
    Fetch paper metadata by its Arxiv ID

    :param arxiv_id: Arxiv ID of the paper
    :param load_references: If `True`, this paper will be downloaded and the extracted list of references will be added to the resulting `PaperInfo` object
    :return: PaperInfo if the paper exists
    """
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    response = make_request(url)
    response.raise_for_status()

    content = atoma.parse_atom_bytes(response.content)

    if not content.entries:
        return None

    return parse_entry(content.entries[0], load_references=load_references)


def get_papers_in_category(category_id: str, start: int = 0, batch_size: int = 1_000, load_references: bool = True) -> Iterator[PaperInfo]:
    """
    Makes requests to the Arxiv's API and retrieves PaperInfo entries for papers with the specified category

    :param start: The page to start with (0-based)
    :param category_id: Arxiv's category ID (e.g. "cs.LG")
    :param batch_size: How many entries to fetch at a time
    :param load_references: Whether to load references
    :return:
    """

    def get_entries_from_page(start: int = 0) -> List[PaperInfo] | None:
        # We request papers ordering by the submission date in the ascending order
        url = f"https://export.arxiv.org/api/query?search_query=cat:{category_id}&sortBy=submittedDate&sortOrder=ascending&start={start}"
        response = make_request(url)
        response.raise_for_status()

        content = atoma.parse_atom_bytes(response.content)
        if not content.entries:
            return None

        return [parse_entry(entry, load_references=load_references) for entry in content.entries]

    batch_size = batch_size or 1_000
    while True:
        entries = get_entries_from_page(start)
        if entries:
            start += batch_size
            yield from entries
        else:
            break
