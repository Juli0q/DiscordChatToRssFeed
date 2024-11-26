from feedgen.ext.base import BaseEntryExtension
from lxml import etree

class ContentEncodedExtension(BaseEntryExtension):
    def __init__(self):
        self.content_encoded = None

    def extend_rss(self, rss_entry):
        if self.content_encoded:
            # Create the content:encoded element
            content_ns = 'http://purl.org/rss/1.0/modules/content/'
            content_encoded_element = etree.SubElement(
                rss_entry,
                f'{{{content_ns}}}encoded'
            )
            # Set the text as CDATA
            content_encoded_element.text = etree.CDATA(self.content_encoded)

    def extend_atom(self, atom_entry):
        pass  # Not needed for Atom feeds

    def set_content_encoded(self, content):
        self.content_encoded = content
