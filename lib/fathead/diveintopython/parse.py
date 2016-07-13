#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from bs4 import BeautifulSoup
from tidylib import tidy_document

URL_ROOT = 'http://www.diveintopython3.net/'
DOWNLOADED_HTML_PATH = 'download/diveintopython3-master'

class PythonData(object):
    """
    Object responsible for loading raw HTML data from Python docs:
    """
    def __init__(self, file):
        """
        Initialize PythonData object. Load data from HTML.
        """
        self.HTML = ""
        self.FILE = file
        self.load_data()

    def load_data(self):
        """
        Open the HTML file and load it into the object.

        """
        with codecs.open(self.FILE, 'r', encoding='utf-8', errors='ignore') as data_file:
            # DiveIntoPython3 html needs to be tidyed first,
            # otherwise BS4 sees all the docs as one <p>
            document, errors = tidy_document(data_file.read())
            self.HTML = document

    def get_raw_data(self):
        """
        Returns: The raw HTML that was loaded.

        """
        return self.HTML

    def get_file(self):
        """
        Returns: The file path of the file being used.

        """
        return self.FILE


class PythonDataParser(object):
    """
    Object responsible for parsing the raw HTML that contains Python data
    """
    def __init__(self, data_object):
        """
        Given raw data, get the relevant sections
        Args:
            raw_data: HTML data
        """
        self.file_being_used = data_object.get_file()
        self.file_name = self.file_being_used.split('/').pop()
        self.main_sections = []
        self.sub_sections = []
        self.soup = BeautifulSoup(data_object.get_raw_data(), 'html.parser')

    def parse_for_data(self):
        """
        Main loop for parsing main subjects and their sub sections
        """
        for header in self.soup.find_all('h2'):
            section = self.parse_section(header)
            self.main_sections.append(section)

        for header in self.soup.find_all('h3'):
            section = self.parse_section(header)
            section['example'] = self.get_example(header)
            section['abstract'] = '{}<br><pre><code>{}</code></pre>'.format(section['paragraph'], section['example'])
            self.sub_sections.append(section)

        self.parsed_data = self.main_sections + self.sub_sections

    def get_data(self):
        """
        Get the parsed data.
        Returns:
            self.parsed_data: Dict containing necessary data elements
        """
        return self.parsed_data

    def get_example(self, soup):
        """
        Gets the next code example after soup tag object
        Args:
            Soup tag object
        Returns:
            Text inside <pre> tag
        """
        return soup.findNext('pre').get_text().replace('\n', '\\n')

    def get_url(self, soup):
        """
        Parses url to the content
        Args:
            Soup tag object
        Returns:
            Url with anchor
        """

        anchor = soup.get('id')

        if anchor:
            parsed_url = '{}#{}'.format(os.path.join(URL_ROOT, self.file_name), anchor)
        else:
            parsed_url = os.path.join(URL_ROOT, file_name)

        return parsed_url

    def parse_section(self, soup):
        """
        Parses main and sub sections in soup object.

        Args:
            soup: Soup tag object
        Returns:
            Section data, containing title, first paragraph and url to content.
        """
        first_paragraph = self.clean_formatting(soup.findNext('p').get_text())

        return {
            'title': self.clean_formatting(soup.get_text()),
            'paragraph': first_paragraph,
            'anchor': self.get_url(soup),
            'url': os.path.join(URL_ROOT, self.file_name)
        }

    def clean_formatting(self, text):
        """
        Fixes up some weird double spacing and newlines.
        Args:
            text: Piece of text to be fixed.

        Returns:
            Given text without double spacing and new lines.
        """
        text = text.replace('  ', ' ').replace('\n', ' ').replace('\\n', r'\\n')
        return text.strip()


class PythonDataOutput(object):
    """
    Object responsible for outputting data into the output.txt file
    """
    def __init__(self, data):
        self.data = data

    def create_file(self):
        """
        Iterate through the data and create the needed output.txt file,
        appending to file as necessary.
        """
        with open('output.txt', 'w') as output_file:
            for data_element in self.data:
                title = data_element.get('title')
                abstract = data_element.get('abstract')
                first_paragraph = data_element.get('first_paragraph')

                if abstract is None:
                    abstract = first_paragraph

                if abstract is None:
                    continue

                anchor = data_element.get('anchor')
                url = data_element.get('url')

                list_of_data = [
                    title,      # title
                    'A',        # type is article
                    '',         # no redirect data
                    '',         # ignore
                    '',         # no categories
                    '',         # ignore
                    '',         # no related topics
                    '',         # ignore
                    url,        # add an external link back to Django home
                    '',         # no disambiguation
                    '',         # images
                    abstract,   # abstract
                    anchor      # anchor to specific section
                ]

                try:
                    output_file.write('{}\n'.format('\t'.join(list_of_data)))
                except Exception as e:
                    import pdb; pdb.set_trace()



if __name__ == "__main__":
    # Sections which we want to include
    to_be_parsed = [
        'native-datatypes.html',
    ]
    for filename in to_be_parsed:
        file_path = os.path.join(DOWNLOADED_HTML_PATH, filename)
        data = PythonData(file_path)
        parser = PythonDataParser(data)
        parser.parse_for_data()
        output = PythonDataOutput(parser.get_data())
        output.create_file()
