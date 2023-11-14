# !pip3 install pdfminer.six
from pathlib import Path
from tempfile import NamedTemporaryFile
from utils.url import is_valid_url
import requests
from pdfminer.high_level import extract_text


def get_contents(path_or_url: str) -> str:
    """
    Get PDF file contents

    :param path_or_url: Path to the file in the local filesystem or a URL to it
    :return: File contents as a string
    """
    if is_valid_url(path_or_url):
        response = requests.get(path_or_url)
        response.raise_for_status()

        destination = NamedTemporaryFile()
        destination.write(response.content)
        path = destination.name
    else:
        path = Path(path_or_url)
        assert path.exists(), f"Provided path '{path_or_url}' does not exist"

    return extract_text(path)
