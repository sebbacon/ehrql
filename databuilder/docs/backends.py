import operator

from ..backends.base import BaseBackend
from .common import build_hierarchy


def build_backends():
    backends = sorted(BaseBackend.__subclasses__(), key=operator.attrgetter("__name__"))

    for backend in backends:
        # get the full name for all implemented contracts the backend implements
        tables = [getattr(backend, name) for name in backend.tables]
        contract_classes = [table.implements for table in tables if table.implements]
        contract_names = [
            "/".join([*build_hierarchy(c), c.__name__]) for c in contract_classes
        ]

        yield {
            "name": backend.__name__,
            "contracts": contract_names,
        }
