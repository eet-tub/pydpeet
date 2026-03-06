"""
TODO Code taken from : https://github.com/citation-file-format/citeme/tree/master
"""

import logging

from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

try:
    import BeautifulSoup
except ImportError:
    bs = None
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        bs4 = None
    else:
        bs4 = BeautifulSoup
else:
    bs = BeautifulSoup.BeautifulSoup

logger = logging.getLogger(__name__)


class BibHtmlWriter(BibTexWriter):
    def __init__(self):
        super().__init__()
        self.display_order = [
            "author",
            "title",
            "booktitle",
            "journal",
            "editor",
            "volume",
            "number",
            "series",
            "publisher",
            "year",
            "pages",
            "url",
            "doi",
        ]
        self.html_template = """
<html>
<head>
    <link rel="stylesheet" href="css/bibstyle.css" />
</head>
</html>
<body>
    {0}
</body>
"""

    def write(self, bib_database, full=False):
        """
        Converts a bibliographic database to a html-formatted string.
        :param bib_database: bibliographic database to be converted to a BibTeX string
        :type bib_database: BibDatabase
        :return: BibTeX-formatted string
        :rtype: str or unicode
        """
        html = super().write(bib_database)
        if full:
            html = self.html_template.format(html)

        soup = None
        if bs4:
            soup = bs4(html, "html5lib")
        if bs:
            soup = bs(html)

        if soup:
            return soup.prettify()
        else:
            return html

    def _entries_to_bibtex(self, bib_database):
        html = '<fieldset class="the_bibliography">\n<legend>The Bibliography</legend>'
        if self.order_entries_by:
            # TODO: allow sort field does not exist for entry
            entries = sorted(bib_database.entries, key=lambda x: BibDatabase.entry_sort_key(x, self.order_entries_by))
        else:
            entries = bib_database.entries

        if self.align_values:
            # determine maximum field width to be used
            widths = [max(map(len, entry.keys())) for entry in entries]
            self._max_field_width = max(widths)

        html += '<ol class="references">'
        for entry in entries:
            html += "<li>" + self._entry_to_bibtex(entry) + "</li>"

        html += "</ol>"
        html += "</fieldset>"
        return html

    def _entry_to_bibtex(self, entry):
        html = ""
        # Write BibTeX key
        html += '<cite id="' + entry["ID"] + '" class="bib-entry">'

        # create display_order of fields for this entry
        # only those keys which are both in self.display_order and in entry.keys
        display_order = [i for i in self.display_order if i in entry]

        # Write field = value lines
        for field in [i for i in display_order if i not in ["ENTRYTYPE", "ID"]]:
            try:
                if field == "url":
                    html += (
                        "\n<span class='bib-entry-field bib-entry-url bib-entry-"
                        + "{0:<{1}}".format(field, self._max_field_width)
                        + f"'><a href='{entry[field]}'>{entry[field]}<a></span>"
                    )
                else:
                    html += (
                        "\n<span class='bib-entry-field bib-entry-"
                        + "{0:<{1}}".format(field, self._max_field_width)
                        + "'>"
                        + entry[field]
                        + "</span>"
                    )
            except TypeError as t:
                raise TypeError("The field {} in entry {} must be a string".format(field, entry["ID"])) from t
        html += "\n</cite>\n" + self.entry_separator

        return html

    def _comments_to_bibtex(self, bib_database):
        return "".join(
            [f'<div class="bib-comment">{comment}</div>\n{self.entry_separator}' for comment in bib_database.comments]
        )

    def _preambles_to_bibtex(self, bib_database):
        return "".join([f"{preamble}\n{self.entry_separator}" for preamble in bib_database.preambles])
