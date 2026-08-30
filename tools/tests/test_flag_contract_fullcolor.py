from __future__ import annotations

import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path, PurePosixPath

import pytest


ROOT = Path(__file__).resolve().parents[2]
ASSETS = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
)
ART_DEFINES = ASSETS / "XML" / "Art" / "CIV4ArtDefines_Civilization.xml"
CIVILIZATION_INFOS = (
    ASSETS / "XML" / "Civilizations" / "CIV4CivilizationInfos.xml"
)
PLAYER_COLOR_INFOS = ASSETS / "XML" / "Interface" / "CIV4PlayerColorInfos.xml"
COLOR_VALS = ASSETS / "XML" / "Interface" / "CIV4ColorVals.xml"
FLAG_MANIFEST = ROOT / "tools" / "flags" / "manifest.json"

EXPECTED_TOTAL = 59
DDS_MAGIC = b"DDS "
DDS_HEADER_BYTES = 128
DDS_HEADER_SIZE = 124
DDS_FOURCC = b"DXT3"
DDS_WIDTH = 128
DDS_HEIGHT = 128
DDS_MIP_COUNT = 8
DDS_TOP_LINEAR_SIZE = 16_384
DDS_FILE_BYTES = 22_000
DDS_MIP_DIMENSIONS = (
    (128, 128),
    (64, 64),
    (32, 32),
    (16, 16),
    (8, 8),
    (4, 4),
    (2, 2),
    (1, 1),
)
DDS_MIP_PAYLOAD_BYTES = (16_384, 4_096, 1_024, 256, 64, 16, 16, 16)

PROTECTED_XML_SHA256 = {
    CIVILIZATION_INFOS: "5912545e05804142015d13fa5adcd5425a71a36e82f338a9dce544f53ff6657f",
    PLAYER_COLOR_INFOS: "3a4607e6b52a3f5678d81c8ecc8945f49f415b0cd231720829aa4422d60276a4",
    COLOR_VALS: "455e3f437d9c3cd629ffea7cdbb98304dbd8e53fc703b71416cc694efcfa6860",
}

