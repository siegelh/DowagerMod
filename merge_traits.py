import os
import xml.etree.ElementTree as ET

def merge_xml_files(directory, existing_file_path):
    # Load and parse the existing XML file
    tree = ET.parse(existing_file_path)
    root = tree.getroot()

    # Iterate over each XML file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            file_path = os.path.join(directory, filename)

            # Parse the new XML file
            new_tree = ET.parse(file_path)
            new_root = new_tree.getroot()

            for new_element in new_root:
                # Check if this entry exists in the existing file
                existing_element = root.find(new_element.tag)
                if existing_element is not None:
                    # Replace the existing entry
                    root.remove(existing_element)
                root.append(new_element)

    # Save the updated XML content back to the existing file
    tree.write(existing_file_path)

# Example usage
merge_xml_files('traits', r"C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Warlords\Assets\XML\Civilizations\CIV4TraitInfos.xml")
