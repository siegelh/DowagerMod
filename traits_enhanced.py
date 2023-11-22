import tkinter as tk
from tkinter import ttk
from collections import OrderedDict
import xml.etree.ElementTree as ET
from xml.dom import minidom

def generate_output():
    # Get values from input fields
    user_name = name_entry.get()
    health_value = health_entry.get()
    happiness_value = happiness_entry.get()
    general_rate_modifier = general_rate_modifier_entry.get()
    domestic_general_rate_modifier = domestic_general_rate_modifier_entry.get()
    great_people_rate_modifier = great_people_rate_modifier_entry.get()
    promotion_experience_modifier = promotion_experience_modifier_entry.get()
    max_anarchy_length = max_anarchy_length_entry.get()
    world_wonder_modifier = world_wonder_modifier_entry.get()
    national_wonder_modifier = national_wonder_modifier_entry.get()
    team_wonder_modifier = team_wonder_modifier_entry.get()
    upkeep_modifier = upkeep_modifier_entry.get()
    city_income_change_gold = city_income_change_gold_entry.get()
    city_income_change_science = city_income_change_science_entry.get()
    city_income_change_culture = city_income_change_culture_entry.get()
    city_income_change_espionage = city_income_change_espionage_entry.get()
    city_income_modifier_gold = city_income_modifier_gold_entry.get()
    city_income_modifier_science = city_income_modifier_science_entry.get()
    city_income_modifier_culture = city_income_modifier_culture_entry.get()
    city_income_modifier_espionage = city_income_modifier_espionage_entry.get()
    extra_yield_threshold_food = extra_yield_threshold_food_entry.get()
    extra_yield_threshold_hammer = extra_yield_threshold_hammer_entry.get()
    extra_yield_threshold_gold = extra_yield_threshold_gold_entry.get()
    trade_yield_modifier_food = trade_yield_modifier_food_entry.get()
    trade_yield_modifier_gold = trade_yield_modifier_gold_entry.get()
    trade_yield_modifier_hammer = trade_yield_modifier_hammer_entry.get()
    promotions = collect_promotions()
    units = collect_unit_types()
    print(promotions)
    print(units)

    extra_yield_threshold =  generate_named_tuples([extra_yield_threshold_food, extra_yield_threshold_hammer, extra_yield_threshold_gold], "iExtraYieldThreshold")
    trade_yield_modifier = generate_named_tuples([trade_yield_modifier_food, trade_yield_modifier_hammer, trade_yield_modifier_gold], "iYield")
    city_income_changes = generate_named_tuples([city_income_change_gold, city_income_change_science, city_income_change_culture, city_income_change_espionage], "iCommerce")
    city_income_modifier = generate_named_tuples([city_income_modifier_gold, city_income_modifier_science, city_income_modifier_culture, city_income_modifier_espionage], "iCommerce")

    # If we enter any of these conditions, then it's an invalid trait and for now we just end without generating the file
    if user_name == "":
        result_label.config(text="Error: Please give your trait a name, imby.")
        return
    
    both_empty_or_non_empty = (not promotions) == (not units)
    if not both_empty_or_non_empty:
        result_label.config(text="Error: If using either Promotion or Unit, must include both.")
        return
    


# all required traits
    trait_data = OrderedDict({'Type': "TRAIT_" + user_name.upper(), 
                              'Description': "TXT_KEY_TRAIT_" + user_name.upper(), 
                              'ShortDescription': "TXT_KEY_TRAIT_" + user_name.upper() + "_SHORT", 
                              'iHealth': health_value, 
                              'iHappiness': happiness_value, 
                              'iMaxAnarchy': max_anarchy_length, 
                              'iUpkeepModifier': upkeep_modifier,
                              'iLevelExperienceModifier': promotion_experience_modifier,
                              'iGreatPeopleRateModifier': great_people_rate_modifier, 
                              'iGreatGeneralRateModifier': general_rate_modifier, 
                              'iDomesticGreatGeneralRateModifier': domestic_general_rate_modifier,
                              'iMaxGlobalBuildingProductionModifier': world_wonder_modifier, 
                              'iMaxTeamBuildingProductionModifier': team_wonder_modifier, 
                              'iMaxPlayerBuildingProductionModifier': national_wonder_modifier, 
                              'ExtraYieldThresholds': extra_yield_threshold, 
                              'TradeYieldModifiers': trade_yield_modifier, 
                              'CommerceChanges': city_income_changes, 
                              'CommerceModifiers': city_income_modifier, 
                              'FreePromotions': generate_promotions_output(promotions), 
                              'FreePromotionUnitCombats': generate_units_output(units)})
    
    builder = TraitInfoBuilder(trait_data)
    builder.build_xml()
    xml_output = builder.get_xml()

    # Write the output to the text file
    trait_file_name = "TRAIT_" + user_name.upper()
    file_path = f"traits/{trait_file_name}.txt"
    with open(file_path, "w") as file:
        file.write(xml_output)

    # Update the text in the result_label
    result_label.config(text=f"Output written to {file_path}")

    # Trait Class