# CivilizationType -> (ArtDefineTag, preserved repository-relative DDS path).
# This is deliberately embedded rather than loaded from the production session
# report so the regression contract remains portable with the repository.
FULLCOLOR_FLAGS = {
    "CIVILIZATION_AMERICA_FEDERAL": (
        "ART_DEF_CIVILIZATION_AMERICA_FEDERAL",
        "Art/Interface/TeamColor/FlagDECAL_AmericaFederal.dds",
    ),
    "CIVILIZATION_AMERICA_FOUNDING_REPUBLIC": (
        "ART_DEF_CIVILIZATION_AMERICA",
        "Art/Interface/TeamColor/FlagDECAL_Star.dds",
    ),
    "CIVILIZATION_AMERICA_NEW_DEAL": (
        "ART_DEF_CIVILIZATION_AMERICA_NEW_DEAL",
        "Art/Interface/TeamColor/FlagDECAL_AmericaNewDeal.dds",
    ),
    "CIVILIZATION_AMERICA_UNION": (
        "ART_DEF_CIVILIZATION_AMERICA_UNION",
        "Art/Interface/TeamColor/FlagDECAL_AmericaUnion.dds",
    ),
    "CIVILIZATION_APACHE_CONFEDERACY": (
        "ART_DEF_CIVILIZATION_APACHE_CONFEDERACY",
        "Art/Interface/TeamColor/FlagDECAL_Apache.dds",
    ),
    "CIVILIZATION_ARABIA": (
        "ART_DEF_CIVILIZATION_ARABIA",
        "Art/Interface/TeamColor/FlagDECAL_Arabic.dds",
    ),
    "CIVILIZATION_ATHENIAN_GREECE": (
        "ART_DEF_CIVILIZATION_GREECE",
        "Art/Interface/TeamColor/FlagDECAL_Helmet.dds",
    ),
    "CIVILIZATION_AZTEC": (
        "ART_DEF_CIVILIZATION_AZTEC",
        "Art/Interface/TeamColor/FlagDECAL_AztecCalendar.dds",
    ),
    "CIVILIZATION_BABYLON": (
        "ART_DEF_CIVILIZATION_BABYLON",
        "Art/Interface/TeamColor/FlagDECAL_Babylon.dds",
    ),
    "CIVILIZATION_BRITISH_REGENCY": (
        "ART_DEF_CIVILIZATION_ENGLAND_REGENCY",
        "Art/Interface/TeamColor/FlagDECAL_EnglandRegency.dds",
    ),
    "CIVILIZATION_BYZANTIUM": (
        "ART_DEF_CIVILIZATION_BYZANTIUM",
        "Art/Interface/TeamColor/FlagDECAL_Byzantine.dds",
    ),
    "CIVILIZATION_CARTHAGE": (
        "ART_DEF_CIVILIZATION_CARTHAGE",
        "Art/Interface/TeamColor/FlagDECAL_Carthage.dds",
    ),
    "CIVILIZATION_EGYPT_EIGHTEENTH_DYNASTY": (
        "ART_DEF_CIVILIZATION_EGYPT_EIGHTEENTH_DYNASTY",
        "Art/Interface/TeamColor/FlagDECAL_EgyptEighteenthDynasty.dds",
    ),
    "CIVILIZATION_EGYPT_NEW_KINGDOM": (
        "ART_DEF_CIVILIZATION_EGYPT",
        "Art/Interface/TeamColor/FlagDECAL_EyeOfRa.dds",
    ),
    "CIVILIZATION_ELIZABETHAN_ENGLAND": (
        "ART_DEF_CIVILIZATION_ENGLAND",
        "Art/Interface/TeamColor/FlagDECAL_StGeorgeCross.dds",
    ),
    "CIVILIZATION_ETHIOPIA_IMPERIAL": (
        "ART_DEF_CIVILIZATION_ETHIOPIA",
        "Art/Interface/TeamColor/FlagDECAL_Ethiopia.dds",
    ),
    "CIVILIZATION_ETHIOPIA_SOLOMONIC": (
        "ART_DEF_CIVILIZATION_ETHIOPIA_SOLOMONIC",
        "Art/Interface/TeamColor/FlagDECAL_EthiopiaSolomonic.dds",
    ),
    "CIVILIZATION_FRANCE_BOURBON": (
        "ART_DEF_CIVILIZATION_FRANCE",
        "Art/Interface/TeamColor/FlagDECAL_FleurDeLis.dds",
    ),
    "CIVILIZATION_FRANCE_FIFTH_REPUBLIC": (
        "ART_DEF_CIVILIZATION_FRANCE_FIFTH_REPUBLIC",
        "Art/Interface/TeamColor/FlagDECAL_FranceFifthRepublic.dds",
    ),
    "CIVILIZATION_FRANCE_FIRST_EMPIRE": (
        "ART_DEF_CIVILIZATION_FRANCE_FIRST_EMPIRE",
        "Art/Interface/TeamColor/FlagDECAL_FranceFirstEmpire.dds",
    ),
    "CIVILIZATION_GAULIC_CONFEDERATION": (
        "ART_DEF_CIVILIZATION_GAULIC_CONFEDERATION",
        "Art/Interface/TeamColor/FlagDECAL_Gaul.dds",
    ),
    "CIVILIZATION_GERMAN_EMPIRE": (
        "ART_DEF_CIVILIZATION_GERMAN_EMPIRE",
        "Art/Interface/TeamColor/FlagDECAL_GermanEmpire.dds",
    ),
    "CIVILIZATION_HOLY_ROMAN": (
        "ART_DEF_CIVILIZATION_HOLY_ROMAN",
        "Art/Interface/TeamColor/FlagDECAL_HolyRomanEmpire.dds",
    ),
    "CIVILIZATION_ICENI_BRITAIN": (
        "ART_DEF_CIVILIZATION_ICENI_BRITAIN",
        "Art/Interface/TeamColor/FlagDECAL_Iceni.dds",
    ),
    "CIVILIZATION_IMPERIAL_RUSSIA": (
        "ART_DEF_CIVILIZATION_RUSSIA",
        "Art/Interface/TeamColor/FlagDECAL_DoubleEagle.dds",
    ),
    "CIVILIZATION_INCA": (
        "ART_DEF_CIVILIZATION_INCA",
        "Art/Interface/TeamColor/FlagDECAL_Sun.dds",
    ),
    "CIVILIZATION_INDIA": (
        "ART_DEF_CIVILIZATION_INDIA_GANDHI",
        "Art/Interface/TeamColor/FlagDECAL_IndiaGandhi.dds",
    ),
    "CIVILIZATION_JAPAN": (
        "ART_DEF_CIVILIZATION_JAPAN",
        "Art/Interface/TeamColor/FlagDECAL_Dot.dds",
    ),
    "CIVILIZATION_KHMER": (
        "ART_DEF_CIVILIZATION_KHMER",
        "Art/Interface/TeamColor/FlagDECAL_Khmer.dds",
    ),
    "CIVILIZATION_KOREA": (
        "ART_DEF_CIVILIZATION_KOREA",
        "Art/Interface/TeamColor/FlagDECAL_KoreanSymbol.dds",
    ),
    "CIVILIZATION_MACEDONIAN_EMPIRE": (
        "ART_DEF_CIVILIZATION_MACEDONIAN_EMPIRE",
        "Art/Interface/TeamColor/FlagDECAL_Macedon.dds",
    ),
    "CIVILIZATION_MALI": (
        "ART_DEF_CIVILIZATION_MALI",
        "Art/Interface/TeamColor/FlagDECAL_Mask.dds",
    ),
    "CIVILIZATION_MAURYA": (
        "ART_DEF_CIVILIZATION_INDIA",
        "Art/Interface/TeamColor/FlagDECAL_WheelOfLaw.dds",
    ),
    "CIVILIZATION_MAYA": (
        "ART_DEF_CIVILIZATION_MAYA",
        "Art/Interface/TeamColor/FlagDECAL_Maya.dds",
    ),
    "CIVILIZATION_MONGOL_EMPIRE": (
        "ART_DEF_CIVILIZATION_MONGOL",
        "Art/Interface/TeamColor/FlagDECAL_Horse.dds",
    ),
    "CIVILIZATION_NATIVE_AMERICA": (
        "ART_DEF_CIVILIZATION_NATIVE_AMERICA",
        "Art/Interface/TeamColor/FlagDECAL_NativeAmerica.dds",
    ),
    "CIVILIZATION_NETHERLANDS": (
        "ART_DEF_CIVILIZATION_NETHERLANDS",
        "Art/Interface/TeamColor/FlagDECAL_Netherlands.dds",
    ),
    "CIVILIZATION_OTTOMAN_CLASSICAL": (
        "ART_DEF_CIVILIZATION_OTTOMAN_CLASSICAL",
        "Art/Interface/TeamColor/FlagDECAL_OttomanClassical.dds",
    ),
    "CIVILIZATION_OTTOMAN_CONQUEST": (
        "ART_DEF_CIVILIZATION_OTTOMANS",
        "Art/Interface/TeamColor/FlagDECAL_Ottoman.dds",
    ),
    "CIVILIZATION_PEOPLES_REPUBLIC_CHINA": (
        "ART_DEF_CIVILIZATION_PRC",
        "Art/BTG/Civilization/PRC/flagdecal_prc.dds",
    ),
    "CIVILIZATION_PERSIA_FOUNDING_ACHAEMENID": (
        "ART_DEF_CIVILIZATION_PERSIA_FOUNDING_ACHAEMENID",
        "Art/Interface/TeamColor/FlagDECAL_PersiaFounding.dds",
    ),
    "CIVILIZATION_PERSIA_IMPERIAL_ACHAEMENID": (
        "ART_DEF_CIVILIZATION_PERSIA_IMPERIAL_ACHAEMENID",
        "Art/Interface/TeamColor/FlagDECAL_PersiaImperial.dds",
    ),
    "CIVILIZATION_PETRINE_RUSSIA": (
        "ART_DEF_CIVILIZATION_RUSSIA_PETRINE",
        "Art/Interface/TeamColor/FlagDECAL_RussiaPetrine.dds",
    ),
    "CIVILIZATION_POLAND": (
        "ART_DEF_CIVILIZATION_POLAND",
        "Art/Interface/TeamColor/FlagDECAL_Poland.dds",
    ),
    "CIVILIZATION_POLYNESIA_BTG": (
        "ART_DEF_CIVILIZATION_POLYNESIA_BTG",
        "Art/BTG/Polynesia/flagdecal_polynesia.dds",
    ),
    "CIVILIZATION_PORTUGAL": (
        "ART_DEF_CIVILIZATION_PORTUGAL",
        "Art/Interface/TeamColor/FlagDECAL_Portugal.dds",
    ),
    "CIVILIZATION_PRUSSIA": (
        "ART_DEF_CIVILIZATION_PRUSSIA",
        "Art/Interface/TeamColor/FlagDECAL_Prussia.dds",
    ),
    "CIVILIZATION_QIN_DYNASTY": (
        "ART_DEF_CIVILIZATION_CHINA",
        "Art/Interface/TeamColor/FlagDECAL_Dragon.dds",
    ),
    "CIVILIZATION_ROMAN_PRINCIPATE": (
        "ART_DEF_CIVILIZATION_ROME",
        "Art/Interface/TeamColor/FlagDECAL_Laurels.dds",
    ),
    "CIVILIZATION_ROMAN_REPUBLIC_LATE": (
        "ART_DEF_CIVILIZATION_ROMAN_REPUBLIC_LATE",
        "Art/Interface/TeamColor/FlagDECAL_RomanRepublic.dds",
    ),
    "CIVILIZATION_SPAIN": (
        "ART_DEF_CIVILIZATION_SPAIN",
        "Art/Interface/TeamColor/FlagDECAL_Castle.dds",
    ),
    "CIVILIZATION_SUMERIA": (
        "ART_DEF_CIVILIZATION_SUMERIA",
        "Art/Interface/TeamColor/FlagDECAL_Sumeria.dds",
    ),
    "CIVILIZATION_USSR": (
        "ART_DEF_CIVILIZATION_RUSSIA_USSR",
        "Art/Interface/TeamColor/FlagDECAL_RussiaUSSR.dds",
    ),
    "CIVILIZATION_VENICE": (
        "ART_DEF_CIVILIZATION_VENICE",
        "Art/BTG/Civilization/Venice/flagdecal_venice.dds",
    ),
    "CIVILIZATION_VICTORIAN_BRITAIN": (
        "ART_DEF_CIVILIZATION_ENGLAND_VICTORIAN",
        "Art/Interface/TeamColor/FlagDECAL_EnglandVictorian.dds",
    ),
    "CIVILIZATION_VIKING": (
        "ART_DEF_CIVILIZATION_VIKINGS",
        "Art/Interface/TeamColor/FlagDECAL_Viking.dds",
    ),
    "CIVILIZATION_WARTIME_BRITAIN": (
        "ART_DEF_CIVILIZATION_ENGLAND_WARTIME",
        "Art/Interface/TeamColor/FlagDECAL_EnglandWartime.dds",
    ),
    "CIVILIZATION_YUAN_DYNASTY": (
        "ART_DEF_CIVILIZATION_YUAN_DYNASTY",
        "Art/Interface/TeamColor/FlagDECAL_Yuan.dds",
    ),
    "CIVILIZATION_ZULU": (
        "ART_DEF_CIVILIZATION_ZULU",
        "Art/Interface/TeamColor/FlagDECAL_ZuluShield.dds",
    ),
}

