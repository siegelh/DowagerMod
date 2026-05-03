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
		_append_header(lines, dump_id, source, mx, my, px, py)
		_append_font_files(lines)
		_append_runtime_symbols(lines)
		_append_player_context(lines, px, py)
		_append_probe_strings(lines)
		lines.append(u"=== DowagerMod GlyphDiagnostics END ===")

		path = _write_dedicated_log(dump_id, lines)
		if path:
			_notify(u"Glyph diagnostics written: %s" % path)
			CvUtil.pyPrint("GlyphDiagnostics wrote %s" % _to_printable(path))
			return path

		_write_python_dbg_fallback(lines)
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


def _append_header(lines, dump_id, source, mx, my, px, py):
	game = gc.getGame()
	i_player = _safe_int(lambda: game.getActivePlayer(), -1)
	lines.append(u"=== DowagerMod GlyphDiagnostics BEGIN ===")
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

	if i_player >= 0:
		player = gc.getPlayer(i_player)
		lines.append(_kv(u"active_player_name", _safe_value(lambda: player.getNameKey())))
		lines.append(_kv(u"active_player_civ_type", _info_type(lambda: gc.getCivilizationInfo(player.getCivilizationType()))))
		lines.append(_kv(u"active_player_civ_description", _safe_value(lambda: player.getCivilizationDescription(0))))
		lines.append(_kv(u"active_player_leader_type", _info_type(lambda: gc.getLeaderHeadInfo(player.getLeaderType()))))
		lines.append(_kv(u"active_player_team", _safe_value(lambda: player.getTeam())))
		lines.append(_kv(u"active_player_state_religion", _religion_name(_safe_int(lambda: player.getStateReligion(), -1))))


def _append_font_files(lines):
	lines.append(u"[font_files]")
	paths = _font_file_candidates()
	for file_name in FONT_FILE_NAMES:
		path = _first_existing_font_path(paths, file_name)
		if path:
			lines.append(_join_fields([u"FONT", file_name, path, _file_size_text(path), _file_md5_text(path)]))
		else:
			lines.append(_join_fields([u"FONT", file_name, u"<not found>", u"size=<missing>", u"md5=<missing>"]))


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
