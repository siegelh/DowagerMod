## Local GameFont/glyph diagnostics for multiplayer rendering issues.
##
## This module is intentionally read-only: it writes local logs and never
## changes game state, RNG state, network state, units, cities, or script data.

from CvPythonExtensions import *
import CvUtil
import os
import sys
import time


gc = CyGlobalContext()


try:
	_range = xrange
except NameError:
	_range = range

try:
	_unicode = unicode
except NameError:
	_unicode = str

try:
	_unichr = unichr
except NameError:
	_unichr = chr


DIAGNOSTIC_VERSION = "1"
PAD_AMOUNT = 25

FONT_FILE_NAMES = [
	"GameFont.tga",
	"GameFont_75.tga",
]

YIELD_INFO_FALLBACK_COUNT = 3
COMMERCE_INFO_FALLBACK_COUNT = 4

GENERIC_SYMBOLS = [
	("HAPPY_CHAR", 0),
	("UNHAPPY_CHAR", 1),
	("HEALTHY_CHAR", 2),
	("UNHEALTHY_CHAR", 3),
	("BULLET_CHAR", 4),
	("STRENGTH_CHAR", 5),
	("MOVES_CHAR", 6),
	("RELIGION_CHAR", 7),
	("STAR_CHAR", 8),
	("SILVER_STAR_CHAR", 9),
	("TRADE_CHAR", 10),
	("DEFENSE_CHAR", 11),
	("GREAT_PEOPLE_CHAR", 12),
	("BAD_GOLD_CHAR", 13),
	("BAD_FOOD_CHAR", 14),
	("EATEN_FOOD_CHAR", 15),
	("GOLDEN_AGE_CHAR", 16),
	("ANGRY_POP_CHAR", 17),
	("OPEN_BORDERS_CHAR", 18),
	("DEFENSIVE_PACT_CHAR", 19),
	("MAP_CHAR", 20),
	("OCCUPATION_CHAR", 21),
	("POWER_CHAR", 22),
]

HIGH_RISK_BONUS_TYPE_PARTS = [
	"GOLD",
	"SPICE",
	"SPICES",
	"REFIN",
	"ART",
	"MASTERPIECE",
]


def dumpGlyphDiagnostics(mx=-1, my=-1, px=-1, py=-1, source="hotkey"):
	"""Write a local glyph diagnostic dump and return the file path or empty string."""
	lines = []
	try:
		dump_id = _build_dump_id()
		_append_diagnostic_metadata(lines, dump_id, source, mx, my, px, py)
		_append_file_fingerprints(lines)
		_append_user_data_state(lines)
		_append_trigger_context(lines, mx, my, px, py)
		_append_runtime_symbols(lines)
		_append_allocation_analysis(lines)
		_append_player_context(lines, px, py)
		_append_city_religion_expectations(lines, px, py)
		_append_probe_strings(lines)
		_append_diagnosis_summary(lines)
		lines.append(u"=== DowagerMod GlyphDiagnostics END ===")

		path = _write_dedicated_log(dump_id, lines)
		if path:
			_show_visible_probes()
			_notify(u"Glyph diagnostics written: %s" % path)
			CvUtil.pyPrint("GlyphDiagnostics wrote %s" % _to_printable(path))
			return path

		_write_python_dbg_fallback(lines)
		_show_visible_probes()
		_notify(u"Glyph diagnostics written to PythonDbg.log")
		CvUtil.pyPrint("GlyphDiagnostics wrote fallback PythonDbg.log block")
		return "PythonDbg.log"

	except Exception:
		CvUtil.pyPrint("GlyphDiagnostics ERROR: %s" % _to_printable(_exception_text()))
		_notify(u"Glyph diagnostics failed; see PythonDbg.log")
		return ""


def _build_dump_id():
	game = gc.getGame()
	i_turn = _safe_int(lambda: game.getGameTurn(), -1)
	i_player = _safe_int(lambda: game.getActivePlayer(), -1)
	player_label = _player_file_label(i_player)
	stamp = time.strftime("%Y%m%d-%H%M%S")
	return "GlyphDiagnostics_Turn%03d_Player%02d_%s_%s" % (i_turn, i_player, player_label, stamp)


def _player_file_label(i_player):
	if i_player < 0:
		return "NoActivePlayer"
	try:
		player = gc.getPlayer(i_player)
		leader = _safe_value(lambda: gc.getLeaderHeadInfo(player.getLeaderType()).getDescription())
		civ = _safe_value(lambda: gc.getCivilizationInfo(player.getCivilizationType()).getDescription())
		return _filename_token(u"%s_%s" % (leader, civ))
	except Exception:
		return "Player%02d" % i_player


def _filename_token(value):
	text = _to_unicode(value)
	result = []
	last_was_sep = False
	for ch in text:
		if (ch >= u"A" and ch <= u"Z") or (ch >= u"a" and ch <= u"z") or (ch >= u"0" and ch <= u"9"):
			result.append(ch)
			last_was_sep = False
		else:
			if not last_was_sep:
				result.append(u"_")
				last_was_sep = True
	token = u"".join(result).strip(u"_")
	if not token:
		token = u"UnknownPlayer"
	if len(token) > 80:
		token = token[:80].rstrip(u"_")
	return _to_ascii(token)


def _to_ascii(value):
	text = _to_unicode(value)
	try:
		encoded = text.encode("ascii", "ignore")
		try:
			return encoded.decode("ascii")
		except AttributeError:
			return encoded
	except Exception:
		return "UnknownPlayer"


