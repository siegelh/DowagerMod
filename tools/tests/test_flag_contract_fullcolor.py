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
    'CIVILIZATION_AMERICA_FEDERAL': (
        'Art/Interface/TeamColor/FlagDECAL_AmericaFederal.dds',
        '8c8e9846dc377eefb40f52640feedbd7fd4748f0594d13f15258fee5fd2bfba6',
    ),
    'CIVILIZATION_AMERICA_FOUNDING_REPUBLIC': (
        'Art/Interface/TeamColor/FlagDECAL_Star.dds',
        '4261a2177f879578b6b52ef9802268e67057fab5f8a8c4a501b67c4ec3dfd6d4',
    ),
    'CIVILIZATION_AMERICA_NEW_DEAL': (
        'Art/Interface/TeamColor/FlagDECAL_AmericaNewDeal.dds',
        '50a6c9832e4b2c548bbf37b9fae2c4ca638556448754810bd8851eb6f215fb94',
    ),
    'CIVILIZATION_AMERICA_UNION': (
        'Art/Interface/TeamColor/FlagDECAL_AmericaUnion.dds',
        '82dbbb1cf913868f2d0ee6b72e65478bc8c75ac2dac8d0f1ed247bbfcb2d88ae',
    ),
    'CIVILIZATION_APACHE_CONFEDERACY': (
        'Art/Interface/TeamColor/FlagDECAL_Apache.dds',
        'bb5409f083efe8bc1c60fed836dba3764832b5ad2b17bb912948e22ec2630a7b',
    ),
    'CIVILIZATION_ARABIA': (
        'Art/Interface/TeamColor/FlagDECAL_Arabic.dds',
        'f4d8f1a6a39735ac478df7489597137582f9547553ce84a08cb8a5d5657e1d3e',
    ),
    'CIVILIZATION_ATHENIAN_GREECE': (
        'Art/Interface/TeamColor/FlagDECAL_Helmet.dds',
        'd5fb053498c2ebb96f618d9adff4e8fabdadeedabc80688ae1dd10f44edb10cc',
    ),
    'CIVILIZATION_AZTEC': (
        'Art/Interface/TeamColor/FlagDECAL_AztecCalendar.dds',
        '34b5475f9e60e3047d36c60c7def810563750dccc751c59f748c881875f42f71',
    ),
    'CIVILIZATION_BABYLON': (
        'Art/Interface/TeamColor/FlagDECAL_Babylon.dds',
        '9cfc8a2c438dec1ace7b27b66f7e58e5a2dc539bfa28e0635f05a97dd0dd33eb',
    ),
    'CIVILIZATION_BRITISH_REGENCY': (
        'Art/Interface/TeamColor/FlagDECAL_EnglandRegency.dds',
        '8c9c5db44ab67e2d5f2e7e9a1ad494a13555b376d2663ecf62d514ffbdc4fb28',
    ),
    'CIVILIZATION_BYZANTIUM': (
        'Art/Interface/TeamColor/FlagDECAL_Byzantine.dds',
        'e2af98fdb8b0187d152ffdfaeea9c6af80d2d5b726bf797bd4b04724ed7b141f',
    ),
    'CIVILIZATION_CARTHAGE': (
        'Art/Interface/TeamColor/FlagDECAL_Carthage.dds',
        'e9356778a9449fb14c1d45db7d4b5d030f77d1a81825ed7b41f2bd2ef1320dca',
    ),
    'CIVILIZATION_EGYPT_EIGHTEENTH_DYNASTY': (
        'Art/Interface/TeamColor/FlagDECAL_EgyptEighteenthDynasty.dds',
        'a41c5d062938a86f31e4d375e0fbd3ac3acd9ed716a4feea35e501714adb7193',
    ),
    'CIVILIZATION_EGYPT_NEW_KINGDOM': (
        'Art/Interface/TeamColor/FlagDECAL_EyeOfRa.dds',
        '00b53c9586aa76cd61adbc11b23c4e6f55dae77dfc3e686c326417297b35af03',
    ),
    'CIVILIZATION_ELIZABETHAN_ENGLAND': (
        'Art/Interface/TeamColor/FlagDECAL_StGeorgeCross.dds',
        'ea8d4975eb2a0b14bf26abe733f1b02691430c94bd6218c656193b9b42c19f31',
    ),
    'CIVILIZATION_ETHIOPIA_IMPERIAL': (
        'Art/Interface/TeamColor/FlagDECAL_Ethiopia.dds',
        '5f3f684704b552e24341cc1f3e3fe1ca1cf1c8adf9ea4ad27871102b100790fa',
    ),
    'CIVILIZATION_ETHIOPIA_SOLOMONIC': (
        'Art/Interface/TeamColor/FlagDECAL_EthiopiaSolomonic.dds',
        '8667a59df521330be4724aa876d62e44579b4a28f750e7c1baa0c39f1a9b35f9',
    ),
    'CIVILIZATION_FRANCE_BOURBON': (
        'Art/Interface/TeamColor/FlagDECAL_FleurDeLis.dds',
        'a6e525924a0989657ab7a541ece8f74e8d65cda5793a38c3b736468f1222bbe7',
    ),
    'CIVILIZATION_FRANCE_FIFTH_REPUBLIC': (
        'Art/Interface/TeamColor/FlagDECAL_FranceFifthRepublic.dds',
        '43ce8c2b2cdc77eecf0b50036b6d83de57502ddf7365b58c71725fcb39e51f00',
    ),
    'CIVILIZATION_FRANCE_FIRST_EMPIRE': (
        'Art/Interface/TeamColor/FlagDECAL_FranceFirstEmpire.dds',
        '92a8e97a52b96b65cc8859c2db3dd43a05c8004fed005f0bef7fa6456dcdb978',
    ),
    'CIVILIZATION_GAULIC_CONFEDERATION': (
        'Art/Interface/TeamColor/FlagDECAL_Gaul.dds',
        '71556ce077b012b7e7f693721d7bf0dcdda95a0e174fe620073368931a9f865e',
    ),
    'CIVILIZATION_GERMAN_EMPIRE': (
        'Art/Interface/TeamColor/FlagDECAL_GermanEmpire.dds',
        '4d35caf86849791c1a6fe59d2efe0801b010f823fcc611537409cd1a354a41e7',
    ),
    'CIVILIZATION_HOLY_ROMAN': (
        'Art/Interface/TeamColor/FlagDECAL_HolyRomanEmpire.dds',
        '967eb5623b49b7e0634e7a155a09e8cb8edf3ec5f144104b33e214196c1c5896',
    ),
    'CIVILIZATION_ICENI_BRITAIN': (
        'Art/Interface/TeamColor/FlagDECAL_Iceni.dds',
        '32487867b9649b9eb6652ae3673d673d479860de4c519414d8a8f44e8a0dad68',
    ),
    'CIVILIZATION_IMPERIAL_RUSSIA': (
        'Art/Interface/TeamColor/FlagDECAL_DoubleEagle.dds',
        '6b7fefc641d678cf82e4fd387bdae4b7356ad69631181ca7d986016bfd069704',
    ),
    'CIVILIZATION_INCA': (
        'Art/Interface/TeamColor/FlagDECAL_Sun.dds',
        'e176faa26580d58077735a5d9dd7a5ac83fc27e388840838a50bddf48d34dbd9',
    ),
    'CIVILIZATION_INDIA': (
        'Art/Interface/TeamColor/FlagDECAL_IndiaGandhi.dds',
        'e5dc69943d947cb744dcff1967b3059743794627b02d1c7d4db4ccc4add8b959',
    ),
    'CIVILIZATION_JAPAN': (
        'Art/Interface/TeamColor/FlagDECAL_Dot.dds',
        '591904daa3953e182d05ffcdf48e3d23e5c9c76c6466cd1487fda0102d22d0f6',
    ),
    'CIVILIZATION_KHMER': (
        'Art/Interface/TeamColor/FlagDECAL_Khmer.dds',
        '45dbf928cdf720524b0042a7fa4097e2b25fb50d29c3db4a787382841f582ccd',
    ),
    'CIVILIZATION_KOREA': (
        'Art/Interface/TeamColor/FlagDECAL_KoreanSymbol.dds',
        'fd568460dd3edfbdbec82b7382bb017955f1978fc51dbc7d12b40e45ffe065d6',
    ),
    'CIVILIZATION_MACEDONIAN_EMPIRE': (
        'Art/Interface/TeamColor/FlagDECAL_Macedon.dds',
        '68c8025729c1d8e02e198da7dc3f85dd0e5421b96d2bc8d7c5cd8f500dfdbebf',
    ),
    'CIVILIZATION_MALI': (
        'Art/Interface/TeamColor/FlagDECAL_Mask.dds',
        '246a15f631603649e1b34560b4d09d0fceae6a5af4a3f5c1572b6e75f6884387',
    ),
    'CIVILIZATION_MAURYA': (
        'Art/Interface/TeamColor/FlagDECAL_WheelOfLaw.dds',
        '4b7f4b5694b7a73e541692ba24f51b9f5d214d01f81e5e1d7e416bb33de96767',
    ),
    'CIVILIZATION_MAYA': (
        'Art/Interface/TeamColor/FlagDECAL_Maya.dds',
        '58c09dad3691cf46edbac0d3ca814d2de990bb35e39baf1a0368c1c8de6c1b6d',
    ),
    'CIVILIZATION_MONGOL_EMPIRE': (
        'Art/Interface/TeamColor/FlagDECAL_Horse.dds',
        'b3ab5dec4e6ae56640e6711ef7aec6236bb0876ecbbc761c2cf4d584dcfae40e',
    ),
    'CIVILIZATION_NATIVE_AMERICA': (
        'Art/Interface/TeamColor/FlagDECAL_NativeAmerica.dds',
        '598140035f7d4b9b2bec3e17d4c225dd011920697d54eb1680d6dd44afd3f90c',
    ),
    'CIVILIZATION_NETHERLANDS': (
        'Art/Interface/TeamColor/FlagDECAL_Netherlands.dds',
        '9cad6e2637290ce365fa22ead4aaaabf6a73174f9fd81f3ce95fbc5d484010e4',
    ),
    'CIVILIZATION_OTTOMAN_CLASSICAL': (
        'Art/Interface/TeamColor/FlagDECAL_OttomanClassical.dds',
        'c798ecc0748278212b93104b53440a7804e088cc2270c70836733bd2ff9d2f86',
    ),
    'CIVILIZATION_OTTOMAN_CONQUEST': (
        'Art/Interface/TeamColor/FlagDECAL_Ottoman.dds',
        '43903c93558fa55f7556365447df84cd7b73bd7a21c2d88d06d76d13c3d6d581',
    ),
    'CIVILIZATION_PEOPLES_REPUBLIC_CHINA': (
        'Art/BTG/Civilization/PRC/flagdecal_prc.dds',
        'cbb777c1131bfcac5534742ca0d5a5aa7567b89d236bcddb3b7ef7c31c4bf3df',
    ),
    'CIVILIZATION_PERSIA_FOUNDING_ACHAEMENID': (
        'Art/Interface/TeamColor/FlagDECAL_PersiaFounding.dds',
        'f7599b312417c0cb802bf8e1b67a8c48c3e43d194d29f8dfc0a4a9bd308efaeb',
    ),
    'CIVILIZATION_PERSIA_IMPERIAL_ACHAEMENID': (
        'Art/Interface/TeamColor/FlagDECAL_PersiaImperial.dds',
        '924ecfca49b0e5c9e28bafe1325705189864ac1eda1e136913fb41a49993bebc',
    ),
    'CIVILIZATION_PETRINE_RUSSIA': (
        'Art/Interface/TeamColor/FlagDECAL_RussiaPetrine.dds',
        '2447b2276892fbcd1a8812e76bfcaa208b640065f579c397659d0245a900319c',
    ),
    'CIVILIZATION_POLAND': (
        'Art/Interface/TeamColor/FlagDECAL_Poland.dds',
        'e95b22d3e2e056272611906e772cf018f1930133e9d3754b663c518f0f7178e0',
    ),
    'CIVILIZATION_POLYNESIA_BTG': (
        'Art/BTG/Polynesia/flagdecal_polynesia.dds',
        '707b6b902b1cd4bec847c1c9405c4dd9a06a26f79ef50b8f93770dd4068443f8',
    ),
    'CIVILIZATION_PORTUGAL': (
        'Art/Interface/TeamColor/FlagDECAL_Portugal.dds',
        '414ecd5d1cd21a0539fcbf3d6ac9445f6b1ebd9b9383aca4ecc9033ebf17a871',
    ),
    'CIVILIZATION_PRUSSIA': (
        'Art/Interface/TeamColor/FlagDECAL_Prussia.dds',
        'ef1928dd1d5e366857ad5494ac6a8c1e530623007b334d8b2e38c6d9123d1f8d',
    ),
    'CIVILIZATION_QIN_DYNASTY': (
        'Art/Interface/TeamColor/FlagDECAL_Dragon.dds',
        '8f610c075fac6f0d9eaabc42db2c6a822d80f5732bca5c45cc1e4fb6bc063c4f',
    ),
    'CIVILIZATION_ROMAN_PRINCIPATE': (
        'Art/Interface/TeamColor/FlagDECAL_Laurels.dds',
        'd95fd5376cd0701ff91792a19bfbd2392225a6f8bfa0da1f72a1fe51733d1561',
    ),
    'CIVILIZATION_ROMAN_REPUBLIC_LATE': (
        'Art/Interface/TeamColor/FlagDECAL_RomanRepublic.dds',
        'b44b2d885c4e585caa63a6cf0bc62eabf9f480636653bd17cf124e6bbaacdfa0',
    ),
    'CIVILIZATION_SPAIN': (
        'Art/Interface/TeamColor/FlagDECAL_Castle.dds',
        '47ff6c48426a5c4166757c4ea31d7a0c45b40c6bed0ce88058aaa02623041d11',
    ),
    'CIVILIZATION_SUMERIA': (
        'Art/Interface/TeamColor/FlagDECAL_Sumeria.dds',
        '74174ae5cbd3b7411e72a82d6448ba703fbebeea54c97aee6c66be7b12910f80',
    ),
    'CIVILIZATION_USSR': (
        'Art/Interface/TeamColor/FlagDECAL_RussiaUSSR.dds',
        'd80cdba646d2a5c0feef7bc6e9d21fedda71a21448deb59d5bc8375493d02ee3',
    ),
    'CIVILIZATION_VENICE': (
        'Art/BTG/Civilization/Venice/flagdecal_venice.dds',
        'fb325c4fe24ed33fc197bf43560319843c72e641c79af73bc59a007c089c66ed',
    ),
    'CIVILIZATION_VICTORIAN_BRITAIN': (
        'Art/Interface/TeamColor/FlagDECAL_EnglandVictorian.dds',
        '6b143f9f21bf75392975ec8e431322030216d909b5681d1fb3b9615f3b448be1',
    ),
    'CIVILIZATION_VIKING': (
        'Art/Interface/TeamColor/FlagDECAL_Viking.dds',
        'd98a513a5786ca1d552d56fcb69ba437b5952eff7d90e6b0029a14479629b9e1',
    ),
    'CIVILIZATION_WARTIME_BRITAIN': (
        'Art/Interface/TeamColor/FlagDECAL_EnglandWartime.dds',
        '1a836fc612fe437695e55ac27d47656b9b08a73bc7a9cb51f9a28a30be64d77e',
    ),
    'CIVILIZATION_YUAN_DYNASTY': (
        'Art/Interface/TeamColor/FlagDECAL_Yuan.dds',
        '68e66df556b2bd88f31a57ea6046ebcf931f6b5530cf00150f114b3616b7cebf',
    ),
    'CIVILIZATION_ZULU': (
        'Art/Interface/TeamColor/FlagDECAL_ZuluShield.dds',
        '5cf870803e94784c9fdc055a5648b8b05c4af0f05d6bfe4b14b984dede2776da',
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
            _parse_and_validate_dds(data)
            parsed += 1
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


def test_maya_flag_has_visible_rgb_contrast() -> None:
    _, relative_path = FULLCOLOR_FLAGS["CIVILIZATION_MAYA"]
    pixels = _parse_and_validate_dds(_asset_path(relative_path).read_bytes())
    assert len(set(pixels)) > 1
    assert any(pixel != (0, 0, 0) for pixel in pixels)
