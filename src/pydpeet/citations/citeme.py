"""
TODO Code taken from : https://github.com/citation-file-format/citeme/tree/master
"""

import functools
import json
import pathlib
from six import iteritems

from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from .html_writer import BibHtmlWriter

# Singleton!
class CiteMe(object):
    # Class variable!
    __instance = None
    __check_fields = True
    __pedantic = False

    # Override new to make this a singleton class
    # taken from http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html#id5
    def __new__(cls):
        if CiteMe.__instance is None:
            CiteMe.__instance = object.__new__(cls)
            # Initialization of class here, because
            # __init__ gets called multiple times
            CiteMe.__instance.references = {}
        return CiteMe.__instance

    def add_reference(self, citation):
        if CiteMe.__check_fields:
            citation.checkFields(CiteMe.__pedantic)

        if citation.type not in self.references:
            self.references[citation.type] = {}

        if citation.handle not in self.references[citation.type]:
            self.references[citation.type][citation.handle] = citation

    def print_references(self):
        for ref_type in self.references:
            for handle, citation in iteritems(self.references[ref_type]):
                #print(ref_type, handle, citation.description)
                print(citation.description)

    def write_to_bibtex(self, filename):
        db = BibDatabase()
        db.entries = []
        for ref_type in self.references:
            for handle, citation in iteritems(self.references[ref_type]):
                description = citation.description
                description['ENTRYTYPE'] = citation.type
                description['ID'] = handle
                db.entries.append(description)
        writer = BibTexWriter()
        with open(filename, 'w') as bibfile:
            bibfile.write(writer.write(db))

    def write_to_html(self, filename, full=False):
        with open(filename, 'w') as bibfile:
            bibfile.write(self.get_html(full=full))

    def get_html(self, full=False):
        db = BibDatabase()
        db.entries = []
        for ref_type in self.references:
            for handle, citation in iteritems(self.references[ref_type]):
                description = citation.description
                description['ENTRYTYPE'] = citation.type
                description['ID'] = handle
                db.entries.append(description)
        writer = BibHtmlWriter()
        return writer.write(db, full=full)

    def references_by_type(self, ref_type):
        if ref_type in self.references:
            return self.references['ref_type']
        else:
            return []

    @staticmethod
    def set_pedantic(value):
        CiteMe.__pedantic = value

    @staticmethod
    def set_check_fields(value):
        CiteMe.__check_fields = value


class Citation(object):
    def __init__(self, handle, description, the_type):
        self.handle = handle
        self.description = description
        self.type = the_type

        # optional and required field
        # from https://en.wikipedia.org/wiki/BibTeX
        self._required = []
        self._optional = []
        self._general_options = ['url', 'doi']

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            CiteMe().add_reference(self)
            return f(*args, **kwargs)
        return wrapped_f

    def checkFields(self, pedantic):
        missing = []
        too_many = []
        if self._required:
            for field in self._required:
                if isinstance(field, tuple):
                    if not any(f in self.description for f in field):
                        missing.append(field)
                elif field not in self.description:
                    missing.append(field)

        if pedantic and self._optional:
            self._optional.extend(self._general_options)
            for field in self.description:
                found = False
                for option in self._optional:
                    if isinstance(option, tuple):
                        if field in option:
                            found = True
                    elif field == option:
                        found = True
                for option in self._required:
                    if isinstance(option, tuple):
                        if field in option:
                            found = True
                    elif field == option:
                        found = True
                if not found:
                    too_many.append(field)

        if missing or too_many:
            raise Exception("Fields for citation of type {0} is not correct:\n"
                            "required fields: {1}\n"
                            "optional fields: {2}\n\n"
                            "missing fields: {3}\n"
                            "non supported fields: {4}\n\n"
                            "found fields: {5}".format(
                                self.type, self._required, self._optional,
                                missing, too_many,
                                self.description.keys()
                            ))


class article(Citation):
    def __init__(self, handle, description):
        super(article, self).__init__(handle, description,'article')
        self._required = ['author', 'title', 'journal', 'year', 'volume']
        self._optional = ['number', 'pages', 'month', 'note', 'key']


class book(Citation):
    def __init__(self, handle, description):
        super(book, self).__init__(handle, description,'book')
        self._required = [('author', 'editor'), 'title', 'publisher', 'year']
        self._optional = [('volume', 'number'), 'series', 'address', 'edition', 'month', 'note', 'key']


class booklet(Citation):
    def __init__(self, handle, description):
        super(booklet, self).__init__(handle, description,'booklet')
        self._required = ['title']
        self._optional = ['author', 'howpublished', 'address', 'month', 'year', 'note', 'key']


class inbook(Citation):
    def __init__(self, handle, description):
        super(inbook, self).__init__(handle, description,'inbook')
        self._required = [('author', 'editor'), 'title', ('chapter', 'pages'), 'publisher', 'year']
        self._optional = [('volume', 'number'), 'series', 'type', 'address', 'edition', 'month', 'note', 'key']


class incollection(Citation):
    def __init__(self, handle, description):
        super(incollection, self).__init__(handle, description,'incollection')
        self._required = ['author', 'title', 'booktitle', 'publisher', 'year']
        self._optional = ['editor', ('volume', 'number'), 'series', 'type', 'chapter', 'pages', 'address', 'edition', 'month', 'note', 'key']