def _append_diagnostic_metadata(lines, dump_id, source, mx, my, px, py):
	game = gc.getGame()
	i_player = _safe_int(lambda: game.getActivePlayer(), -1)
	lines.append(u"=== DowagerMod GlyphDiagnostics BEGIN ===")
	lines.append(u"[diagnostic_metadata]")
	lines.append(_kv(u"version", DIAGNOSTIC_VERSION))
	lines.append(_kv(u"dump_id", dump_id))
	lines.append(_kv(u"source", source))
	lines.append(_kv(u"local_time", time.strftime("%Y-%m-%d %H:%M:%S")))
	lines.append(_kv(u"game_turn", _safe_value(lambda: game.getGameTurn())))
	lines.append(_kv(u"game_year", _safe_value(lambda: game.getGameTurnYear())))
	lines.append(_kv(u"is_network_multiplayer", _safe_value(lambda: game.isNetworkMultiPlayer())))
	lines.append(_kv(u"active_player", i_player))
	lines.append(_kv(u"mouse_screen_xy", u"%s,%s" % (mx, my)))
	lines.append(_kv(u"mouse_plot_xy", u"%s,%s" % (px, py)))
	lines.append(_kv(u"cwd", _safe_value(lambda: os.getcwd())))
	lines.append(_kv(u"diagnostic_module_path", _safe_value(lambda: os.path.abspath(__file__))))
	lines.append(_kv(u"localappdata", os.environ.get("LOCALAPPDATA", "")))
	lines.append(_kv(u"userprofile", os.environ.get("USERPROFILE", "")))
	lines.append(_kv(u"onedrive", os.environ.get("OneDrive", "")))
	lines.append(_kv(u"onedrive_commercial", os.environ.get("OneDriveCommercial", "")))
	lines.append(_kv(u"onedrive_consumer", os.environ.get("OneDriveConsumer", "")))

	if i_player >= 0:
		player = gc.getPlayer(i_player)
		lines.append(_kv(u"active_player_name", _safe_value(lambda: player.getNameKey())))
		lines.append(_kv(u"active_player_civ_type", _info_type(lambda: gc.getCivilizationInfo(player.getCivilizationType()))))
		lines.append(_kv(u"active_player_civ_description", _safe_value(lambda: player.getCivilizationDescription(0))))
		lines.append(_kv(u"active_player_leader_type", _info_type(lambda: gc.getLeaderHeadInfo(player.getLeaderType()))))
		lines.append(_kv(u"active_player_team", _safe_value(lambda: player.getTeam())))
		lines.append(_kv(u"active_player_state_religion", _religion_name(_safe_int(lambda: player.getStateReligion(), -1))))

	lines.append(u"[python_path]")
	for index, path in enumerate(sys.path):
		lines.append(_join_fields([u"SYS_PATH", index, path]))


def _append_file_fingerprints(lines):
	lines.append(u"[file_fingerprints]")
	assets_dir = _assets_dir()
	base_assets_dir = _base_assets_dir()
	paths = []
	for file_name in FONT_FILE_NAMES:
		paths.append((u"FONT", file_name, _first_existing_font_path(_font_file_candidates(), file_name)))
	paths.extend([
		(u"PYTHON", u"CvGlyphDiagnostics.py", os.path.abspath(__file__)),
		(u"PYTHON", u"CvEventManager.py", os.path.join(assets_dir, "Python", "CvEventManager.py")),
		(u"DLL", u"CvGameCoreDLL.dll", os.path.join(assets_dir, "CvGameCoreDLL.dll")),
		(u"XML", u"CIV4BonusInfos.xml", _find_asset_file([assets_dir, base_assets_dir], os.path.join("XML", "Terrain", "CIV4BonusInfos.xml"))),
		(u"XML", u"CIV4ArtDefines_Bonus.xml", _find_asset_file([assets_dir, base_assets_dir], os.path.join("XML", "Art", "CIV4ArtDefines_Bonus.xml"))),
		(u"XML", u"CIV4ReligionInfo.xml", _find_asset_file([assets_dir, base_assets_dir], os.path.join("XML", "GameInfo", "CIV4ReligionInfo.xml"))),
		(u"XML", u"CIV4CorporationInfo.xml", _find_asset_file([assets_dir, base_assets_dir], os.path.join("XML", "GameInfo", "CIV4CorporationInfo.xml"))),
		(u"XML", u"CIV4CommerceInfo.xml", _find_asset_file([assets_dir, base_assets_dir], os.path.join("XML", "GameInfo", "CIV4CommerceInfo.xml"))),
		(u"XML", u"CIV4YieldInfos.xml", _find_asset_file([assets_dir, base_assets_dir], os.path.join("XML", "Terrain", "CIV4YieldInfos.xml"))),
	])
	for family, label, path in paths:
		_append_one_file_fingerprint(lines, family, label, path)


def _append_one_file_fingerprint(lines, family, label, path):
	if not path:
		lines.append(_join_fields([u"FILE", family, label, u"path=<not found>", u"exists=False", u"size=<missing>", u"mtime=<missing>", u"md5=<missing>"]))
		return
	fields = [u"FILE", family, label, u"path=%s" % path, u"exists=%s" % os.path.isfile(path), _file_size_text(path), _file_mtime_text(path), _file_md5_text(path)]
	if label in FONT_FILE_NAMES:
		fields.append(_tga_header_text(path))
	lines.append(_join_fields(fields))


def _assets_dir():
	try:
		return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	except Exception:
		return ""


def _base_assets_dir():
	try:
		assets_dir = _assets_dir()
		return os.path.normpath(os.path.join(assets_dir, "..", "..", "Assets"))
	except Exception:
		return ""


def _find_asset_file(asset_dirs, relative_path):
	for asset_dir in asset_dirs:
		if not asset_dir:
			continue
		path = os.path.join(asset_dir, relative_path)
		if os.path.isfile(path):
			return path
	return ""


def _font_file_candidates():
	candidates = []
	try:
		module_dir = os.path.dirname(os.path.abspath(__file__))
		assets_dir = os.path.dirname(module_dir)
		candidates.append(os.path.join(assets_dir, "res", "Fonts"))
	except Exception:
		pass

	try:
		cwd = os.getcwd()
		candidates.append(os.path.join(cwd, "Beyond the Sword", "Assets", "res", "Fonts"))
		candidates.append(os.path.join(cwd, "Assets", "res", "Fonts"))
		candidates.append(os.path.join(cwd, "res", "Fonts"))
	except Exception:
		pass

	return candidates


def _first_existing_font_path(font_dirs, file_name):
	for font_dir in font_dirs:
		path = os.path.join(font_dir, file_name)
		if os.path.isfile(path):
			return path
	return ""