class TraitInfoBuilder:
    def __init__(self, trait_data):
        if not isinstance(trait_data, OrderedDict):
            raise TypeError("trait_data must be an OrderedDict")
        self.trait_data = trait_data
        self.root = ET.Element("TraitInfo")

    def build_xml(self):
        for key, value in self.trait_data.items():
            if isinstance(value, (int, str)):
                self._add_simple_element(key, value)
            elif value == "":
                self._add_empty_element(key)
            elif isinstance(value, list):
                self._add_nested_elements(key, value)

    def _add_simple_element(self, element_name, value):
        element = ET.SubElement(self.root, element_name)
        element.text = str(value)

    def _add_empty_element(self, element_name):
        ET.SubElement(self.root, element_name)

    def _add_nested_elements(self, parent_element_name, children):
        parent_element = ET.SubElement(self.root, parent_element_name)
        for child in children:
            if isinstance(child[1], dict):
                child_element = ET.SubElement(parent_element, child[0])
                for sub_child_name, sub_child_value in child[1].items():
                    sub_child_element = ET.SubElement(child_element, sub_child_name)
                    sub_child_element.text = str(sub_child_value)
            else:
                child_element = ET.SubElement(parent_element, child[0])
                child_element.text = str(child[1])

    def get_xml(self):
        rough_string = ET.tostring(self.root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

# functions

def generate_named_tuples(input_list, name_variable):
    """
    This function takes a list and a name variable, and outputs a list of tuples
    where each tuple contains the name variable and an element from the list.
    """
    return [(name_variable, value) for value in input_list]

def generate_promotions_output(promotion_list):
    output = ["FreePromotions"]
    nested_list = []

    for promotion in promotion_list:
        nested_list.append(("FreePromotion", {"PromotionType": promotion, "bFreePromotion": "1"}))

    output.append(nested_list)
    return output[1]

def generate_units_output(unit_list):
    output = ["FreePromotionUnitCombats"]
    nested_list = []

    for unit in unit_list:
        nested_list.append(("FreePromotionUnitCombat", {"UnitCombatType": unit, "bFreePromotionUnitCombat": "1"}))

    output.append(nested_list)
    return output[1]

def extract_promotion_types(xml_path):
    # Parse the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extracting namespace from the root element
    ns = '{' + root.tag.split('}')[0].strip('{') + '}'

    # Find all 'PromotionInfo' elements, accounting for namespace
    promotion_infos = root.findall(f".//{ns}PromotionInfo")

    # Extract the 'Type' element text from each 'PromotionInfo'
    types = [promo.find(f'{ns}Type').text for promo in promotion_infos if promo.find(f'{ns}Type') is not None]

    return types

def collect_promotions():
    selected_promotions = promotion_listbox.curselection()
    selected_promotions_values = [promotion_listbox.get(i) for i in selected_promotions]
    return selected_promotions_values
    print(f"Selected Promotions: {', '.join(selected_promotions_values)}")

def collect_unit_types():
    selected_unit_types = unit_type_listbox.curselection()
    selected_unit_types_values = [unit_type_listbox.get(i) for i in selected_unit_types]
    return selected_unit_types_values
    print(f"Selected Unit Types: {', '.join(selected_unit_types_values)}")

def create_category_frame(frame, category_name, hover_text, row):
    category_label = tk.Label(frame, text=category_name, font=('Helvetica', 12, 'bold'))
    category_label.grid(row=row, column=0, pady=(10, 5), sticky='w')
    category_label.bind("<Enter>", lambda event, text=hover_text: show_tooltip(event, text))
    category_label.bind("<Leave>", hide_tooltip)
    return ttk.Separator(frame, orient="horizontal").grid(row=row + 1, column=0, sticky="ew", pady=(0, 10))

def show_tooltip(event, text):
    tooltip_label.config(text=text)
    tooltip_label.place(x=event.x_root + 10, y=event.y_root + 10)

def hide_tooltip(event):
    tooltip_label.place_forget()

# Create the main window
window = tk.Tk()
window.title("Civ 4 Trait Maker")

# Create and place input fields in different frames
frame1 = tk.Frame(window)
frame1.grid(row=0, padx=10, pady=10)

create_category_frame(frame1, "Trait Information", "Enter trait information here.", 0)

tk.Label(frame1, text="Trait Name:").grid(row=1, column=0, padx=10, pady=5)
name_entry = tk.Entry(frame1)
name_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame1, text="Health:").grid(row=2, column=0, padx=10, pady=5)
health_entry = tk.Entry(frame1)
health_entry.grid(row=2, column=1, padx=10, pady=5)
health_entry.insert(0, "0")

