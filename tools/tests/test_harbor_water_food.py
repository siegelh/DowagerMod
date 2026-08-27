from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DLL = ROOT / "third_party" / "beyond-the-sword-sdk" / "CvGameCoreDLL"
ASSETS = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
)


class HarborWaterFoodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.city = (DLL / "CvCity.cpp").read_text(encoding="utf-8")
        cls.city_header = (DLL / "CvCity.h").read_text(encoding="utf-8")
        cls.city_ai = (DLL / "CvCityAI.cpp").read_text(encoding="utf-8")
        cls.text_mgr = (DLL / "CvGameTextMgr.cpp").read_text(encoding="utf-8")
        cls.defines = ET.parse(ASSETS / "XML" / "GlobalDefines.xml")
        cls.text = ET.parse(
            ASSETS / "XML" / "Text" / "ZZZ_CIV4GameText_HarborWaterFood.xml"
        )
        cls.buildings = (
            ASSETS / "XML" / "Buildings" / "CIV4BuildingInfos.xml"
        ).read_text(encoding="utf-8")
        cls.building_classes = (
            ASSETS / "XML" / "Buildings" / "CIV4BuildingClassInfos.xml"
        ).read_text(encoding="utf-8")
        cls.civilizations = (
            ASSETS / "XML" / "Civilizations" / "CIV4CivilizationInfos.xml"
        ).read_text(encoding="utf-8")

    def test_formula_uses_divisor_two_and_cap_eight(self) -> None:
        values = {}
        for node in self.defines.getroot():
            children = {
                child.tag.rsplit("}", 1)[-1]: child.text for child in node
            }
            values[children.get("DefineName")] = children.get("iDefineIntVal")
        self.assertEqual(values["HARBOR_WATER_FOOD_DIVISOR"], "2")
        self.assertEqual(values["HARBOR_WATER_FOOD_CAP"], "8")
        for water, expected in ((0, 0), (1, 0), (2, 1), (3, 1), (14, 7), (15, 7), (16, 8), (20, 8)):
            with self.subTest(water=water):
                self.assertEqual(min(8, water // 2), expected)

    def test_full_bfc_water_counter_has_requested_scope(self) -> None:
        helper = self._function(self.city, "int CvCity::countNumWaterPlotsInBFC")
        self.assertIn("NUM_CITY_PLOTS", helper)
        self.assertIn("iI == CITY_HOME_PLOT", helper)
        self.assertIn("plotCity(getX_INLINE(), getY_INLINE(), iI)", helper)
        self.assertIn("pLoopPlot->isWater()", helper)
        self.assertNotIn("getWorkingCity()", helper)
        self.assertNotIn("isWorkingPlot", helper)
        self.assertNotIn("getOwner", helper)

    def test_harbor_resolution_is_class_based(self) -> None:
        resolver = self._function(self.city, "BuildingTypes CvCity::getActiveHarborBuilding")
        self.assertIn('"BUILDINGCLASS_HARBOR"', resolver)
        self.assertIn("getCivilizationBuildings(eHarborClass)", resolver)
        self.assertIn("getNumActiveBuilding(eHarbor)", resolver)
        self.assertNotIn("BUILDING_HARBOR", resolver)
        self.assertNotIn("BUILDING_CARTHAGE_COTHON", resolver)
        self.assertNotIn("BUILDING_PETER_ADMIRALTY", resolver)

    def test_all_live_harbor_replacements_use_the_shared_class(self) -> None:
        for building in (
            "BUILDING_HARBOR",
            "BUILDING_CARTHAGE_COTHON",
            "BUILDING_PETER_ADMIRALTY",
        ):
            with self.subTest(building=building):
                self.assertIn(f"<Type>{building}</Type>", self.buildings)

        self.assertRegex(
            self.building_classes,
            r"<Type>BUILDINGCLASS_HARBOR</Type>[\s\S]*?"
            r"<DefaultBuilding>BUILDING_HARBOR</DefaultBuilding>",
        )
        for replacement in (
            "BUILDING_CARTHAGE_COTHON",
            "BUILDING_PETER_ADMIRALTY",
        ):
            with self.subTest(replacement=replacement):
                self.assertRegex(
                    self.civilizations,
                    r"<BuildingClassType>BUILDINGCLASS_HARBOR</BuildingClassType>"
                    r"\s*<BuildingType>" + re.escape(replacement) + r"</BuildingType>",
                )

    def test_derived_food_is_cached_but_not_serialized(self) -> None:
        self.assertIn("int m_iHarborWaterFood;", self.city_header)
        getter = self._function(self.city, "int CvCity::getBaseYieldRate")
        self.assertIn("getHarborWaterFood()", getter)
        setter = self._function(self.city, "void CvCity::setBaseYieldRate")
        self.assertIn("iNewValue - iDerivedValue", setter)
        read = self._function(self.city, "void CvCity::read")
        write = self._function(self.city, "void CvCity::write")
        self.assertIn("updateHarborWaterFood(false)", read)
        self.assertNotIn("m_iHarborWaterFood", write)

    def test_ai_values_projected_food(self) -> None:
        ai = self._function(self.city_ai, "int CvCityAI::AI_buildingValueThreshold")
        self.assertIn("getPotentialHarborWaterFood()", ai)
        self.assertIn("iHarborWaterFood * 6", ai)
        self.assertIn("iHarborWaterFood * 4", ai)

    def test_building_and_city_help_are_wired(self) -> None:
        building_help = self._function(
            self.text_mgr, "void CvGameTextMgr::setBuildingHelp"
        )
        yield_help = self._function(self.text_mgr, "void CvGameTextMgr::setYieldHelp")
        self.assertIn("TXT_KEY_BUILDING_HARBOR_WATER_FOOD_CITY", building_help)
        self.assertIn("getPotentialHarborWaterFood()", building_help)
        self.assertIn("TXT_KEY_BUILDING_HARBOR_WATER_FOOD_ACTIVE", yield_help)
        self.assertIn("getActiveHarborBuilding()", yield_help)

    def test_localized_help_keys_have_all_fallbacks(self) -> None:
        languages = ("English", "French", "German", "Italian", "Spanish")
        entries = {}
        for node in self.text.getroot():
            children = {
                child.tag.rsplit("}", 1)[-1]: child.text for child in node
            }
            entries[children["Tag"]] = children
        for key in (
            "TXT_KEY_BUILDING_HARBOR_WATER_FOOD",
            "TXT_KEY_BUILDING_HARBOR_WATER_FOOD_CITY",
            "TXT_KEY_BUILDING_HARBOR_WATER_FOOD_ACTIVE",
        ):
            with self.subTest(key=key):
                self.assertIn(key, entries)
                for language in languages:
                    self.assertTrue(entries[key].get(language))

    @staticmethod
    def _function(source: str, signature: str) -> str:
        start = source.index(signature)
        brace = source.index("{", start)
        depth = 0
        for index in range(brace, len(source)):
            if source[index] == "{":
                depth += 1
            elif source[index] == "}":
                depth -= 1
                if depth == 0:
                    return source[start : index + 1]
        raise AssertionError(f"Unterminated function: {signature}")


if __name__ == "__main__":
    unittest.main()