def _append_user_data_state(lines):
	lines.append(u"[user_data_state]")
	candidates = _my_games_candidates()
	for index, path in enumerate(candidates):
		lines.append(_join_fields([u"MY_GAMES_CANDIDATE", index, path, u"exists=%s" % os.path.isdir(path)]))
	user_data = _first_existing_dir(candidates)
	lines.append(_kv(u"selected_my_games_path", user_data if user_data else u"<not found>"))
	if user_data:
		ini = os.path.join(user_data, "CivilizationIV.ini")
		cache_dir = os.path.join(user_data, "cache")
		lines.append(_join_fields([u"INI", ini, u"exists=%s" % os.path.isfile(ini), u"DisableCaching=%s" % _read_disable_caching(ini)]))
		lines.append(_join_fields([u"CACHE_DIR", cache_dir, u"exists=%s" % os.path.isdir(cache_dir)]))
		try:
			for name in sorted(os.listdir(user_data)):
				path = os.path.join(user_data, name)
				kind = u"dir" if os.path.isdir(path) else u"file"
				lines.append(_join_fields([u"MY_GAMES_ENTRY", name, kind]))
		except Exception:
			lines.append(_join_fields([u"MY_GAMES_LIST_ERROR", _exception_text()]))
	lines.append(_kv(u"glyph_output_dir", _preferred_log_dir()))


def _my_games_candidates():
	candidates = []
	user_profile = os.environ.get("USERPROFILE", "")
	if user_profile:
		_append_onedrive_my_games_candidates(candidates, user_profile)
		candidates.append(os.path.join(user_profile, "Documents", "My Games", "Beyond the Sword"))
		candidates.append(os.path.join(user_profile, "Documents", "My Games", "beyond the sword"))
	for key in ["OneDriveCommercial", "OneDriveConsumer", "OneDrive"]:
		root = os.environ.get(key, "")
		if root:
			candidates.append(os.path.join(root, "Documents", "My Games", "Beyond the Sword"))
			candidates.append(os.path.join(root, "Documents", "My Games", "beyond the sword"))
	return _dedupe(candidates)


def _append_onedrive_my_games_candidates(candidates, user_profile):
	try:
		for name in os.listdir(user_profile):
			if name.lower().startswith("onedrive"):
				root = os.path.join(user_profile, name)
				candidates.append(os.path.join(root, "Documents", "My Games", "Beyond the Sword"))
				candidates.append(os.path.join(root, "Documents", "My Games", "beyond the sword"))
	except Exception:
		pass


def _append_trigger_context(lines, mx, my, px, py):
	lines.append(u"[trigger_context]")
	lines.append(_kv(u"mouse_screen_xy", u"%s,%s" % (mx, my)))
	lines.append(_kv(u"mouse_plot_xy", u"%s,%s" % (px, py)))
	game = gc.getGame()
	i_active_player = _safe_int(lambda: game.getActivePlayer(), -1)
	player = gc.getPlayer(i_active_player) if i_active_player >= 0 else None
	_append_plot_context(lines, u"TRIGGER_PLOT", px, py, player)
	lines.append(_kv(u"active_screen", _safe_value(lambda: CyInterface().getShowInterface())))
	lines.append(_kv(u"selected_unit", _selected_unit_summary()))


def _append_plot_context(lines, label, px, py, player):
	try:
		px = int(px)
		py = int(py)
	except Exception:
		lines.append(_join_fields([label, u"available=False"]))
		return
	if px < 0 or py < 0:
		lines.append(_join_fields([label, u"available=False"]))
		return
	try:
		plot = CyMap().plot(px, py)
		i_team = _safe_int(lambda: player.getTeam(), -1) if player else -1
		i_owner = _safe_int(lambda: plot.getOwner(), -1)
		i_bonus = _safe_int(lambda: plot.getBonusType(i_team), -1)
		fields = [
			label,
			u"x=%s" % _safe_value(lambda: plot.getX()),
			u"y=%s" % _safe_value(lambda: plot.getY()),
			u"owner=%s" % _player_label(i_owner),
			u"is_city=%s" % _safe_value(lambda: plot.isCity()),
			u"bonus=%s" % _bonus_name(i_bonus),
		]
		if _safe_bool(lambda: plot.isCity(), False):
			city = plot.getPlotCity()
			if city and not city.isNone():
				fields.append(u"city=%s" % _safe_value(lambda: city.getName()))
				fields.append(u"city_owner=%s" % _player_label(_safe_int(lambda: city.getOwner(), -1)))
				fields.append(u"city_religion_markers=%s" % _city_religion_marker_string(city))
		lines.append(_join_fields(fields))
	except Exception:
		lines.append(_join_fields([label, u"error=%s" % _exception_text()]))


def _append_runtime_symbols(lines):
	lines.append(u"[runtime_symbols]")
	_append_info_chars(lines, u"YIELD", _info_count(lambda: gc.getNumYieldInfos(), YIELD_INFO_FALLBACK_COUNT), lambda i: gc.getYieldInfo(i), ["getChar"])
	_append_info_chars(lines, u"COMMERCE", _info_count(lambda: gc.getNumCommerceInfos(), COMMERCE_INFO_FALLBACK_COUNT), lambda i: gc.getCommerceInfo(i), ["getChar"])
	_append_info_chars(lines, u"RELIGION", _safe_int(lambda: gc.getNumReligionInfos(), 0), lambda i: gc.getReligionInfo(i), ["getChar", "getHolyCityChar"])
	_append_info_chars(lines, u"CORPORATION", _safe_int(lambda: gc.getNumCorporationInfos(), 0), lambda i: gc.getCorporationInfo(i), ["getChar", "getHeadquarterChar"])
	_append_info_chars(lines, u"BONUS", _safe_int(lambda: gc.getNumBonusInfos(), 0), lambda i: gc.getBonusInfo(i), ["getChar"])
	_append_generic_symbols(lines)


def _append_info_chars(lines, family, count, info_getter, char_methods):
	for i in _range(count):
		info = _safe_info(lambda: info_getter(i))
		if info is None:
			lines.append(_join_fields([family, i, u"<missing info>"]))
			continue
		fields = [family, i, _info_type_from_info(info), _safe_value(lambda: info.getDescription())]
		for method_name in char_methods:
			fields.append(_char_method_field(info, method_name))
		lines.append(_join_fields(fields))


