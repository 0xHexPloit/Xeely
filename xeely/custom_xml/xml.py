from typing import List
from typing import Optional
from xml.dom.minidom import Document
from xml.dom.pulldom import parseString
from xml.sax import make_parser
from xml.sax.handler import feature_external_ges

from xeely.custom_xml.doctype import XMLDoctype
from xeely.custom_xml.errors import NotTextElement
from xeely.custom_xml.errors import XMLElementNotFound
from xeely.custom_xml.text_element import XMLTextElement


def get_custom_xml_tag():
    return '<?xml version="1.0" encoding="UTF-8" ?>'


class XML:
    _doctype: Optional[XMLDoctype]
    _root_node: Document

    def __init__(self, root_node: Document):
        self._root_node = root_node
        self._doctype = None

    @staticmethod
    def _check_if_node_is_of_type_text_node(node: Document) -> bool:
        children: List[Document] = node.childNodes
        not_text_element_children = [
            child for child in children if child.nodeType != child.TEXT_NODE
        ]

        return len(not_text_element_children) == 0

    @staticmethod
    def _get_text_node_value(node: Document) -> str:
        output = ""
        children: List[Document] = node.childNodes

        for child in children:
            output += child.nodeValue

        return output

    def _get_text_element(self, element_name, *, nth: int = 0) -> Document:
        elements: List[Document] = self._root_node.getElementsByTagName(element_name)
        elements_size = len(elements)

        if nth >= elements_size:
            raise XMLElementNotFound()

        element = elements[nth]

        if not XML._check_if_node_is_of_type_text_node(element):
            raise NotTextElement()

        return element

    def get_text_element_value(self, element_name: str, *, nth: int = 0) -> str:
        text_element = self._get_text_element(element_name, nth=nth)
        return XML._get_text_node_value(text_element)

    def change_text_element_value(self, element_name: str, new_value: str, *, nth: int = 0):
        text_element = self._get_text_element(element_name, nth=nth)

        new_text_node = self._root_node.createTextNode(new_value)

        text_element.childNodes = [new_text_node]

    def _get_text_elements_value_rec(self, current_node: Document, arr: List[XMLTextElement]):
        if XML._check_if_node_is_of_type_text_node(current_node):
            arr.append(
                XMLTextElement(current_node.nodeName, XML._get_text_node_value(current_node))
            )

        children: List[Document] = current_node.childNodes

        for child in children:
            self._get_text_elements_value_rec(child, arr)

    def get_text_elements(self) -> List[XMLTextElement]:
        output: List[XMLTextElement] = []
        self._get_text_elements_value_rec(self._root_node, output)
        return [item for item in output if len(item.get_value().strip("\n ")) != 0]

    def to_xml(self) -> str:
        output = f"{str(self._root_node.toxml()).replace('amp;', '')}"
        output_lines = output.split("\n")

        # Ensuring that first line contains only <?xml ... ?> tag
        if len([character for character in output_lines[0] if character == ">"]) > 1:
            pos = output_lines[0].find(">")
            remaining_content = output_lines[0][pos + 1 :]
            output_lines[0] = output_lines[0][: pos + 1]
            output_lines.insert(1, remaining_content)

        # Replacing XML tag with custom one
        output_lines[0] = get_custom_xml_tag()

        if self._doctype is not None:
            output_lines.insert(1, self._doctype.to_xml())

        output = "\n".join(output_lines)

        return output

    def get_root_node_name(self) -> str:
        node: Document = self._root_node.childNodes[0]
        return node.nodeName

    def set_doctype(self, doctype: XMLDoctype):
        self._doctype = doctype

    @staticmethod
    def parse_string(xml: str, allows_external_entities: bool = False) -> Optional["XML"]:
        # Parsing XML content
        parser = make_parser()
        parser.setFeature(feature_external_ges, allows_external_entities)
        xml_doc = parseString(xml, parser)
        xml_obj: Optional["XML"] = None

        for event, node in xml_doc:
            xml_doc.expandNode(node)
            xml_obj = XML(node)
            break

        return xml_obj