tk.Label(frame1, text="Happiness:").grid(row=3, column=0, padx=10, pady=5)
happiness_entry = tk.Entry(frame1)
happiness_entry.grid(row=3, column=1, padx=10, pady=5)
happiness_entry.insert(0, "0")

tk.Label(frame1, text="General Rate Modifier:").grid(row=4, column=0, padx=10, pady=5)
general_rate_modifier_entry = tk.Entry(frame1)
general_rate_modifier_entry.grid(row=4, column=1, padx=10, pady=5)
general_rate_modifier_entry.insert(0, "0")

tk.Label(frame1, text="Domestic General Rate Modifier:").grid(row=5, column=0, padx=10, pady=5)
domestic_general_rate_modifier_entry = tk.Entry(frame1)
domestic_general_rate_modifier_entry.grid(row=5, column=1, padx=10, pady=5)
domestic_general_rate_modifier_entry.insert(0, "0")

tk.Label(frame1, text="Great People Rate Modifier:").grid(row=6, column=0, padx=10, pady=5)
great_people_rate_modifier_entry = tk.Entry(frame1)
great_people_rate_modifier_entry.grid(row=6, column=1, padx=10, pady=5)
great_people_rate_modifier_entry.insert(0, "0")

tk.Label(frame1, text="Promotion Experience Modifier:").grid(row=7, column=0, padx=10, pady=5)
promotion_experience_modifier_entry = tk.Entry(frame1)
promotion_experience_modifier_entry.grid(row=7, column=1, padx=10, pady=5)
promotion_experience_modifier_entry.insert(0, "0")

tk.Label(frame1, text="Max Anarchy Length:").grid(row=8, column=0, padx=10, pady=5)
max_anarchy_length_entry = tk.Entry(frame1)
max_anarchy_length_entry.grid(row=8, column=1, padx=10, pady=5)
max_anarchy_length_entry.insert(-1, "-1")

tk.Label(frame1, text="World Wonder Production Modifier:").grid(row=9, column=0, padx=10, pady=5)
world_wonder_modifier_entry = tk.Entry(frame1)
world_wonder_modifier_entry.grid(row=9, column=1, padx=10, pady=5)
world_wonder_modifier_entry.insert(0, "0")

tk.Label(frame1, text="National Wonder Production Modifier:").grid(row=10, column=0, padx=10, pady=5)
national_wonder_modifier_entry = tk.Entry(frame1)
national_wonder_modifier_entry.grid(row=10, column=1, padx=10, pady=5)
national_wonder_modifier_entry.insert(0, "0")

tk.Label(frame1, text="Team Wonder Production Modifier:").grid(row=11, column=0, padx=10, pady=5)
team_wonder_modifier_entry = tk.Entry(frame1)
team_wonder_modifier_entry.grid(row=11, column=1, padx=10, pady=5)
team_wonder_modifier_entry.insert(0, "0")