def _append_generic_symbols(lines):
	game = gc.getGame()
	for symbol_name, symbol_enum in GENERIC_SYMBOLS:
		code = _safe_int(lambda: game.getSymbolID(symbol_enum), -1)
		lines.append(_join_fields([u"GENERIC_SYMBOL", symbol_name, _char_field(u"getSymbolID", code)]))


def _append_allocation_analysis(lines):
	lines.append(u"[allocation_analysis]")
	model = _build_allocation_model()
	for key in sorted(model.keys()):
		lines.append(_kv(key, model[key]))
	_append_duplicate_bonus_groups(lines)


def _build_allocation_model():
	yield_count = _info_count(lambda: gc.getNumYieldInfos(), YIELD_INFO_FALLBACK_COUNT)
	commerce_count = _info_count(lambda: gc.getNumCommerceInfos(), COMMERCE_INFO_FALLBACK_COUNT)
	religion_count = _safe_int(lambda: gc.getNumReligionInfos(), 0)
	corporation_count = _safe_int(lambda: gc.getNumCorporationInfos(), 0)
	bonus_count = _safe_int(lambda: gc.getNumBonusInfos(), 0)
	first_symbol = _safe_int(lambda: gc.getYieldInfo(0).getChar(), 8483)
	current = first_symbol
	current += yield_count
	current = _pad_to_next(current)
	current += commerce_count
	current = _pad_to_next(current)
	if commerce_count < PAD_AMOUNT:
		current = _pad_to_next(current)
	current += 2 * religion_count
	current += 2 * corporation_count
	current = _pad_to_next(current)
	if 2 * (religion_count + corporation_count) < PAD_AMOUNT:
		current = _pad_to_next(current)
	bonus_base = current
	current += 1
	art_count = 0
	non_art_count = 0
	max_bonus_char = -1
	distinct_bonus_chars = {}
	for i in _range(bonus_count):
		info = gc.getBonusInfo(i)
		bonus_type = _info_type_from_info(info)
		code = _safe_int(lambda info=info: info.getChar(), -1)
		distinct_bonus_chars[code] = 1
		if code > max_bonus_char:
			max_bonus_char = code
		if _is_art_masterpiece_type(bonus_type):
			art_count += 1
		else:
			non_art_count += 1
			current += 1
	current = _pad_to_next(current)
	if bonus_count < PAD_AMOUNT:
		current = _pad_to_next(current)
	if bonus_count < 2 * PAD_AMOUNT:
		current = _pad_to_next(current)
	live_generic_start = _safe_int(lambda: gc.getGame().getSymbolID(0), -1)
	next_boundary = _next_boundary((bonus_base + 1 + non_art_count), PAD_AMOUNT)
	model = {
		u"first_symbol_code": first_symbol,
		u"pad_amount": PAD_AMOUNT,
		u"yield_count": yield_count,
		u"commerce_count": commerce_count,
		u"religion_count": religion_count,
		u"corporation_count": corporation_count,
		u"bonus_count": bonus_count,
		u"art_masterpiece_bonus_count": art_count,
		u"non_art_slot_consuming_bonus_count": non_art_count,
		u"distinct_bonus_char_count": len(distinct_bonus_chars.keys()),
		u"bonus_base_id": bonus_base,
		u"max_bonus_char": max_bonus_char,
		u"modeled_first_generic_symbol_id": current,
		u"live_first_generic_symbol_id": live_generic_start,
		u"generic_symbol_start_matches_model": (current == live_generic_start),
		u"non_art_bonus_count_to_next_padding_boundary": max(0, next_boundary - (bonus_base + 1 + non_art_count)),
		u"generic_shift_risk": _generic_shift_risk(non_art_count),
	}
	return model


def _append_duplicate_bonus_groups(lines):
	by_char = {}
	by_index = {}
	bonus_count = _safe_int(lambda: gc.getNumBonusInfos(), 0)
	bonus_base = _safe_int(lambda: gc.getBonusInfo(0).getChar(), 8600)
	for i in _range(bonus_count):
		info = gc.getBonusInfo(i)
		bonus_type = _info_type_from_info(info)
		code = _safe_int(lambda info=info: info.getChar(), -1)
		index = code - bonus_base if code >= 0 else -1
		by_char.setdefault(code, []).append(bonus_type)
		by_index.setdefault(index, []).append(bonus_type)
	for code in sorted(by_char.keys()):
		items = by_char[code]
		if len(items) > 1:
			lines.append(_join_fields([u"DUPLICATE_CHAR_CODE", code, u"count=%d" % len(items), _compact_list(items)]))
	for index in sorted(by_index.keys()):
		items = by_index[index]
		if len(items) > 1:
			label = u"ART_MASTERPIECE_SHARED_SLOT" if index == 5 and _all_art_masterpieces(items) else u"DUPLICATE_FONT_INDEX"
			lines.append(_join_fields([label, index, u"count=%d" % len(items), _compact_list(items)]))


def _append_player_context(lines, px, py):
	lines.append(u"[active_player_context]")
	game = gc.getGame()
	i_player = _safe_int(lambda: game.getActivePlayer(), -1)
	if i_player < 0:
		lines.append(u"NO_ACTIVE_PLAYER")
		return

	player = gc.getPlayer(i_player)
	_append_available_bonuses(lines, player)
	_append_city_context(lines, player, i_player)
	_append_mouse_plot_context(lines, px, py, player)


def _append_available_bonuses(lines, player):
	lines.append(u"[active_player_available_bonuses]")
	count = _safe_int(lambda: gc.getNumBonusInfos(), 0)
	for i in _range(count):
		available = _safe_int(lambda i=i: player.getNumAvailableBonuses(i), 0)
		if available > 0 or _is_high_risk_bonus(i):
			info = gc.getBonusInfo(i)
			lines.append(_join_fields([u"PLAYER_BONUS", i, _info_type_from_info(info), u"available=%d" % available, _char_method_field(info, "getChar")]))


def _append_city_context(lines, player, i_player):
	lines.append(u"[active_player_cities]")
	try:
		city, iter_city = player.firstCity(False)
		guard = 0
		while city and not city.isNone() and guard < 512:
			_append_one_city(lines, city, i_player)
			city, iter_city = player.nextCity(iter_city, False)
			guard += 1
	except Exception:
		lines.append(_join_fields([u"CITY_CONTEXT_ERROR", _exception_text()]))


