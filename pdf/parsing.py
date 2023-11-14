import re
from typing import Iterable, List
from pdf.reading import get_contents


def get_references(
    path_or_url: str,
    reference_formats: Iterable[str] = (r"arXiv:[0-9]+.[0-9]+", r"abs/[0-9]+.[0-9]+"),
) -> List[str]:
    """
    Get list of Arxiv IDs to referenced papers

    :param path_or_url: Path to the file in the local filesystem or a URL to it
    :param reference_formats: Reference formats to use. Defaults to recognizing "arXiv:1610.02357" and "abs/1512.00567"
    :return: List of Arxiv IDs to referenced papers
    """
    content = get_contents(path_or_url)
    # Sometimes, there is no PDF. In this case, `content` will be `None`.
    if not content:
        return []

    references = []
    for reference_format in reference_formats:
        pattern = re.compile(reference_format)
        for match in re.findall(pattern, content):
            if not match:
                continue

            # Currently, we're just extracting all numbers and a dot from the string.
            # NOTE: even if the reference is given as "arXiv:1705.03122v2", the valid Arxiv ID is still "1705.03122"
            # TODO: extract all entries, even if they don't have an Arxiv page. Easier said than done, but it'll help later
            references.append("".join([s for s in match if s.isdigit() or s == "."]))

    return references