tk.Label(frame1, text="Upkeep Modifier:").grid(row=12, column=0, padx=10, pady=5)
upkeep_modifier_entry = tk.Entry(frame1)
upkeep_modifier_entry.grid(row=12, column=1, padx=10, pady=5)
upkeep_modifier_entry.insert(0, "0")

# City Income Change
create_category_frame(frame1, "City Income Change (Extra raw values)", "City Income Change (Extra raw values)", 13)
tk.Label(frame1, text="Gold:").grid(row=14, column=0, padx=5, pady=5, sticky='e')
city_income_change_gold_entry = tk.Entry(frame1)
city_income_change_gold_entry.grid(row=14, column=1, padx=5, pady=5)
city_income_change_gold_entry.insert(0, "0")

tk.Label(frame1, text="Science:").grid(row=14, column=2, padx=5, pady=5, sticky='e')
city_income_change_science_entry = tk.Entry(frame1)
city_income_change_science_entry.grid(row=14, column=3, padx=5, pady=5)
city_income_change_science_entry.insert(0, "0")

tk.Label(frame1, text="Culture:").grid(row=14, column=4, padx=5, pady=5, sticky='e')
city_income_change_culture_entry = tk.Entry(frame1)
city_income_change_culture_entry.grid(row=14, column=5, padx=5, pady=5)
city_income_change_culture_entry.insert(0, "0")

tk.Label(frame1, text="Espionage:").grid(row=14, column=6, padx=5, pady=5, sticky='e')
city_income_change_espionage_entry = tk.Entry(frame1)
city_income_change_espionage_entry.grid(row=14, column=7, padx=5, pady=5)
city_income_change_espionage_entry.insert(0, "0")

# City Income Modifier
create_category_frame(frame1, "City Income Modifier (As a percent for each city)", "City Income Modifier (As a percent for each city)", 15)
tk.Label(frame1, text="Gold:").grid(row=16, column=0, padx=5, pady=5, sticky='e')
city_income_modifier_gold_entry = tk.Entry(frame1)
city_income_modifier_gold_entry.grid(row=16, column=1, padx=5, pady=5)
city_income_modifier_gold_entry.insert(0, "0")

tk.Label(frame1, text="Science:").grid(row=16, column=2, padx=5, pady=5, sticky='e')
city_income_modifier_science_entry = tk.Entry(frame1)
city_income_modifier_science_entry.grid(row=16, column=3, padx=5, pady=5)
city_income_modifier_science_entry.insert(0, "0")

tk.Label(frame1, text="Culture:").grid(row=16, column=4, padx=5, pady=5, sticky='e')
city_income_modifier_culture_entry = tk.Entry(frame1)
city_income_modifier_culture_entry.grid(row=16, column=5, padx=5, pady=5)
city_income_modifier_culture_entry.insert(0, "0")

tk.Label(frame1, text="Espionage:").grid(row=16, column=6, padx=5, pady=5, sticky='e')
city_income_modifier_espionage_entry = tk.Entry(frame1)
city_income_modifier_espionage_entry.grid(row=16, column=7, padx=5, pady=5)
city_income_modifier_espionage_entry.insert(0, "0")

# Extra Yield Thresholds
create_category_frame(frame1, "Extra Yield Thresholds", "Extra Yield Thresholds", 17)
tk.Label(frame1, text="Food:").grid(row=18, column=0, padx=5, pady=5, sticky='e')
extra_yield_threshold_food_entry = tk.Entry(frame1)
extra_yield_threshold_food_entry.grid(row=18, column=1, padx=5, pady=5)
extra_yield_threshold_food_entry.insert(0, "0")

tk.Label(frame1, text="Hammer:").grid(row=18, column=2, padx=5, pady=5, sticky='e')
extra_yield_threshold_hammer_entry = tk.Entry(frame1)
extra_yield_threshold_hammer_entry.grid(row=18, column=3, padx=5, pady=5)
extra_yield_threshold_hammer_entry.insert(0, "0")

tk.Label(frame1, text="Gold:").grid(row=18, column=4, padx=5, pady=5, sticky='e')
extra_yield_threshold_gold_entry = tk.Entry(frame1)
extra_yield_threshold_gold_entry.grid(row=18, column=5, padx=5, pady=5)
extra_yield_threshold_gold_entry.insert(0, "0")

