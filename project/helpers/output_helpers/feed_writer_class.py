from datetime import datetime, timezone
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from dateutil.parser import parse
import xml.dom.minidom
import os
import re


class FeedProcessorBase(ABC):
    @abstractmethod
    def process_all(self):
        pass

    @abstractmethod
    def process_title(self):
        pass

    @abstractmethod
    def process_published(self):
        pass

    @abstractmethod
    def process_updated(self):
        pass

    @abstractmethod
    def process_id(self):
        pass

    @abstractmethod
    def process_summary(self):
        pass

    @abstractmethod
    def process_enclosures(self):
        pass

    @abstractmethod
    def process_tags(self):
        pass

    @abstractmethod
    def process_link(self):
        pass

    @abstractmethod
    def process_author(self):
        pass

    @abstractmethod
    def get_xml(self):
        pass

    @abstractmethod
    def cache(self):
        pass


class FeedProcessorET(FeedProcessorBase):
    def __init__(self, entries, feed_data, output_file):
        self.entries = entries
        self.feed_data = feed_data
        self.output_file = output_file
        self.root = ET.Element("feed", xmlns="http://www.w3.org/2005/Atom")
        super().__init__()

    def process_all(self):
        """
        Process each entry and add to root.
        Required fields are title, author, id, updated, and link.
        """

        ET.SubElement(self.root, "title").text = self.feed_data["title"]
        ET.SubElement(self.root, "id").text = self.feed_data["id"]
        ET.SubElement(self.root, "updated").text = self.feed_data["updated"]

        handlers = {
            "title": self.process_title,
            "published": self.process_published,
            "updated": self.process_updated,
            "id": self.process_id,
            "summary": self.process_summary,
            "enclosures": self.process_enclosures,
            "tags": self.process_tags,
            "link": self.process_link,
            "author": self.process_author,
        }
        for entry in self.entries:
            self.entry_element = ET.SubElement(self.root, "entry")
            self.entry = entry

            for _, handler in handlers.items():
                handler()

        # self.clean_xml(self.root)

    # Required
    def process_title(self):
        ET.SubElement(self.entry_element, "title").text = self.entry.get(
            "title", "No title"
        )

    # Optional
    def process_published(self):
        published = self.entry.get("published", self.feed_data["updated"])
        if not self.is_atom_time(published):
            # Change time format to RFC-3339
            try:
                parsed_date = self.custom_timezone_parser(published)
                published = parsed_date.replace(
                    tzinfo=timezone.utc
                ).isoformat()

            except Exception as e:
                # Not necessary for entry to have published date
                print(
                    f"==== ERROR parsing published date: {e}, using current date"
                )
                published = datetime.now(timezone.utc).isoformat()

        ET.SubElement(self.entry_element, "published").text = published

    # Required
    def process_updated(self):
        updated = self.entry.get("updated", self.feed_data["updated"])
        if not self.is_atom_time(updated):
            # Change time format to RFC-3339
            try:
                parsed_date = self.custom_timezone_parser(updated)
                updated = parsed_date.replace(tzinfo=timezone.utc).isoformat()

            except Exception as e:
                print(
                    f"==== ERROR parsing updated date: {e}, using current date"
                )
                updated = datetime.now(timezone.utc).isoformat()

        ET.SubElement(self.entry_element, "updated").text = updated

    # Required
    def process_id(self):
        # Check if id exists and is a valid URI or URN
        if not self.entry.get("id"):
            id_value = "hardcoded-id:0000"
        else:
            id_value = self.entry.get("id", f"urn:tag:{self.entry['id']}")
            if not self.is_valid_atom_id(id_value):
                # Change id format to URN
                id_value = f"urn:tag:{self.entry['id']}"

        ET.SubElement(self.entry_element, "id").text = id_value

    # Optional
    def process_summary(self):
        if "summary" in self.entry:
            # Convert summary type to Atom type
            type_mapping = {
                "text/plain": "text",
                "text/html": "html",
                "application/xhtml+xml": "xhtml",
            }
            summary_type = type_mapping.get(
                self.entry.get("summary_detail", {}).get("type"), "text"
            )
            ET.SubElement(
                self.entry_element, "summary", type=summary_type
            ).text = self.entry["summary"]

    # Optional
    def process_enclosures(self):
        for enclosure in self.entry.get("enclosures", []):
            link_data = {
                "rel": "enclosure",
                "type": enclosure.get("type", "text/html"),
                "length": str(enclosure.get("length", "")),
                "href": enclosure["href"],
            }
            ET.SubElement(self.entry_element, "link", **link_data)

    # Optional
    def process_tags(self):
        for tag in self.entry.get("tags", []):
            attrib_data = {
                "scheme": tag.get("scheme", ""),
                "label": tag.get("label", ""),
                "term": tag.get("term", ""),
            }
            ET.SubElement(self.entry_element, "category", **attrib_data)

    # Required
    def process_link(self):
        # If link is not present, use feed id
        link_data = self.entry.get("link", self.feed_data["id"])
        link_attributes = {
            "rel": self.entry.get("rel", "alternate"),
            "type": self.entry.get("type", "text/html"),
            "href": link_data,
        }

        ET.SubElement(self.entry_element, "link", **link_attributes)

    # Required
    def process_author(self):
        author = ET.SubElement(self.entry_element, "author")
        ET.SubElement(author, "name").text = self.entry.get(
            "author", "Anonymous"
        )

    def is_valid_atom_id(self, atom_id):
        """
        Checks if the atom_id is a valid URI or URN.
        """
        uri_pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://.*$")
        urn_pattern = re.compile(r"^urn:[a-zA-Z0-9][a-zA-Z0-9-]{0,31}:.*$")

        return (
            uri_pattern.match(atom_id) is not None
            or urn_pattern.match(atom_id) is not None
        )

    def is_atom_time(self, date_str):
        """
        Checks if the date_str is a valid RFC-3339 date-time string.
        """
        try:
            datetime.fromisoformat(date_str)
            return True
        except ValueError:
            return False

    def custom_timezone_parser(self, time_string):
        """
        Attempts to parse the time_string with timezone info.
        """
        tzinfos = {"UT": 0}
        return parse(time_string, tzinfos=tzinfos)

    def clean_xml(self, element):
        """Remove attributes with value None."""
        for child in element:
            self.clean_xml(child)

        for key, value in element.attrib.items():
            if value is None:
                del element.attrib[key]

        self.root = element

    def prettify_xml(self):
        """
        Prettify XML using minidom.
        """
        encoding = self.feed_data.get("encoding", "utf-8")
        xml_string = ET.tostring(self.root, encoding=encoding, method="xml")
        dom = xml.dom.minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ", encoding=encoding).decode(encoding)

    def cache(self):
        new_tree = ET.ElementTree(self.root)
        new_root = new_tree.getroot()

        if os.path.exists(self.output_file):
            try:
                old_tree = ET.parse(self.output_file)
                old_root = old_tree.getroot()

                for entry in old_root.findall("entry"):
                    new_root.append(entry)

                self.root = new_root

            except ET.ParseError:
                print(
                    f"The file {self.output_file} could not be parsed and will be overwritten."
                )

    def get_xml(self):
        return self.prettify_xml()