# CivilizationType -> (repository-relative DDS path, exact file SHA-256).
# Generated from the repaired outputs, then embedded so this contract has no
# dependency on session-local artifacts.
EXPECTED_DDS_SHA256 = {
    "CIVILIZATION_AMERICA_FEDERAL": (
        "Art/Interface/TeamColor/FlagDECAL_AmericaFederal.dds",
        "aad6cf8690f2285e332ca34a864d8dff2fce1b46c9e5a63af0b90f6a1413fac2",
    ),
    "CIVILIZATION_AMERICA_FOUNDING_REPUBLIC": (
        "Art/Interface/TeamColor/FlagDECAL_Star.dds",
        "2f4cbdb54ea571e90d7d8b2a6eb702f5dc88de869d6bcdbbc734aaa75e3cb8ea",
    ),
    "CIVILIZATION_AMERICA_NEW_DEAL": (
        "Art/Interface/TeamColor/FlagDECAL_AmericaNewDeal.dds",
        "209d4893a1cf58abcb16abdadd8f097940b1f461f2b2da4e62f987eeb6c8d70a",
    ),
    "CIVILIZATION_AMERICA_UNION": (
        "Art/Interface/TeamColor/FlagDECAL_AmericaUnion.dds",
        "d067a6ff6f552cbc1ec9978285a4f9ca5dd98d7262f745965958eade81f255e3",
    ),
    "CIVILIZATION_APACHE_CONFEDERACY": (
        "Art/Interface/TeamColor/FlagDECAL_Apache.dds",
        "26f590875cca4d2e4ac1c552c453de451930d40128133c5695cc91fd06c374b3",
    ),
    "CIVILIZATION_ARABIA": (
        "Art/Interface/TeamColor/FlagDECAL_Arabic.dds",
        "96f5846bc9e6dded72376711844fdde04ca31060be6a995689bd4d2fd3bbee9f",
    ),
    "CIVILIZATION_ATHENIAN_GREECE": (
        "Art/Interface/TeamColor/FlagDECAL_Helmet.dds",
        "dbacc342c174c595bb214222ab1285401259b73817627cdcc79d376fd794fd16",
    ),
    "CIVILIZATION_AZTEC": (
        "Art/Interface/TeamColor/FlagDECAL_AztecCalendar.dds",
        "57038da4353578b6af3fef69864f19902eda2cec1058ea8e6799ed3ff0d39c20",
    ),
    "CIVILIZATION_BABYLON": (
        "Art/Interface/TeamColor/FlagDECAL_Babylon.dds",
        "cd9ade99028040faa6ceaa8b0398fb98ece42eb6218cff9aee19dfb85304ea06",
    ),
    "CIVILIZATION_BRITISH_REGENCY": (
        "Art/Interface/TeamColor/FlagDECAL_EnglandRegency.dds",
        "570e811b6dbddad97b87a37987f0cf13c7b423eff9bbcc0a87727e64e51a9006",
    ),
    "CIVILIZATION_BYZANTIUM": (
        "Art/Interface/TeamColor/FlagDECAL_Byzantine.dds",
        "67b8087078d81c590a22404fd4762ab4accf3bcc5cc3a13e8dcbb7fbaf6f0309",
    ),
    "CIVILIZATION_CARTHAGE": (
        "Art/Interface/TeamColor/FlagDECAL_Carthage.dds",
        "8f0fae3c8b3de3ce653fd6872d8d431dfdc6c2f52e8b5bc4b603c80f7b8519af",
    ),
    "CIVILIZATION_EGYPT_EIGHTEENTH_DYNASTY": (
        "Art/Interface/TeamColor/FlagDECAL_EgyptEighteenthDynasty.dds",
        "e5e698f2a81b85876d41e93694ea2d2090b8186cb373987417d3f10de1d2982e",
    ),
    "CIVILIZATION_EGYPT_NEW_KINGDOM": (
        "Art/Interface/TeamColor/FlagDECAL_EyeOfRa.dds",
        "fdb7e528d4037814fd5f85e33b527c24582a80c81d9748a4b8e3f5fb08959d69",
    ),
    "CIVILIZATION_ELIZABETHAN_ENGLAND": (
        "Art/Interface/TeamColor/FlagDECAL_StGeorgeCross.dds",
        "614c0a167b6310c35a792dd9e4c78ad4d8a54765982606367d2c9080ff532666",
    ),
    "CIVILIZATION_ETHIOPIA_IMPERIAL": (
        "Art/Interface/TeamColor/FlagDECAL_Ethiopia.dds",
        "0e375aa88c3652c75123ac6cfbd568ba0a5f1dcf94a7c65253f343c66126bfb0",
    ),
    "CIVILIZATION_ETHIOPIA_SOLOMONIC": (
        "Art/Interface/TeamColor/FlagDECAL_EthiopiaSolomonic.dds",
        "73a5742765efea347740a9b013f5ce0c00feda2caa6db165be11894c36b4ebed",
    ),
    "CIVILIZATION_FRANCE_BOURBON": (
        "Art/Interface/TeamColor/FlagDECAL_FleurDeLis.dds",
        "eea5ac958ccb3258db65c5e897900ec6d569c1857ac45288460e4937887058f3",
    ),
    "CIVILIZATION_FRANCE_FIFTH_REPUBLIC": (
        "Art/Interface/TeamColor/FlagDECAL_FranceFifthRepublic.dds",
        "069df445af98209396b0459aeda4186c795ad1a61a0f2f9d100b5e26bb5cfb6d",
    ),
    "CIVILIZATION_FRANCE_FIRST_EMPIRE": (
        "Art/Interface/TeamColor/FlagDECAL_FranceFirstEmpire.dds",
        "f6dfc7bc44619a6bc7bd884da0a6a3bebb5d792da81cbb1cdc8cafe0a0a2adbe",
    ),
    "CIVILIZATION_GAULIC_CONFEDERATION": (
        "Art/Interface/TeamColor/FlagDECAL_Gaul.dds",
        "f0457d3bc8110dbc3fe27414e2dad70d90d50608d286f6ab988ec1bee54ee06c",
    ),
    "CIVILIZATION_GERMAN_EMPIRE": (
        "Art/Interface/TeamColor/FlagDECAL_GermanEmpire.dds",
        "dee620da5f8e3cd8f8a910fa5ce77f3faf197dc1bc402c0d95722f8f57666e90",
    ),
    "CIVILIZATION_HOLY_ROMAN": (
        "Art/Interface/TeamColor/FlagDECAL_HolyRomanEmpire.dds",
        "e7afeab3d5d6cdd1ff93938d410885bef5302497eccd2e890e56e85cf175cd82",
    ),
    "CIVILIZATION_ICENI_BRITAIN": (
        "Art/Interface/TeamColor/FlagDECAL_Iceni.dds",
        "5e38506130c5c6390b94d8b3ee4242faab407129d78b604e668d2667bbae4bbf",
    ),
    "CIVILIZATION_IMPERIAL_RUSSIA": (
        "Art/Interface/TeamColor/FlagDECAL_DoubleEagle.dds",
        "e7de79fb74e821e1346fc970d360822f6d2860d46dc67bad56bcd73dfdbd52f6",
    ),
    "CIVILIZATION_INCA": (
        "Art/Interface/TeamColor/FlagDECAL_Sun.dds",
        "e176faa26580d58077735a5d9dd7a5ac83fc27e388840838a50bddf48d34dbd9",
    ),
    "CIVILIZATION_INDIA": (
        "Art/Interface/TeamColor/FlagDECAL_IndiaGandhi.dds",
        "39f4ea777345cb5d07d3e62f41f527489dd1705bc7fae8e8121cc181141e43d2",
    ),
    "CIVILIZATION_JAPAN": (
        "Art/Interface/TeamColor/FlagDECAL_Dot.dds",
        "55a980d1c4a462ffe70eecf01b6d0ba551e5ba8b0fb5448f02d9ee6a29513a3e",
    ),
    "CIVILIZATION_KHMER": (
        "Art/Interface/TeamColor/FlagDECAL_Khmer.dds",
        "ee6b0730ee0f3e23b0f89cc6570bf06dc91e4d73fca7bf2de0d98300ee3c7bf9",
    ),
    "CIVILIZATION_KOREA": (
        "Art/Interface/TeamColor/FlagDECAL_KoreanSymbol.dds",
        "f96e6354cf6679ddca1efe50b7ebe227546f31777b719562b4b5f5a89dcde5f7",
    ),
    "CIVILIZATION_MACEDONIAN_EMPIRE": (
        "Art/Interface/TeamColor/FlagDECAL_Macedon.dds",
        "5bcbdd1d820842ea3e931de1fe78a5dcec280c8670b45a1d697170f89b42d30d",
    ),
    "CIVILIZATION_MALI": (
        "Art/Interface/TeamColor/FlagDECAL_Mask.dds",
        "14e640d02065dd4e55f78967635ff92a56a0d99525a57d9d25a4de4abd71e466",
    ),
    "CIVILIZATION_MAURYA": (
        "Art/Interface/TeamColor/FlagDECAL_WheelOfLaw.dds",
        "8a19993d44b710e2afd7eea08aab951db9d72c9aa3a2489480c0d8302b020995",
    ),
    "CIVILIZATION_MAYA": (
        "Art/Interface/TeamColor/FlagDECAL_Maya.dds",
        "cca287635512a66ca80591a2f00120f101000166b2e80fc65923be9fe1c6a427",
    ),
    "CIVILIZATION_MONGOL_EMPIRE": (
        "Art/Interface/TeamColor/FlagDECAL_Horse.dds",
        "b3ab5dec4e6ae56640e6711ef7aec6236bb0876ecbbc761c2cf4d584dcfae40e",
    ),
    "CIVILIZATION_NATIVE_AMERICA": (
        "Art/Interface/TeamColor/FlagDECAL_NativeAmerica.dds",
        "6b7fbd7ed87e0f8557eae471232411d288a1c05c15305d22919bae833b0583d8",
    ),
    "CIVILIZATION_NETHERLANDS": (
        "Art/Interface/TeamColor/FlagDECAL_Netherlands.dds",
        "24377b99c3f9f4b4aaf6df1fc5d4cf1e70b9ec1f568d40bc68cf50970275a72f",
    ),
    "CIVILIZATION_OTTOMAN_CLASSICAL": (
        "Art/Interface/TeamColor/FlagDECAL_OttomanClassical.dds",
        "007e92ebc21cf0fe3305396c85e169c31f63a3dbab4856357cc0f6e760ae44e0",
    ),
    "CIVILIZATION_OTTOMAN_CONQUEST": (
        "Art/Interface/TeamColor/FlagDECAL_Ottoman.dds",
        "dddb6f4ee6ce036a7ea06d5c758bef292a577c8cd4c9396fde4e3f50ba4822ff",
    ),
    "CIVILIZATION_PEOPLES_REPUBLIC_CHINA": (
        "Art/BTG/Civilization/PRC/flagdecal_prc.dds",
        "ce1fdc568b23e80edf30913483f9d378a6fbbda968ba0e6d6e8d149ca6451c21",
    ),
    "CIVILIZATION_PERSIA_FOUNDING_ACHAEMENID": (
        "Art/Interface/TeamColor/FlagDECAL_PersiaFounding.dds",
        "c748f49b2bdf643335689596335b5d4c9631fa253fbd2e06e12c81fa3dc2a127",
    ),
    "CIVILIZATION_PERSIA_IMPERIAL_ACHAEMENID": (
        "Art/Interface/TeamColor/FlagDECAL_PersiaImperial.dds",
        "b3ad9056cbf35eb1b7175185c0b2c88409b0a8c3bf06d53a2f0cb39f9cb9ea36",
    ),
    "CIVILIZATION_PETRINE_RUSSIA": (
        "Art/Interface/TeamColor/FlagDECAL_RussiaPetrine.dds",
        "1cdb70ea687448d40b78214b6c3b29fb038cf6b262e9f06e70a71a49130d77e5",
    ),
    "CIVILIZATION_POLAND": (
        "Art/Interface/TeamColor/FlagDECAL_Poland.dds",
        "9330974c84197ab1a4d1c54f39a909d999a31b7f6e7e65ff81740b842693f984",
    ),
    "CIVILIZATION_POLYNESIA_BTG": (
        "Art/BTG/Polynesia/flagdecal_polynesia.dds",
        "a0919d9ebc38e0bb11ab3d7f2414c0cbfd5d727e844e45367d7083f499bb614c",
    ),
    "CIVILIZATION_PORTUGAL": (
        "Art/Interface/TeamColor/FlagDECAL_Portugal.dds",
        "4d85a5155ff5e9e3446cebe224e8a5710a2cfaa5aca00c27d27090ca82ef86ef",
    ),
    "CIVILIZATION_PRUSSIA": (
        "Art/Interface/TeamColor/FlagDECAL_Prussia.dds",
        "4aa1702f088cd712c8b815bbef29cf382011aa4d9dc2999228138ca198a22cac",
    ),
    "CIVILIZATION_QIN_DYNASTY": (
        "Art/Interface/TeamColor/FlagDECAL_Dragon.dds",
        "7685838470e830befa3cf62245ecd611d397439aec7358e96252ec31f2d7bf71",
    ),
    "CIVILIZATION_ROMAN_PRINCIPATE": (
        "Art/Interface/TeamColor/FlagDECAL_Laurels.dds",
        "94beade5583aed082f53b50ceb698e50f100d9fe9ff618477f1f453e200c72f5",
    ),
    "CIVILIZATION_ROMAN_REPUBLIC_LATE": (
        "Art/Interface/TeamColor/FlagDECAL_RomanRepublic.dds",
        "87d3893da71dd00bffaebdde7452ffd71a261f2d6ef5fd2dda2d43a444ebc65a",
    ),
    "CIVILIZATION_SPAIN": (
        "Art/Interface/TeamColor/FlagDECAL_Castle.dds",
        "253a10485418060da714c386f3d4e6b5d734dc3cf9c9ed58980794436875cc6f",
    ),
    "CIVILIZATION_SUMERIA": (
        "Art/Interface/TeamColor/FlagDECAL_Sumeria.dds",
        "74174ae5cbd3b7411e72a82d6448ba703fbebeea54c97aee6c66be7b12910f80",
    ),
    "CIVILIZATION_USSR": (
        "Art/Interface/TeamColor/FlagDECAL_RussiaUSSR.dds",
        "9de0f51dcc8f8a1e50f57ade6724bbb16eaf89779c7e00c2e118b18ce32cd7e0",
    ),
    "CIVILIZATION_VENICE": (
        "Art/BTG/Civilization/Venice/flagdecal_venice.dds",
        "597ff33e56084fa12422b8b9761621cc5168e545fb51a294896476b5035bc7cf",
    ),
    "CIVILIZATION_VICTORIAN_BRITAIN": (
        "Art/Interface/TeamColor/FlagDECAL_EnglandVictorian.dds",
        "64910c810eb16b8140854a453f89c49e0ef48c66c662e54859e185e48cea190e",
    ),
    "CIVILIZATION_VIKING": (
        "Art/Interface/TeamColor/FlagDECAL_Viking.dds",
        "396da9888ca0056b1e9763c1ccc1376b885ba4cd6c8a4464e905aed5700f7485",
    ),
    "CIVILIZATION_WARTIME_BRITAIN": (
        "Art/Interface/TeamColor/FlagDECAL_EnglandWartime.dds",
        "4c3a3b2b38b39852652b191184ee46127b47277f5ef693a08125269f800e5dc4",
    ),
    "CIVILIZATION_YUAN_DYNASTY": (
        "Art/Interface/TeamColor/FlagDECAL_Yuan.dds",
        "bfb488c9968d7c013893032a373c604fb801216f80696486fe4755f22c7e7e5f",
    ),
    "CIVILIZATION_ZULU": (
        "Art/Interface/TeamColor/FlagDECAL_ZuluShield.dds",
        "3fbcb2e65380c98772988d7bede88d80cc5db992955a62d00b946d784808a955",
    ),
}