# Trade Yield Modifier
create_category_frame(frame1, "Trade Yield Modifier", "Extra Yield Modifier", 19)
tk.Label(frame1, text="Food:").grid(row=20, column=0, padx=5, pady=5, sticky='e')
trade_yield_modifier_food_entry = tk.Entry(frame1)
trade_yield_modifier_food_entry.grid(row=20, column=1, padx=5, pady=5)
trade_yield_modifier_food_entry.insert(0, "0")

tk.Label(frame1, text="Hammer:").grid(row=20, column=2, padx=5, pady=5, sticky='e')
trade_yield_modifier_hammer_entry = tk.Entry(frame1)
trade_yield_modifier_hammer_entry.grid(row=20, column=3, padx=5, pady=5)
trade_yield_modifier_hammer_entry.insert(0, "0")

tk.Label(frame1, text="Gold:").grid(row=20, column=4, padx=5, pady=5, sticky='e')
trade_yield_modifier_gold_entry = tk.Entry(frame1)
trade_yield_modifier_gold_entry.grid(row=20, column=5, padx=5, pady=5)
trade_yield_modifier_gold_entry.insert(0, "0")

# Promotions
create_category_frame(frame1, "Promotions", "Select promotions and unit types here.", 21)

promotion_listbox = tk.Listbox(frame1, selectmode="multiple", height=15, width = 30, exportselection=False)
promotions = [
    "Accuracy", "Ace", "Ambush", "Barrage I", "Barrage II", "Barrage III", "Blitz", "Charge",
    "City Garrison I", "City Garrison II", "City Garrison III", "City Raider I", "City Raider II", "City Raider III",
    "Combat I", "Combat II", "Combat III", "Combat IV", "Combat V", "Combat VI", "Commando", "Cover",
    "Drill I", "Drill II", "Drill III", "Drill IV", "Flanking I", "Flanking II", "Formation",
    "Guerrilla I", "Guerrilla II", "Guerrilla III", "Interception I", "Interception II", "Leadership", "March",
    "Medic I", "Medic II", "Medic III", "Mobility", "Morale", "Navigation I", "Navigation II", "Pinch",
    "Range I", "Range II", "Sentry", "Shock", "Tactics", "Woodsman I", "Woodsman II", "Woodsman III"
]

promotions = extract_promotion_types(r"CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\XML\Units\CIV4PromotionInfos.xml")
#print(promotions)
for promotion in promotions:
    promotion_listbox.insert(tk.END, promotion)

unit_type_listbox = tk.Listbox(frame1, selectmode="multiple", height=15, width = 30, exportselection=False)
unit_types = [
    "UNITCOMBAT_RECON", "UNITCOMBAT_ARCHER", "UNITCOMBAT_MOUNTED", "UNITCOMBAT_MELEE", "UNITCOMBAT_SIEGE", "UNITCOMBAT_GUN", "UNITCOMBAT_ARMOR", "UNITCOMBAT_HELICOPTER", "UNITCOMBAT_NAVAL", "UNITCOMBAT_AIR"
]
for unit_type in unit_types:
    unit_type_listbox.insert(tk.END, unit_type)

promotion_listbox.grid(row=22, column=0, padx=10, pady=5)
unit_type_listbox.grid(row=22, column=1, padx=10, pady=5)

# Buttons to collect and print selected promotions and unit types
collect_promotions_button = tk.Button(frame1, text="Apply Promotions", command=collect_promotions)
collect_promotions_button.grid(row=23, column=0, pady=5)

collect_unit_types_button = tk.Button(frame1, text="Apply Unit Types", command=collect_unit_types)
collect_unit_types_button.grid(row=23, column=1, pady=5)

# Create a button to trigger the text generation
generate_button = tk.Button(window, text="Generate", command=generate_output)
generate_button.grid(row=24, column=0, pady=10)

# Create a label to display the formatted output
result_label = tk.Label(window, text="", font=('Helvetica', 12))
result_label.grid(row=26, column=0, pady=10)


# Tooltip label
tooltip_label = tk.Label(window, text="", bg="white", relief="solid", borderwidth=1)
tooltip_label.place_forget()

# Start the main loop
window.mainloop()