class FeedProcessorSTR(FeedProcessorBase):
    def __init__(self, entries, feed_type, output_file):
        if feed_type == "rss":
            self.wrapper_tag = "item"
        else:
            self.wrapper_tag = "entry"

        self.entries = entries
        self.xml_strings = []
        self.output_file = output_file
        super().__init__()

    def process_all(self):
        handlers = {
            "title": self.process_title,
            "published": self.process_published,
            "updated": self.process_updated,
            "id": self.process_id,
            "summary": self.process_summary,
            "enclosures": self.process_enclosures,
            "tags": self.process_tags,
            "link": self.process_link,
            "author": self.process_author,
        }
        for entry in self.entries:
            self.xml_strings.append(f"<{self.wrapper_tag}>")
            self.entry = entry
            for _, handler in handlers.items():
                handler()
            self.xml_strings.append(f"</{self.wrapper_tag}>")

    def process_title(self):
        title = self.entry.get("title")
        if title:
            self.xml_strings.append(f"  <title>{title}</title>")

    def process_published(self):
        published = self.entry.get("published")
        if published:
            self.xml_strings.append(f"  <published>{published}</published>")

    def process_updated(self):
        updated = self.entry.get("updated")
        if updated:
            self.xml_strings.append(f"  <updated>{updated}</updated>")

    def process_id(self):
        id_value = self.entry.get("id")
        if id_value:
            self.xml_strings.append(f"  <id>{id_value}</id>")

    def process_summary(self):
        summary = self.entry.get("summary")
        if summary:
            self.xml_strings.append(f"  <summary>{summary}</summary>")

    def process_enclosures(self):
        enclosures = self.entry.get("enclosures", [])
        for enclosure in enclosures:
            href = enclosure.get("href")
            type_ = enclosure.get("type")
            self.xml_strings.append(
                f'  <enclosure href="{href}" type="{type_}"/>'
            )

    def process_tags(self):
        tags = self.entry.get("tags", [])
        for tag in tags:
            scheme = tag.get("scheme")
            label = tag.get("label")
            term = tag.get("term")
            self.xml_strings.append(
                f'  <category scheme="{scheme}" label="{label}" term="{term}"/>'
            )

    def process_link(self):
        link = self.entry.get("link")
        if link:
            self.xml_strings.append(
                f'  <link rel="alternate" type="text/html" href="{link}"/>'
            )

    def process_author(self):
        author = self.entry.get("author")
        if author:
            self.xml_strings.append(
                f"  <author>\n    <name>{author}</name>\n  </author>"
            )

    def get_xml(self):
        return "\n".join(self.xml_strings) + "\n\n"

    def cache(self):
        if os.path.exists(self.output_file):
            with open(self.output_file, "r", encoding="utf-8") as f:
                existing_content = f.read()

                self.xml_strings.extend(existing_content.splitlines())