EXCLUDED_ART_BLOCKS = {
    "ART_DEF_CIVILIZATION_MINOR": (
        314,
        "b58dfd9ad647440b06bf4a06fdc642fabf67f1c974cb5c9a819f6aeeb7dab970",
    ),
    "ART_DEF_CIVILIZATION_BARBARIAN": (
        326,
        "1890b73796a7a4a4d1f9e6b7231c6c30a77b18e255a758f61e22b66a26360613",
    ),
    "ART_DEF_CIVILIZATION_CELTS": (
        304,
        "00fea59ba539adec65cd696e1af67314d701e4d59d098a4f47598dc7e080dacc",
    ),
    "ART_DEF_CIVILIZATION_GERMANY": (
        329,
        "45d5d17f928644f0de0fffa6fd7190cb201f109d0cc4e0cbf705af832baedba2",
    ),
    "ART_DEF_CIVILIZATION_PERSIA": (
        323,
        "29945862d42d3687fd1b60589dcc6ae45e7eda21fc90579cd380234bba40159d",
    ),
}

ART_BLOCK_PATTERN = re.compile(
    rb"<CivilizationArtInfo>.*?</CivilizationArtInfo>", re.DOTALL
)
TYPE_PATTERN = re.compile(rb"<Type>\s*([^<]+?)\s*</Type>")