def _append_one_city(lines, city, i_player):
	religions = _city_religions(city)
	corporations = _city_corporations(city)
	bonuses = _city_bonuses(city)
	lines.append(_join_fields([
		u"CITY",
		_safe_value(lambda: city.getName()),
		u"x=%s" % _safe_value(lambda: city.getX()),
		u"y=%s" % _safe_value(lambda: city.getY()),
		u"connected_to_capital=%s" % _safe_value(lambda: city.isConnectedToCapital(i_player)),
		u"religions=%s" % _join_list(religions),
		u"corporations=%s" % _join_list(corporations),
		u"bonuses=%s" % _join_list(bonuses),
	]))


def _append_city_religion_expectations(lines, px, py):
	lines.append(u"[city_religion_expectations]")
	seen = {}
	_append_human_city_religion_expectations(lines, seen)
	_append_mouse_city_religion_expectation(lines, px, py, seen)


def _append_human_city_religion_expectations(lines, seen):
	max_players = _safe_int(lambda: gc.getMAX_PLAYERS(), 0)
	for i_player in _range(max_players):
		player = _safe_info(lambda i_player=i_player: gc.getPlayer(i_player))
		if player is None:
			continue
		if not _safe_bool(lambda player=player: player.isAlive(), False):
			continue
		if not _safe_bool(lambda player=player: player.isHuman(), False):
			continue
		try:
			city, iter_city = player.firstCity(False)
			guard = 0
			while city and not city.isNone() and guard < 512:
				_append_city_religion_expectation(lines, city, i_player, u"HUMAN_CITY", seen)
				city, iter_city = player.nextCity(iter_city, False)
				guard += 1
		except Exception:
			lines.append(_join_fields([u"CITY_RELIGION_EXPECTATION_ERROR", _player_label(i_player), _exception_text()]))


def _append_mouse_city_religion_expectation(lines, px, py, seen):
	try:
		px = int(px)
		py = int(py)
	except Exception:
		return
	if px < 0 or py < 0:
		return
	try:
		plot = CyMap().plot(px, py)
		if plot and _safe_bool(lambda: plot.isCity(), False):
			city = plot.getPlotCity()
			if city and not city.isNone():
				_append_city_religion_expectation(lines, city, _safe_int(lambda: city.getOwner(), -1), u"MOUSE_CITY", seen)
	except Exception:
		lines.append(_join_fields([u"MOUSE_CITY_RELIGION_EXPECTATION_ERROR", _exception_text()]))


def _append_city_religion_expectation(lines, city, i_player, source, seen):
	key = u"%s:%s:%s" % (_safe_value(lambda: city.getOwner()), _safe_value(lambda: city.getX()), _safe_value(lambda: city.getY()))
	if seen.has_key(key):
		return
	seen[key] = 1
	lines.append(_join_fields([
		u"CITY_RELIGION_EXPECTATION",
		source,
		u"owner=%s" % _player_label(i_player),
		u"city=%s" % _safe_value(lambda: city.getName()),
		u"x=%s" % _safe_value(lambda: city.getX()),
		u"y=%s" % _safe_value(lambda: city.getY()),
		u"markers=%s" % _city_religion_marker_string(city),
	]))


def _append_mouse_plot_context(lines, px, py, player):
	lines.append(u"[mouse_plot_context]")
	try:
		px = int(px)
		py = int(py)
	except Exception:
		lines.append(u"MOUSE_PLOT unavailable")
		return

	if px < 0 or py < 0:
		lines.append(u"MOUSE_PLOT unavailable")
		return

	try:
		plot = CyMap().plot(px, py)
		if plot is None:
			lines.append(u"MOUSE_PLOT unavailable")
			return
		i_team = _safe_int(lambda: player.getTeam(), -1)
		i_bonus = _safe_int(lambda: plot.getBonusType(i_team), -1)
		fields = [
			u"MOUSE_PLOT",
			u"x=%s" % _safe_value(lambda: plot.getX()),
			u"y=%s" % _safe_value(lambda: plot.getY()),
			u"is_city=%s" % _safe_value(lambda: plot.isCity()),
			u"bonus=%s" % _bonus_name(i_bonus),
		]
		if _safe_bool(lambda: plot.isCity(), False):
			city = plot.getPlotCity()
			if city and not city.isNone():
				fields.append(u"city=%s" % _safe_value(lambda: city.getName()))
				fields.append(u"city_religions=%s" % _join_list(_city_religions(city)))
				fields.append(u"city_corporations=%s" % _join_list(_city_corporations(city)))
		lines.append(_join_fields(fields))
	except Exception:
		lines.append(_join_fields([u"MOUSE_PLOT_ERROR", _exception_text()]))


def _append_probe_strings(lines):
	lines.append(u"[glyph_probe_strings]")
	_append_probe_for_family(lines, u"PROBE_YIELD", _info_count(lambda: gc.getNumYieldInfos(), YIELD_INFO_FALLBACK_COUNT), lambda i: gc.getYieldInfo(i), "getChar")
	_append_probe_for_family(lines, u"PROBE_COMMERCE", _info_count(lambda: gc.getNumCommerceInfos(), COMMERCE_INFO_FALLBACK_COUNT), lambda i: gc.getCommerceInfo(i), "getChar")
	_append_probe_for_family(lines, u"PROBE_RELIGION", _safe_int(lambda: gc.getNumReligionInfos(), 0), lambda i: gc.getReligionInfo(i), "getChar")
	_append_probe_for_family(lines, u"PROBE_HOLY_CITY", _safe_int(lambda: gc.getNumReligionInfos(), 0), lambda i: gc.getReligionInfo(i), "getHolyCityChar")
	_append_probe_for_family(lines, u"PROBE_CORPORATION", _safe_int(lambda: gc.getNumCorporationInfos(), 0), lambda i: gc.getCorporationInfo(i), "getChar")
	_append_probe_for_family(lines, u"PROBE_HEADQUARTERS", _safe_int(lambda: gc.getNumCorporationInfos(), 0), lambda i: gc.getCorporationInfo(i), "getHeadquarterChar")
	_append_probe_for_selected_bonuses(lines)
	_append_probe_generic_symbols(lines)


