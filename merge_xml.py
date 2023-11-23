from xml.etree import ElementTree as ET
import io
import os

def update_or_merge_xml_directory(master_file_path, additional_file_directory):
    def remove_namespaces(tree):
        for el in tree.iter():
            if '}' in el.tag:
                el.tag = el.tag.split('}', 1)[1]  # Removes namespace
            for at in list(el.attrib.keys()):  # Removes namespace from attributes
                if '}' in at:
                    new_at = at.split('}', 1)[1]
                    el.attrib[new_at] = el.attrib[at]
                    del el.attrib[at]

    master_tree = ET.parse(master_file_path)
    remove_namespaces(master_tree)
    master_root = master_tree.getroot()

    for file in os.listdir(additional_file_directory):
        if file.startswith("TXT_KEY_TRAIT_") and "SHORT" not in file:
            additional_file_path = os.path.join(additional_file_directory, file)

            additional_tree = ET.parse(additional_file_path)
            remove_namespaces(additional_tree)
            additional_root = additional_tree.getroot()

            master_tags = {child.find('Tag').text: child for child in master_root}

            for child in additional_root:
                tag = child.find('Tag').text
                if tag in master_tags:
                    master_root.remove(master_tags[tag])
                master_root.append(child)

    master_tree.write(master_file_path, encoding='ISO-8859-1', xml_declaration=True)



original_xml_path = r"C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Warlords\Assets\XML\Text\CIV4GameText_Warlords_Objects.xml"
new_text_xml_path = r"C:\DowagerMod\traits"
output_xml_path = r"C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Warlords\Assets\XML\Text\CIV4GameText_Warlords_Objects.xml"

update_or_merge_xml_directory(original_xml_path, new_text_xml_path)


# Short Descriptions Updating
def update_or_merge_xml_directory_short(master_file_path, additional_file_directory):
    def remove_namespaces(tree):
        for el in tree.iter():
            if '}' in el.tag:
                el.tag = el.tag.split('}', 1)[1]  # Removes namespace
            for at in list(el.attrib.keys()):  # Removes namespace from attributes
                if '}' in at:
                    new_at = at.split('}', 1)[1]
                    el.attrib[new_at] = el.attrib[at]
                    del el.attrib[at]

    master_tree = ET.parse(master_file_path)
    remove_namespaces(master_tree)
    master_root = master_tree.getroot()

    for file in os.listdir(additional_file_directory):
        if file.startswith("TXT_KEY_TRAIT_") and "SHORT" in file:
            additional_file_path = os.path.join(additional_file_directory, file)

            additional_tree = ET.parse(additional_file_path)
            remove_namespaces(additional_tree)
            additional_root = additional_tree.getroot()

            master_tags = {child.find('Tag').text: child for child in master_root}

            for child in additional_root:
                tag = child.find('Tag').text
                if tag in master_tags:
                    master_root.remove(master_tags[tag])
                master_root.append(child)

    master_tree.write(master_file_path, encoding='ISO-8859-1', xml_declaration=True)

original_xml_path_short = r"C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Warlords\Assets\XML\Text\CIV4GameText_Warlords.xml"
new_text_xml_path = r"C:\DowagerMod\traits"
output_xml_path_short = r"C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Warlords\Assets\XML\Text\CIV4GameText_Warlords.xml"

update_or_merge_xml_directory_short(original_xml_path_short, new_text_xml_path)