class MipRgbValidationError(AssertionError):
    pass


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child_text(node: ET.Element, name: str) -> str:
    matches = [
        (child.text or "").strip()
        for child in node
        if _local_name(child.tag) == name
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one {name} child in {_local_name(node.tag)}, "
            f"found {len(matches)}"
        )
    return matches[0]


def _entries(path: Path, entry_name: str) -> list[ET.Element]:
    return [
        node
        for node in ET.parse(path).getroot().iter()
        if _local_name(node.tag) == entry_name
    ]


def _entries_by_type(
    path: Path, entry_name: str
) -> tuple[dict[str, ET.Element], dict[str, int]]:
    grouped: dict[str, list[ET.Element]] = defaultdict(list)
    for node in _entries(path, entry_name):
        grouped[_child_text(node, "Type")].append(node)
    duplicates = {
        type_name: len(nodes)
        for type_name, nodes in grouped.items()
        if len(nodes) != 1
    }
    return {type_name: nodes[0] for type_name, nodes in grouped.items()}, duplicates


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _asset_path(xml_path: str) -> Path:
    relative = PurePosixPath(xml_path.replace("\\", "/"))
    assert not relative.is_absolute() and ".." not in relative.parts, (
        f"unsafe DDS path in embedded contract: {xml_path}"
    )
    return ASSETS.joinpath(*relative.parts)