def _show_visible_probes():
	probes = _visible_probe_rows()
	for label, text in probes:
		_notify(u"%s %s" % (label, text))


def _visible_probe_rows():
	return [
		(u"Glyph religions:", _probe_text(_safe_int(lambda: gc.getNumReligionInfos(), 0), lambda i: gc.getReligionInfo(i), "getChar")),
		(u"Glyph holy:", _probe_text(_safe_int(lambda: gc.getNumReligionInfos(), 0), lambda i: gc.getReligionInfo(i), "getHolyCityChar")),
		(u"Glyph yields:", _probe_text(_info_count(lambda: gc.getNumYieldInfos(), YIELD_INFO_FALLBACK_COUNT), lambda i: gc.getYieldInfo(i), "getChar")),
		(u"Glyph commerce:", _probe_text(_info_count(lambda: gc.getNumCommerceInfos(), COMMERCE_INFO_FALLBACK_COUNT), lambda i: gc.getCommerceInfo(i), "getChar")),
	]


def _probe_text(count, info_getter, char_method):
	parts = []
	for i in _range(count):
		info = _safe_info(lambda i=i: info_getter(i))
		if info is None:
			continue
		code = _safe_int(lambda info=info, char_method=char_method: getattr(info, char_method)(), -1)
		parts.append(_glyph_for_code(code))
	return u" ".join(parts)


def _append_probe_for_family(lines, label, count, info_getter, char_method):
	entries = []
	for i in _range(count):
		info = _safe_info(lambda i=i: info_getter(i))
		if info is None:
			continue
		code = _safe_int(lambda info=info, char_method=char_method: getattr(info, char_method)(), -1)
		entries.append(u"%s=%s" % (_info_type_from_info(info), _glyph_for_code(code)))
	lines.append(_join_fields([label, _join_list(entries)]))


def _append_probe_for_selected_bonuses(lines):
	entries = []
	count = _safe_int(lambda: gc.getNumBonusInfos(), 0)
	for i in _range(count):
		if not _is_high_risk_bonus(i):
			continue
		info = gc.getBonusInfo(i)
		code = _safe_int(lambda info=info: info.getChar(), -1)
		entries.append(u"%s=%s" % (_info_type_from_info(info), _glyph_for_code(code)))
	lines.append(_join_fields([u"PROBE_SELECTED_BONUSES", _join_list(entries)]))


def _append_probe_generic_symbols(lines):
	entries = []
	game = gc.getGame()
	for symbol_name, symbol_enum in GENERIC_SYMBOLS:
		code = _safe_int(lambda symbol_enum=symbol_enum: game.getSymbolID(symbol_enum), -1)
		entries.append(u"%s=%s" % (symbol_name, _glyph_for_code(code)))
	lines.append(_join_fields([u"PROBE_GENERIC_SYMBOLS", _join_list(entries)]))


def _append_diagnosis_summary(lines):
	lines.append(u"[diagnosis_summary]")
	model = _build_allocation_model()
	fonts_present = True
	for file_name in FONT_FILE_NAMES:
		if not _first_existing_font_path(_font_file_candidates(), file_name):
			fonts_present = False
	lines.append(_kv(u"font_files_present", fonts_present))
	lines.append(_kv(u"runtime_symbol_table_complete", _runtime_symbol_table_complete()))
	lines.append(_kv(u"generic_symbol_start_matches_model", model.get(u"generic_symbol_start_matches_model", False)))
	lines.append(_kv(u"duplicate_resource_glyphs_present", _duplicate_resource_glyphs_present()))
	lines.append(_kv(u"duplicate_resource_glyphs_expected", True))
	lines.append(_kv(u"city_religion_expectations_present", _city_religion_expectations_present()))
	user_data = _first_existing_dir(_my_games_candidates())
	cache_dir = os.path.join(user_data, "cache") if user_data else ""
	ini = os.path.join(user_data, "CivilizationIV.ini") if user_data else ""
	lines.append(_kv(u"cache_dir_present", os.path.isdir(cache_dir) if cache_dir else u"unknown"))
	lines.append(_kv(u"disable_caching_value", _read_disable_caching(ini) if ini else u"unknown"))
	lines.append(_kv(u"likely_install_drift", u"unknown"))
	lines.append(_kv(u"requires_visual_context", True))


def _city_religions(city):
	items = []
	count = _safe_int(lambda: gc.getNumReligionInfos(), 0)
	for i in _range(count):
		if _safe_bool(lambda i=i: city.isHasReligion(i), False):
			items.append(_religion_name(i))
	return items


def _city_corporations(city):
	items = []
	count = _safe_int(lambda: gc.getNumCorporationInfos(), 0)
	for i in _range(count):
		if _safe_bool(lambda i=i: city.isHasCorporation(i), False):
			items.append(_corporation_name(i))
	return items


def _city_bonuses(city):
	items = []
	count = _safe_int(lambda: gc.getNumBonusInfos(), 0)
	for i in _range(count):
		num = _safe_int(lambda i=i: city.getNumBonuses(i), 0)
		if num > 0 or (_is_high_risk_bonus(i) and _safe_bool(lambda i=i: city.hasBonus(i), False)):
			items.append(u"%s:%d" % (_bonus_name(i), num))
	return items


def _is_high_risk_bonus(i_bonus):
	if i_bonus < 0:
		return False
	bonus_type = _bonus_name(i_bonus)
	for token in HIGH_RISK_BONUS_TYPE_PARTS:
		if bonus_type.find(token) != -1:
			return True
	return False


def _religion_name(i_religion):
	if i_religion < 0:
		return u"NO_RELIGION"
	return _info_type(lambda: gc.getReligionInfo(i_religion))


def _corporation_name(i_corporation):
	if i_corporation < 0:
		return u"NO_CORPORATION"
	return _info_type(lambda: gc.getCorporationInfo(i_corporation))


def _bonus_name(i_bonus):
	if i_bonus < 0:
		return u"NO_BONUS"
	return _info_type(lambda: gc.getBonusInfo(i_bonus))


