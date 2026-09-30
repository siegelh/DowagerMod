from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from tools.remaster_visual_phase_3_6 import normalize_plot_routes


class PlotMergeTests(unittest.TestCase):
    def test_custom_routes_exclusive_and_nodes_ordered_without_art_changes(self):
        source = """<LSystemInfos>
<LNode Name="Node_12x12"><Width>12</Width></LNode>
<LProduction From="PLOT_ROOT"><Attribute Class="Improvement">NO_IMPROVEMENT,IMPROVEMENT_ALL,!IMPROVEMENT_MINE</Attribute><To Name="Node_12x12"/></LProduction>
<LNode Name="Node_Dowager_Test"><ArtRef Name="goal:IMPROVEMENT_TEST"><Scale>0.50</Scale></ArtRef></LNode>
<LProduction From="PLOT_ROOT" Name="Dedicated"><Attribute Class="Improvement">IMPROVEMENT_TEST</Attribute><To Name="Node_Dowager_Test"/></LProduction>
<LProduction From="PLOT_ROOT" Name="Fallback"><Attribute Class="Improvement">IMPROVEMENT_CAMP</Attribute><To Name="Node_12x12"/></LProduction>
</LSystemInfos>"""
        types = ["IMPROVEMENT_FARM", "IMPROVEMENT_MINE", "IMPROVEMENT_TEST", "IMPROVEMENT_CAMP"]
        result = normalize_plot_routes(source, types)
        root = ET.fromstring(result)
        self.assertEqual([n.tag for n in root][:2], ["LNode", "LNode"])
        self.assertEqual(root.find(".//Scale").text, "0.50")
        selectors = [n.text for n in root.findall("./LProduction/Attribute")]
        self.assertEqual(selectors, ["NO_IMPROVEMENT,IMPROVEMENT_FARM", "IMPROVEMENT_TEST", "IMPROVEMENT_CAMP"])
        self.assertEqual(normalize_plot_routes(result, types), result)
        original = ET.fromstring(source)
        for name in ("Dedicated", "Fallback"):
            self.assertEqual(
                ET.tostring(root.find(f"./LProduction[@Name='{name}']")),
                ET.tostring(original.find(f"./LProduction[@Name='{name}']")),
            )

    def test_long_positive_roster_is_partitioned_without_loss_or_duplicates(self):
        source = '<LSystemInfos><LProduction From="PLOT_ROOT"><Attribute Class="Improvement">IMPROVEMENT_ALL</Attribute><To Name="Node_12x12"/></LProduction></LSystemInfos>'
        types = ["IMPROVEMENT_EXAMPLE_%02d" % i for i in range(40)]
        result = ET.fromstring(normalize_plot_routes(source, types))
        selectors = [n.text for n in result.findall("./LProduction/Attribute")]
        self.assertTrue(all(len(value) <= 182 for value in selectors))
        self.assertEqual([token for value in selectors for token in value.split(",")], types)

    def test_unknown_broad_route_conditions_fail_explicitly(self):
        source = '<LSystemInfos><LProduction From="PLOT_ROOT"><Attribute Class="Improvement">IMPROVEMENT_ALL</Attribute><Attribute Class="Bonus">NO_BONUS</Attribute><To Name="Node_12x12"/></LProduction></LSystemInfos>'
        with self.assertRaisesRegex(ValueError, "conditions"):
            normalize_plot_routes(source, ["IMPROVEMENT_FARM"])


if __name__ == "__main__":
    unittest.main()