class inproceedings(Citation):
    def __init__(self, handle, description):
        super(inproceedings, self).__init__(handle, description,'inproceedings')
        self._required = ['author', 'title', 'booktitle', 'year']
        self._optional = ['editor', ('volume', 'number'), 'series', 'pages', 'address', 'month', 'organization', 'publisher', 'note', 'key']


# conference has the same fields as inproceedings
class conference(inproceedings):
    def __init__(self, handle, description):
        super(conference, self).__init__(handle, description, 'conference')


class manual(Citation):
    def __init__(self, handle, description):
        super(manual, self).__init__(handle, description,'manual')
        self._required = ['title']
        self._optional = ['author', 'organization', 'address', 'edition', 'month', 'year', 'note', 'key']


class mastersthesis(Citation):
    def __init__(self, handle, description):
        super(mastersthesis, self).__init__(handle, description,'mastersthesis')
        self._required = ['author', 'title', 'school', 'year']
        self._optional = ['type', 'address', 'month', 'note', 'key']


class bachelorthesis(Citation):
    def __init__(self, handle, description):
        super(bachelorthesis, self).__init__(handle, description,'bachelorthesis')
        self._required = ['author', 'title', 'school', 'year']
        self._optional = ['type', 'address', 'month', 'note', 'key']


class internship(Citation):
    def __init__(self, handle, description):
        super(internship, self).__init__(handle, description,'internship')
        self._required = ['author', 'title', 'school', 'year']
        self._optional = ['type', 'address', 'month', 'note', 'key']


class misc(Citation):
    def __init__(self, handle, description):
        super(misc, self).__init__(handle, description,'misc')
        self._optional = ['author', 'title', 'howpublished', 'month', 'year', 'note', 'key']


class phdthesis(Citation):
    def __init__(self, handle, description):
        super(phdthesis, self).__init__(handle, description,'phdthesis')
        self._required = ['author', 'title', 'school', 'year']
        self._optional = ['type', 'address', 'month', 'note', 'key']


class proceedings(Citation):
    def __init__(self, handle, description):
        super(proceedings, self).__init__(handle, description, 'proceedings')
        self._required = ['title', 'year']
        self._optional = ['editor', ('volume', 'number'), 'series', 'address', 'month', 'publisher', 'organization', 'note', 'key']


class techreport(Citation):
    def __init__(self, handle, description):
        super(techreport, self).__init__(handle, description, 'techreport')
        self._required = ['author', 'title', 'institution', 'year']
        self._optional = ['type', 'number', 'address', 'month', 'note', 'key']


class unpublished(Citation):
    def __init__(self, handle, description):
        super(unpublished, self).__init__(handle, description, 'unpublished')
        self._required = ['author', 'title', 'note']
        self._optional = ['month', 'year', 'key']


_CITATION_TYPES = {
    "article": article,
    "book": book,
    "booklet": booklet,
    "inbook": inbook,
    "incollection": incollection,
    "inproceedings": inproceedings,
    "conference": conference,
    "manual": manual,
    "mastersthesis": mastersthesis,
    "bachelorthesis": bachelorthesis,
    "internship": internship,
    "misc": misc,
    "phdthesis": phdthesis,
    "proceedings": proceedings,
    "techreport": techreport,
    "unpublished": unpublished,
}

_REFERENCE_CACHE = None
_REFERENCE_JSON_PATH = pathlib.Path(__file__).resolve().parent / "citations.json"


def _load_reference_db():
    global _REFERENCE_CACHE

    if _REFERENCE_CACHE is None:
        with open(_REFERENCE_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        _REFERENCE_CACHE = {entry["id"]: entry for entry in data}
        _REFERENCE_CACHE["__source__"] = str(_REFERENCE_JSON_PATH)

    return _REFERENCE_CACHE


def from_id(ref_id):
    """
    Usage:
        @citeme.from_id("Daniel_BA")
        def foo():
            ...
    """

    def _decorator(func):
        db = _load_reference_db()

        if ref_id not in db:
            raise KeyError(
                f"Reference ID '{ref_id}' not found in {db.get('__source__')}"
            )

        entry = dict(db[ref_id])  # copy
        ref_type = entry.pop("type")
        handle = entry.pop("id")

        if ref_type not in _CITATION_TYPES:
            raise ValueError(f"Unsupported citation type '{ref_type}'")

        citation_cls = _CITATION_TYPES[ref_type]
        citation = citation_cls(handle, entry)

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            CiteMe().add_reference(citation)
            return func(*args, **kwargs)

        return wrapped

    return _decorator

def set_pedantic(value):
    CiteMe.set_pedantic(value)


def set_check_fields(value):
    CiteMe.set_check_fields(value)


def print_references():
    CiteMe().print_references()


def write_to_bibtex(filename):
    CiteMe().write_to_bibtex(filename)


def write_to_html(filename, full=False):
    CiteMe().write_to_html(filename, full=full)


def get_html(full=False):
    return CiteMe().get_html(full=full)

try:
    from IPython.core.display import display, HTML
except ImportError:
    pass
else:
    def display_bibliography():
        display(HTML(get_html(full=False)))
