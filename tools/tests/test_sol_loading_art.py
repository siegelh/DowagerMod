from __future__ import annotations

import struct
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BTS = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
)
MAIN_MENUS = BTS / "XML" / "Art" / "CIV4MainMenus.xml"
INTERFACE_ART = BTS / "XML" / "Art" / "CIV4ArtDefines_Interface.xml"
LOADING_ART = BTS / "Art" / "Interface" / "Screens" / "Loading"

EXPECTED_ART = {
    "MAINMENU_LOAD_DOWAGER": (
        "Art/Interface/Screens/Loading/LoadingScreenBGDowager.dds",
        (1024, 1024),
    ),
    "MAINMENU_SLIDESHOW_LOAD_DOWAGER": (
        "Art/Interface/Screens/Loading/LoadingScreenBGslideshowDowager.dds",
        (1024, 512),
    ),
}


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child_text(element: ET.Element, name: str) -> str:
    node = next(child for child in element if local(child.tag) == name)
    return (node.text or "").strip()


class SolLoadingArtTests(unittest.TestCase):
    def test_classical_and_bts_profiles_use_dedicated_dowager_art(self) -> None:
        profiles = {
            child_text(menu, "Type"): menu
            for menu in ET.parse(MAIN_MENUS).getroot().iter()
            if local(menu.tag) == "MainMenu"
        }
        for profile_name in ("MAIN_MENU_CLASSICAL", "MAIN_MENU_BEYOND_SWORD"):
            with self.subTest(profile=profile_name):
                profile = profiles[profile_name]
                self.assertEqual(child_text(profile, "Loading"), "MAINMENU_LOAD_DOWAGER")
                self.assertEqual(
                    child_text(profile, "LoadingSlideshow"),
                    "MAINMENU_SLIDESHOW_LOAD_DOWAGER",
                )
        self.assertEqual(child_text(profiles["MAIN_MENU_VANILLA"], "Loading"), "MAINMENU_LOAD")
        self.assertEqual(
            child_text(profiles["MAIN_MENU_WARLORDS"], "Loading"),
            "MAINMENU_LOAD_WARLORDS",
        )

    def test_dedicated_art_keys_resolve_to_valid_dxt1_assets(self) -> None:
        mappings = {
            child_text(info, "Type"): child_text(info, "Path")
            for info in ET.parse(INTERFACE_ART).getroot().iter()
            if local(info.tag) == "InterfaceArtInfo"
        }
        for key, (relative_path, dimensions) in EXPECTED_ART.items():
            with self.subTest(key=key):
                self.assertEqual(mappings[key], relative_path)
                path = BTS / Path(*relative_path.split("/"))
                header = path.read_bytes()[:128]
                self.assertEqual(header[:4], b"DDS ")
                self.assertEqual(struct.unpack_from("<I", header, 4)[0], 124)
                height, width = struct.unpack_from("<II", header, 12)
                self.assertEqual((width, height), dimensions)
                self.assertEqual(header[84:88], b"DXT1")

    def test_stock_loading_art_remains_available(self) -> None:
        for name in (
            "LoadingScreenBGBeyondtheSword.dds",
            "LoadingScreenBGslideshowBeyondtheSword.dds",
            "LoadingScreenBGClassical.dds",
            "LoadingScreenBGslideshowClassical.dds",
            "LoadingScreenBG.dds",
        ):
            with self.subTest(name=name):
                self.assertTrue((LOADING_ART / name).is_file())