def _rgb_from_565(value: int) -> tuple[int, int, int]:
    red = (value >> 11) & 31
    green = (value >> 5) & 63
    blue = value & 31
    return (
        (red << 3) | (red >> 2),
        (green << 2) | (green >> 4),
        (blue << 3) | (blue >> 2),
    )


def _decode_dxt3_top_mip(payload: bytes) -> list[tuple[int, int, int]]:
    pixels = [(0, 0, 0)] * (DDS_WIDTH * DDS_HEIGHT)
    offset = 0
    for block_y in range(0, DDS_HEIGHT, 4):
        for block_x in range(0, DDS_WIDTH, 4):
            endpoint0, endpoint1, indices = struct.unpack_from(
                "<HHI", payload, offset + 8
            )
            color0 = _rgb_from_565(endpoint0)
            color1 = _rgb_from_565(endpoint1)
            palette = (
                color0,
                color1,
                tuple(
                    (2 * color0[channel] + color1[channel]) // 3
                    for channel in range(3)
                ),
                tuple(
                    (color0[channel] + 2 * color1[channel]) // 3
                    for channel in range(3)
                ),
            )
            for pixel_index in range(16):
                x = block_x + pixel_index % 4
                y = block_y + pixel_index // 4
                color_index = (indices >> (pixel_index * 2)) & 0x3
                pixels[y * DDS_WIDTH + x] = palette[color_index]
            offset += 16
    assert offset == len(payload)
    return pixels


