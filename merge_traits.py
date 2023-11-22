import os
import xml.etree.ElementTree as ET
import codecs

comments = [
    "<!-- edited with XMLSPY v2004 rel. 2 U (http://www.xmlspy.com) by Alex Mantzaris (Firaxis Games) -->",
    "<!-- Sid Meier's Civilization 4 -->",
    "<!-- Copyright Firaxis Games 2005 -->",
    "<!-- -->",
    "<!-- Leader Trait Infos -->"
]

def get_distinct_trait_types(original_xml_path):
    print(f"Reading distinct trait types from {original_xml_path}")
    distinct_types = set()

    with open(original_xml_path, 'r', encoding='utf-8') as file:
        inside_trait_info = False
        for line in file:
            if '<Type>' in line and '</Type>' in line:
                type_value = line.strip().replace('<Type>', '').replace('</Type>', '')
                distinct_types.add(type_value)
                print(f"Found distinct type: {type_value}")

    print(f"Total distinct types found: {len(distinct_types)}")
    return distinct_types

def serialize_without_namespace(element):
    print(f"Serializing element: {element.tag}")
    tag = element.tag
    if tag.startswith('{') and 'ns0:' in tag:
        tag = tag.split('}', 1)[1]
    new_element = ET.Element(tag, element.attrib)
    new_element.text = element.text
    new_element.tail = element.tail
    for child in element:
        new_element.append(serialize_without_namespace(child))
    return new_element

def update_or_append_traits_preserving_namespace(original_xml_path, directory_path, comments):
    print(f"Updating or appending traits for {original_xml_path} in {directory_path}")
    distinct_types = get_distinct_trait_types(original_xml_path)

    with open(original_xml_path, 'rb') as file:
        xml_content = file.read()
        if xml_content.startswith(codecs.BOM_UTF8):
            xml_content = xml_content[len(codecs.BOM_UTF8):]
        original_xml_content = xml_content.decode('utf-8')

    ET.register_namespace('', "x-schema:CIV4CivilizationsSchema.xml")
    root = ET.fromstring(original_xml_content)
    trait_infos = root.find('.//{x-schema:CIV4CivilizationsSchema.xml}TraitInfos')

    if trait_infos is None:
        trait_infos = ET.SubElement(root, 'TraitInfos')
        print("Created new TraitInfos element")

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.xml') and filename.startswith('TRAIT_'):
            print(f"Processing file: {filename}")
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                file_content = file_content.replace('<?xml version="1.0"?>', '').strip()
                new_trait_element = ET.fromstring(file_content)
                new_trait_type_element = new_trait_element.find('./Type')

                if new_trait_type_element is not None:
                    new_trait_type = new_trait_type_element.text
                    print(f"Trait type in the file: {new_trait_type}")

                    existing_trait = None
                    namespaces = {'ns': "x-schema:CIV4CivilizationsSchema.xml"}
                    
                    for trait_info in trait_infos.findall('.//ns:TraitInfo', namespaces):
                        type_element = trait_info.find('ns:Type', namespaces)
                        if type_element is not None and type_element.text == new_trait_type:
                            existing_trait = trait_info
                            print(f"Found existing trait type: {new_trait_type}")
                            break

                    if existing_trait is not None:
                        print(f"Replacing existing trait type: {new_trait_type}")
                        trait_infos.remove(existing_trait)
                    else:
                        print(f"Appending new trait type: {new_trait_type}")

                    trait_infos.append(new_trait_element)
                else:
                    print("No <Type> element found in the new trait element")

    xml_str = '<?xml version="1.0"?>\n' + '\n'.join(comments) + '\n' + ET.tostring(root, encoding='unicode', method='xml')
    print("Serialization completed")


    # Write the updated content back to the original file
    with open(original_xml_path, 'w', encoding='utf-8') as file:
        file.write(xml_str)
        print("Wrote updated content back to the original file")

    return xml_str


# Example usage
update_or_append_traits_preserving_namespace(r"C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Warlords\Assets\XML\Civilizations\CIV4TraitInfos_simple.xml",r'C:\DowagerMod\traits', comments)