def _info_type(info_getter):
	info = _safe_info(info_getter)
	if info is None:
		return u"<unavailable>"
	return _info_type_from_info(info)


def _info_type_from_info(info):
	return _safe_value(lambda: info.getType())


def _char_method_field(info, method_name):
	if not hasattr(info, method_name):
		return u"%s=<unavailable>" % method_name
	code = _safe_int(lambda: getattr(info, method_name)(), -1)
	return _char_field(method_name, code)


def _char_field(label, code):
	if code < 0:
		return u"%s=-1 glyph=<none>" % label
	return u"%s=%d hex=0x%04X glyph=%s" % (label, code, code, _glyph_for_code(code))


def _glyph_for_code(code):
	try:
		code = int(code)
		if code < 0:
			return u""
		return _unichr(code)
	except Exception:
		return u"<bad-char>"


def _file_size_text(path):
	try:
		return u"size=%d" % os.path.getsize(path)
	except Exception:
		return u"size=<error:%s>" % _exception_text()


def _file_md5_text(path):
	try:
		digest = _new_md5()
		handle = open(path, "rb")
		try:
			while True:
				block = handle.read(1024 * 1024)
				if not block:
					break
				digest.update(block)
		finally:
			handle.close()
		return u"md5=%s" % digest.hexdigest()
	except Exception:
		return u"md5=<error:%s>" % _exception_text()


def _new_md5():
	try:
		import hashlib
		return hashlib.md5()
	except Exception:
		import md5
		return md5.new()


def _write_dedicated_log(dump_id, lines):
	log_dir = _preferred_log_dir()
	if not log_dir:
		return ""
	try:
		if not os.path.isdir(log_dir):
			os.makedirs(log_dir)
		path = os.path.join(log_dir, "%s.log" % dump_id)
		_write_unicode_lines(path, lines)
		return path
	except Exception:
		CvUtil.pyPrint("GlyphDiagnostics dedicated log failed: %s" % _to_printable(_exception_text()))
		return ""


def _preferred_log_dir():
	candidates = []
	local_app_data = os.environ.get("LOCALAPPDATA", "")
	if local_app_data:
		candidates.append(os.path.join(local_app_data, "DowagerMod", "GlyphDiagnostics"))

	for key in ["OneDriveCommercial", "OneDriveConsumer", "OneDrive"]:
		root = os.environ.get(key, "")
		if root:
			candidates.append(os.path.join(root, "Documents", "My Games", "beyond the sword", "Logs"))
			candidates.append(os.path.join(root, "Documents", "My Games", "Beyond the Sword", "Logs"))

	user_profile = os.environ.get("USERPROFILE", "")
	if user_profile:
		_append_onedrive_document_candidates(candidates, user_profile)
		candidates.append(os.path.join(user_profile, "Documents", "My Games", "Beyond the Sword", "Logs"))
		candidates.append(os.path.join(user_profile, "Documents", "My Games", "beyond the sword", "Logs"))

	expanded = os.path.expanduser("~")
	if expanded and expanded != "~":
		candidates.append(os.path.join(expanded, "Documents", "My Games", "Beyond the Sword", "Logs"))
		candidates.append(os.path.join(expanded, "Documents", "My Games", "beyond the sword", "Logs"))

	for path in candidates:
		if path and _can_create_log_dir(path):
			return path
	return ""


def _append_onedrive_document_candidates(candidates, user_profile):
	try:
		for name in os.listdir(user_profile):
			if name.lower().startswith("onedrive"):
				root = os.path.join(user_profile, name)
				candidates.append(os.path.join(root, "Documents", "My Games", "beyond the sword", "Logs"))
				candidates.append(os.path.join(root, "Documents", "My Games", "Beyond the Sword", "Logs"))
	except Exception:
		pass


def _can_create_log_dir(path):
	if os.path.isdir(path):
		return True
	if path.find(os.path.join("DowagerMod", "GlyphDiagnostics")) != -1:
		root = os.environ.get("LOCALAPPDATA", "")
		return root and os.path.isdir(root)
	parent = os.path.dirname(path)
	return parent and os.path.isdir(parent)


def _write_unicode_lines(path, lines):
	import codecs
	handle = codecs.open(path, "w", "utf-8")
	try:
		for line in lines:
			handle.write(_to_unicode(line))
			handle.write(u"\n")
	finally:
		handle.close()


def _write_python_dbg_fallback(lines):
	CvUtil.pyPrint("=== DowagerMod GlyphDiagnostics fallback BEGIN ===")
	for line in lines:
		CvUtil.pyPrint(_to_printable(line))
	CvUtil.pyPrint("=== DowagerMod GlyphDiagnostics fallback END ===")


def _notify(message):
	try:
		CyInterface().addImmediateMessage(_to_unicode(message), "")
	except Exception:
		CvUtil.pyPrint("GlyphDiagnostics notify failed: %s" % _to_printable(_exception_text()))


def _pad_to_next(current):
	current += 1
	while current % PAD_AMOUNT != 0:
		current += 1
	return current


def _next_boundary(current, pad_amount):
	value = current
	while value % pad_amount != 0:
		value += 1
	return value


def _generic_shift_risk(non_art_count):
	# In current BTS layout, generic symbols remain stable while the post-bonus
	# cursor lands in the same padded row. Warn as the non-art count approaches
	# the next 25-symbol boundary.
	remainder = non_art_count % PAD_AMOUNT
	if remainder >= 20:
		return u"near_padding_boundary"
	return u"normal"


def _is_art_masterpiece_type(type_id):
	return _to_unicode(type_id).startswith(u"BONUS_ART_")


def _all_art_masterpieces(items):
	for item in items:
		if not _is_art_masterpiece_type(item):
			return False
	return True


def _compact_list(items):
	if not items:
		return u"<none>"
	limit = 24
	head = [_to_unicode(item) for item in items[:limit]]
	if len(items) > limit:
		head.append(u"...%d more" % (len(items) - limit))
	return u",".join(head)