def _assert_zero_dxt3_alpha(
    payloads: list[bytes],
) -> None:
    """Require Firaxis fixed-color alpha (zero in every DXT3 nibble and mip)."""
    assert len(payloads) == DDS_MIP_COUNT
    for mip_index, ((width, height), payload) in enumerate(
        zip(DDS_MIP_DIMENSIONS, payloads)
    ):
        for block_offset in range(0, len(payload), 16):
            alpha_block = payload[block_offset : block_offset + 8]
            for nibble_index in range(16):
                alpha_nibble = (
                    alpha_block[nibble_index // 2]
                    >> (4 * (nibble_index % 2))
                ) & 0xF
                if alpha_nibble != 0:
                    raise AssertionError(
                        "DXT3 alpha mismatch: expected every alpha nibble to "
                        "be zero across all 8 mips; "
                        f"mip={mip_index} ({width}x{height}), "
                        f"block={block_offset // 16}, "
                        f"nibble={nibble_index}, value={alpha_nibble}"
                    )


def _assert_nonzero_dxt3_rgb(payloads: list[bytes]) -> None:
    """Require every mip to contain actual DXT3 color-block data."""
    assert len(payloads) == DDS_MIP_COUNT
    failures = []
    for mip_index, ((width, height), payload) in enumerate(
        zip(DDS_MIP_DIMENSIONS, payloads)
    ):
        color_blocks = [
            payload[block_offset + 8 : block_offset + 16]
            for block_offset in range(0, len(payload), 16)
        ]
        if not color_blocks or any(len(block) != 8 for block in color_blocks):
            failures.append(
                "missing or truncated DXT3 color blocks: "
                f"mip={mip_index} ({width}x{height}), "
                f"color_blocks={len(color_blocks)}"
            )
        elif not any(any(block) for block in color_blocks):
            failures.append(
                "all DXT3 color-block bytes are zero: "
                f"mip={mip_index} ({width}x{height}), "
                f"color_blocks={len(color_blocks)}"
            )
    if failures:
        raise MipRgbValidationError(f"mip RGB failures={failures}")


def _parse_and_validate_dds(data: bytes) -> list[tuple[int, int, int]]:
    if len(data) != DDS_FILE_BYTES:
        raise AssertionError(
            f"file bytes={len(data)}, expected exact EOF at {DDS_FILE_BYTES}"
        )
    if data[:4] != DDS_MAGIC:
        raise AssertionError(f"magic={data[:4]!r}, expected {DDS_MAGIC!r}")
    if len(data[:DDS_HEADER_BYTES]) != DDS_HEADER_BYTES:
        raise AssertionError("truncated 128-byte DDS header")

    (
        header_size,
        flags,
        height,
        width,
        linear_size,
        depth,
        mip_count,
    ) = struct.unpack_from("<7I", data, 4)
    pixel_format_size, pixel_format_flags = struct.unpack_from("<II", data, 76)
    fourcc = data[84:88]

    expected_fields = {
        "header_size": (header_size, DDS_HEADER_SIZE),
        "width": (width, DDS_WIDTH),
        "height": (height, DDS_HEIGHT),
        "fourcc": (fourcc, DDS_FOURCC),
        "mip_count": (mip_count, DDS_MIP_COUNT),
        "top_linear_size": (linear_size, DDS_TOP_LINEAR_SIZE),
        "pixel_format_size": (pixel_format_size, 32),
        "depth": (depth, 0),
    }
    mismatches = {
        name: values
        for name, values in expected_fields.items()
        if values[0] != values[1]
    }
    if mismatches:
        raise AssertionError(f"header field mismatches (actual, expected): {mismatches}")
    if not flags & 0x20000:
        raise AssertionError("DDSD_MIPMAPCOUNT flag is not set")
    if not pixel_format_flags & 0x4:
        raise AssertionError("DDPF_FOURCC flag is not set")

    payloads = []
    offset = DDS_HEADER_BYTES
    actual_sizes = []
    for dimensions, expected_size in zip(
        DDS_MIP_DIMENSIONS, DDS_MIP_PAYLOAD_BYTES
    ):
        width, height = dimensions
        calculated_size = (
            16 * max(1, (width + 3) // 4) * max(1, (height + 3) // 4)
        )
        if calculated_size != expected_size:
            raise AssertionError(
                f"internal mip contract mismatch for {width}x{height}: "
                f"{calculated_size} != {expected_size}"
            )
        payload = data[offset : offset + expected_size]
        actual_sizes.append(len(payload))
        if len(payload) != expected_size:
            raise AssertionError(
                f"mip {width}x{height} bytes={len(payload)}, "
                f"expected={expected_size}"
            )
        payloads.append(payload)
        offset += expected_size
    if tuple(actual_sizes) != DDS_MIP_PAYLOAD_BYTES:
        raise AssertionError(
            f"mip payload sizes={tuple(actual_sizes)}, "
            f"expected={DDS_MIP_PAYLOAD_BYTES}"
        )
    if offset != len(data) or offset != DDS_FILE_BYTES:
        raise AssertionError(
            f"mip traversal EOF={offset}, file bytes={len(data)}, "
            f"expected={DDS_FILE_BYTES}"
        )
    _assert_zero_dxt3_alpha(payloads)
    _assert_nonzero_dxt3_rgb(payloads)
    return _decode_dxt3_top_mip(payloads[0])


assert len(FULLCOLOR_FLAGS) == EXPECTED_TOTAL
assert len({art_tag for art_tag, _ in FULLCOLOR_FLAGS.values()}) == EXPECTED_TOTAL
assert len({path for _, path in FULLCOLOR_FLAGS.values()}) == EXPECTED_TOTAL
assert len(EXPECTED_DDS_SHA256) == EXPECTED_TOTAL
assert {
    civilization_type: xml_path
    for civilization_type, (xml_path, _) in EXPECTED_DDS_SHA256.items()
} == {
    civilization_type: xml_path
    for civilization_type, (_, xml_path) in FULLCOLOR_FLAGS.items()
}
assert all(
    re.fullmatch(r"[0-9a-f]{64}", digest)
    for _, digest in EXPECTED_DDS_SHA256.values()
)
assert sum(DDS_MIP_PAYLOAD_BYTES) + DDS_HEADER_BYTES == DDS_FILE_BYTES


def test_embedded_production_contract_matches_canonical_manifest() -> None:
    document = json.loads(FLAG_MANIFEST.read_text(encoding="utf-8"))
    records = document["records"]
    assert document["record_count"] == EXPECTED_TOTAL
    canonical_mappings = {
        record["civilization_type"]: (
            record["art_define"],
            record["runtime_dds_path"],
        )
        for record in records
    }
    canonical_digests = {
        record["civilization_type"]: (
            record["runtime_dds_path"],
            record["production_dds_sha256"],
        )
        for record in records
    }
    assert canonical_mappings == FULLCOLOR_FLAGS
    assert canonical_digests == EXPECTED_DDS_SHA256


@pytest.mark.parametrize(
    ("path", "expected_sha256"),
    PROTECTED_XML_SHA256.items(),
    ids=lambda value: value.name if isinstance(value, Path) else None,
)
def test_protected_xml_files_are_byte_stable(
    path: Path, expected_sha256: str
) -> None:
    data = path.read_bytes()
    assert _sha256(data) == expected_sha256, (
        f"{path.relative_to(ROOT)} changed bytes: "
        f"sha256={_sha256(data)}, expected={expected_sha256}"
    )


def test_playable_civilization_art_mapping_is_exact() -> None:
    civs, duplicates = _entries_by_type(
        CIVILIZATION_INFOS, "CivilizationInfo"
    )
    playable = {
        civilization_type: node
        for civilization_type, node in civs.items()
        if _child_text(node, "bPlayable") == "1"
    }
    expected_types = set(FULLCOLOR_FLAGS)
    found_types = set(playable)
    mapping_mismatches = {
        civilization_type: (
            _child_text(playable[civilization_type], "ArtDefineTag"),
            FULLCOLOR_FLAGS[civilization_type][0],
        )
        for civilization_type in sorted(expected_types & found_types)
        if _child_text(playable[civilization_type], "ArtDefineTag")
        != FULLCOLOR_FLAGS[civilization_type][0]
    }
    assert (
        not duplicates
        and found_types == expected_types
        and not mapping_mismatches
        and len(playable) == EXPECTED_TOTAL
    ), (
        "playable civilization reconciliation failed: "
        f"expected={EXPECTED_TOTAL}, found={len(playable)}, "
        f"parsed={len(civs)}, valid={len(playable) - len(mapping_mismatches)}; "
        f"missing={sorted(expected_types - found_types)}; "
        f"unexpected={sorted(found_types - expected_types)}; "
        f"duplicates={duplicates}; "
        f"mapping_mismatches(actual, expected)={mapping_mismatches}"
    )


def test_fullcolor_art_definitions_are_exact() -> None:
    art_defines, duplicates = _entries_by_type(
        ART_DEFINES, "CivilizationArtInfo"
    )
    expected_by_tag = {
        art_tag: path for art_tag, path in FULLCOLOR_FLAGS.values()
    }
    expected_tags = set(expected_by_tag)
    resolved_tags = expected_tags & set(art_defines)
    path_mismatches = {
        art_tag: (
            _child_text(art_defines[art_tag], "Path"),
            expected_by_tag[art_tag],
        )
        for art_tag in sorted(resolved_tags)
        if _child_text(art_defines[art_tag], "Path")
        != expected_by_tag[art_tag]
    }
    white_mismatches = {
        art_tag: _child_text(art_defines[art_tag], "bWhiteFlag")
        for art_tag in sorted(resolved_tags)
        if _child_text(art_defines[art_tag], "bWhiteFlag") != "1"
    }
    all_white_tags = {
        art_tag
        for art_tag, node in art_defines.items()
        if _child_text(node, "bWhiteFlag") == "1"
    }
    valid = len(resolved_tags - set(path_mismatches) - set(white_mismatches))
    assert (
        not duplicates
        and resolved_tags == expected_tags
        and not path_mismatches
        and not white_mismatches
        and all_white_tags == expected_tags
    ), (
        "full-color ArtDefine reconciliation failed: "
        f"expected={EXPECTED_TOTAL}, found={len(resolved_tags)}, "
        f"parsed={len(art_defines)}, valid={valid}; "
        f"missing={sorted(expected_tags - set(art_defines))}; "
        f"duplicates={duplicates}; "
        f"path_mismatches(actual, expected)={path_mismatches}; "
        f"white_mismatches={white_mismatches}; "
        f"unexpected_white_tags={sorted(all_white_tags - expected_tags)}; "
        f"missing_white_tags={sorted(expected_tags - all_white_tags)}"
    )


@pytest.mark.parametrize(
    ("art_tag", "expected_bytes", "expected_sha256"),
    [
        (art_tag, expected_bytes, expected_sha256)
        for art_tag, (expected_bytes, expected_sha256) in EXCLUDED_ART_BLOCKS.items()
    ],
)
def test_excluded_art_blocks_are_byte_stable_and_not_white(
    art_tag: str, expected_bytes: int, expected_sha256: str
) -> None:
    blocks = {}
    for match in ART_BLOCK_PATTERN.finditer(ART_DEFINES.read_bytes()):
        raw = match.group(0)
        type_match = TYPE_PATTERN.search(raw)
        assert type_match is not None, "ArtInfo block has no Type"
        type_name = type_match.group(1).decode("ascii").strip()
        assert type_name not in blocks, f"duplicate raw ArtInfo block: {type_name}"
        blocks[type_name] = raw

    art_defines, duplicates = _entries_by_type(
        ART_DEFINES, "CivilizationArtInfo"
    )
    assert not duplicates
    assert art_tag not in {
        mapped_art_tag for mapped_art_tag, _ in FULLCOLOR_FLAGS.values()
    }
    assert art_tag in blocks and art_tag in art_defines
    raw = blocks[art_tag]
    assert (len(raw), _sha256(raw)) == (expected_bytes, expected_sha256), (
        f"{art_tag} raw block changed: "
        f"bytes={len(raw)}, sha256={_sha256(raw)}; "
        f"expected bytes={expected_bytes}, sha256={expected_sha256}"
    )
    assert _child_text(art_defines[art_tag], "bWhiteFlag") == "0"


def test_all_fullcolor_dds_files_reconcile_and_validate() -> None:
    found = 0
    parsed = 0
    valid = 0
    hashes: dict[str, list[str]] = defaultdict(list)
    digest_mismatches = []
    mip_rgb_failures = []
    validation_errors = []

    for civilization_type, (_, xml_path) in sorted(FULLCOLOR_FLAGS.items()):
        path = _asset_path(xml_path)
        if not path.is_file():
            validation_errors.append(f"{civilization_type}: missing {xml_path}")
            continue
        found += 1
        data = path.read_bytes()
        actual_digest = _sha256(data)
        expected_path, expected_digest = EXPECTED_DDS_SHA256[civilization_type]
        assert expected_path == xml_path
        hashes[actual_digest].append(xml_path)
        digest_matches = actual_digest == expected_digest
        if not digest_matches:
            digest_mismatches.append(
                f"{civilization_type} ({xml_path}): "
                f"sha256={actual_digest}, expected={expected_digest}"
            )
        try:
            pixels = _parse_and_validate_dds(data)
            parsed += 1
            chromatic_pixels = [
                pixel for pixel in pixels if max(pixel) - min(pixel) >= 8
            ]
            unique_chromatic_colors = len(set(chromatic_pixels))
            peak_chroma = max(
                (max(pixel) - min(pixel) for pixel in pixels), default=0
            )
            minimum_chromatic_pixels = (DDS_WIDTH * DDS_HEIGHT + 99) // 100
            if len(chromatic_pixels) < minimum_chromatic_pixels:
                raise AssertionError(
                    f"chromatic pixels={len(chromatic_pixels)}, "
                    f"expected at least {minimum_chromatic_pixels}"
                )
            if unique_chromatic_colors < 8:
                raise AssertionError(
                    f"unique chromatic RGB colors={unique_chromatic_colors}, "
                    "expected at least 8"
                )
            if peak_chroma < 32:
                raise AssertionError(
                    f"peak RGB channel spread={peak_chroma}, expected at least 32"
                )
            if digest_matches:
                valid += 1
        except MipRgbValidationError as error:
            mip_rgb_failures.append(
                f"{civilization_type} ({xml_path}): {error}"
            )
        except (AssertionError, struct.error) as error:
            validation_errors.append(
                f"{civilization_type} ({xml_path}): {error}"
            )

    duplicate_hashes = {
        digest: paths for digest, paths in hashes.items() if len(paths) > 1
    }
    if duplicate_hashes:
        validation_errors.append(f"duplicate SHA-256 groups={duplicate_hashes}")

    assert (
        found == EXPECTED_TOTAL
        and parsed == EXPECTED_TOTAL
        and valid == EXPECTED_TOTAL
        and len(hashes) == EXPECTED_TOTAL
        and not digest_mismatches
        and not mip_rgb_failures
        and not validation_errors
    ), (
        "full-color DDS reconciliation failed: "
        f"expected={EXPECTED_TOTAL}, found={found}, parsed={parsed}, "
        f"valid={valid}, unique_sha256={len(hashes)}, "
        f"missing={EXPECTED_TOTAL - found}, "
        f"digest_mismatch_total={len(digest_mismatches)}, "
        f"mip_rgb_failure_total={len(mip_rgb_failures)}, "
        f"other_validation_error_total={len(validation_errors)}, "
        f"duplicate_total={sum(len(paths) - 1 for paths in duplicate_hashes.values())}; "
        f"digest_mismatches={digest_mismatches}; "
        f"mip_rgb_failures={mip_rgb_failures}; "
        f"other_validation_errors={validation_errors}"
    )
