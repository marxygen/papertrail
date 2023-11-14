class PapertrailException(Exception):
    pass


class HarvestingException(PapertrailException):
    pass


class NoPDFForPaper(HarvestingException):
    pass


class InvalidPDFForPaper(HarvestingException):
    pass