def _city_religion_marker_string(city):
	items = []
	count = _safe_int(lambda: gc.getNumReligionInfos(), 0)
	for i in _range(count):
		if not _safe_bool(lambda i=i: city.isHasReligion(i), False):
			continue
		info = gc.getReligionInfo(i)
		religion_type = _info_type_from_info(info)
		is_holy = _safe_bool(lambda i=i: city.isHolyCityByType(i), False)
		code = _safe_int(lambda info=info, is_holy=is_holy: info.getHolyCityChar() if is_holy else info.getChar(), -1)
		items.append(u"%s:%d:0x%04X:%s:holy=%s" % (religion_type, code, code, _glyph_for_code(code), is_holy))
	return _join_list(items)


def _player_label(i_player):
	if i_player < 0:
		return u"NO_PLAYER"
	player = _safe_info(lambda: gc.getPlayer(i_player))
	if player is None:
		return u"PLAYER_%d" % i_player
	civ = _safe_value(lambda: player.getCivilizationDescription(0))
	leader = _info_type(lambda: gc.getLeaderHeadInfo(player.getLeaderType()))
	name = _safe_value(lambda: player.getNameKey())
	return u"%d:%s:%s:%s" % (i_player, leader, civ, name)


def _selected_unit_summary():
	unit = _safe_info(lambda: CyInterface().getHeadSelectedUnit())
	if unit is None or _safe_bool(lambda: unit.isNone(), True):
		return u"<none>"
	return u"owner=%s type=%s x=%s y=%s" % (
		_player_label(_safe_int(lambda: unit.getOwner(), -1)),
		_safe_value(lambda: gc.getUnitInfo(unit.getUnitType()).getType()),
		_safe_value(lambda: unit.getX()),
		_safe_value(lambda: unit.getY()),
	)


def _file_mtime_text(path):
	try:
		return u"mtime=%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
	except Exception:
		return u"mtime=<error:%s>" % _exception_text()


def _tga_header_text(path):
	try:
		handle = open(path, "rb")
		try:
			data = handle.read(18)
		finally:
			handle.close()
		if len(data) < 18:
			return u"tga=<short-header>"
		width = _byte_value(data[12]) + (_byte_value(data[13]) << 8)
		height = _byte_value(data[14]) + (_byte_value(data[15]) << 8)
		depth = _byte_value(data[16])
		image_type = _byte_value(data[2])
		return u"tga_width=%d tga_height=%d tga_depth=%d tga_type=%d" % (width, height, depth, image_type)
	except Exception:
		return u"tga=<error:%s>" % _exception_text()


def _byte_value(value):
	try:
		return ord(value)
	except TypeError:
		return int(value)


def _read_disable_caching(ini_path):
	if not ini_path or not os.path.isfile(ini_path):
		return u"unknown"
	try:
		handle = open(ini_path, "r")
		try:
			for line in handle.readlines():
				stripped = line.strip()
				if stripped.lower().startswith("disablecaching"):
					parts = stripped.split("=", 1)
					if len(parts) == 2:
						return parts[1].strip()
					return stripped
		finally:
			handle.close()
	except Exception:
		return u"error:%s" % _exception_text()
	return u"not_found"


def _first_existing_dir(paths):
	for path in paths:
		if path and os.path.isdir(path):
			return path
	return ""


def _dedupe(items):
	seen = {}
	result = []
	for item in items:
		if item and not seen.has_key(item):
			seen[item] = 1
			result.append(item)
	return result


def _runtime_symbol_table_complete():
	if _info_count(lambda: gc.getNumYieldInfos(), YIELD_INFO_FALLBACK_COUNT) <= 0:
		return False
	if _info_count(lambda: gc.getNumCommerceInfos(), COMMERCE_INFO_FALLBACK_COUNT) <= 0:
		return False
	if _safe_int(lambda: gc.getNumReligionInfos(), 0) <= 0:
		return False
	if _safe_int(lambda: gc.getNumBonusInfos(), 0) <= 0:
		return False
	if _safe_int(lambda: gc.getGame().getSymbolID(0), -1) < 0:
		return False
	return True


def _duplicate_resource_glyphs_present():
	seen = {}
	count = _safe_int(lambda: gc.getNumBonusInfos(), 0)
	for i in _range(count):
		code = _safe_int(lambda i=i: gc.getBonusInfo(i).getChar(), -1)
		if seen.has_key(code):
			return True
		seen[code] = 1
	return False


def _city_religion_expectations_present():
	max_players = _safe_int(lambda: gc.getMAX_PLAYERS(), 0)
	for i_player in _range(max_players):
		player = _safe_info(lambda i_player=i_player: gc.getPlayer(i_player))
		if player is None or not _safe_bool(lambda player=player: player.isAlive(), False):
			continue
		try:
			city, iter_city = player.firstCity(False)
			guard = 0
			while city and not city.isNone() and guard < 512:
				if _city_religions(city):
					return True
				city, iter_city = player.nextCity(iter_city, False)
				guard += 1
		except Exception:
			pass
	return False


def _safe_info(func):
	try:
		return func()
	except Exception:
		return None


def _info_count(func, default):
	count = _safe_int(func, -1)
	if count >= 0:
		return count
	return default


def _safe_value(func):
	try:
		return _to_unicode(func())
	except Exception:
		return u"<error:%s>" % _exception_text()


def _safe_int(func, default):
	try:
		return int(func())
	except Exception:
		return default


def _safe_bool(func, default):
	try:
		return bool(func())
	except Exception:
		return default


def _kv(key, value):
	return u"%s=%s" % (_to_unicode(key), _to_unicode(value))


def _join_fields(fields):
	values = []
	for field in fields:
		values.append(_to_unicode(field).replace(u"\t", u" ").replace(u"\r", u" ").replace(u"\n", u" "))
	return u"\t".join(values)


def _join_list(items):
	if not items:
		return u"<none>"
	return u",".join([_to_unicode(item) for item in items])


def _to_unicode(value):
	if isinstance(value, _unicode):
		return value
	try:
		return _unicode(value)
	except Exception:
		return u"<unprintable>"


def _to_printable(value):
	text = _to_unicode(value)
	try:
		return text.encode("utf-8")
	except Exception:
		return str(text)


def _exception_text():
	exc_type, exc_value, exc_tb = sys.exc_info()
	try:
		return _to_unicode(exc_type.__name__) + u":" + _to_unicode(exc_value)
	except Exception:
		return u"<unknown exception>"
