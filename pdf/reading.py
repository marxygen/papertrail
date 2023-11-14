# !pip3 install pdfminer.six
from pathlib import Path
from tempfile import NamedTemporaryFile

from exceptions import InvalidPDFForPaper
from utils.web import is_valid_url, make_request
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFException


def get_contents(path_or_url: str) -> str | None:
    """
    Get PDF file contents

    :param path_or_url: Path to the file in the local filesystem or a URL to it
    :return: File contents as a string
    """
    if is_valid_url(path_or_url):
        response = make_request(path_or_url)
        response.raise_for_status()

        # Sometimes, there is no PDF available for the paper, for example
        #
        # PDF unavailable for cs/9907004...
        # The author has provided no source to generate PDF, and no PDF.
        #
        # Then, we just return `None`
        if "pdf" not in response.headers["Content-Type"]:
            return None

        destination = NamedTemporaryFile()
        destination.write(response.content)
        path = destination.name
    else:
        path = Path(path_or_url)
        assert path.exists(), f"Provided path '{path_or_url}' does not exist"

    try:
        return extract_text(path)
    except PDFException as e:
        raise InvalidPDFForPaper(f"Unable to read PDF at {path_or_url}: {e}") from e
