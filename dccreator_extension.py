from feedgen.ext.base import BaseEntryExtension
from lxml import etree

class DCCreatorEntryExtension(BaseEntryExtension):
    def __init__(self):
        self.creator = None

    def extend_rss(self, rss_entry):
        if self.creator:
            # Define the 'dc' namespace
            dc_ns = 'http://purl.org/dc/elements/1.1/'
            # Add the 'dc:creator' element with the appropriate namespace
            dc_creator_element = etree.SubElement(
                rss_entry,
                f'{{{dc_ns}}}creator'
            )
            dc_creator_element.text = self.creator

    def extend_atom(self, atom_entry):
        pass  # Not needed for Atom feeds

    def set_creator(self, creator):
        self.creator = creator
