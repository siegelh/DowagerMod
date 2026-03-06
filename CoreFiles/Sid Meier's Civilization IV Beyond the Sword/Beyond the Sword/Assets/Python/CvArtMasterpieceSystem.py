## Art Masterpiece system runtime hooks.
## Stability mode: inventory-backed ownership without adding live bonus resources.

from CvPythonExtensions import *
import CvArtMasterpieceData

gc = CyGlobalContext()
localText = CyTranslator()

_STATE_BEGIN = "__ARTSYS_BEGIN__"
_STATE_END = "__ARTSYS_END__"

_CACHE_TRIGGER_BUILDING = -2
_BASE_HAPPINESS_CAP = 10

_ERA_TO_BUCKET = {
	"ERA_ANCIENT": "ANTIQUITY",
	"ERA_CLASSICAL": "ANTIQUITY",
	"ERA_MEDIEVAL": "MEDIEVAL",
	"ERA_RENAISSANCE": "RENAISSANCE",
	"ERA_INDUSTRIAL": "INDUSTRIAL",
	"ERA_MODERN": "MODERN",
	"ERA_POSTMODERN": "CONTEMPORARY",
	"ERA_FUTURE": "CONTEMPORARY",
}


def _get_trigger_building():
	global _CACHE_TRIGGER_BUILDING
	if _CACHE_TRIGGER_BUILDING == -2:
		_CACHE_TRIGGER_BUILDING = gc.getInfoTypeForString("BUILDING_ART_MASTERPIECE_TRIGGER")
	return _CACHE_TRIGGER_BUILDING


def _parse_state():
	game = gc.getGame()
	raw = game.getScriptData()
	state = {"owned": {}, "happy": {}, "migrate_claimed": {}}

	if raw is None:
		raw = ""

	iStart = raw.find(_STATE_BEGIN)
	iEnd = raw.find(_STATE_END)
	if iStart == -1 or iEnd == -1 or iEnd < iStart:
		return state

	block = raw[iStart + len(_STATE_BEGIN):iEnd]
	lines = block.split("\n")
	for line in lines:
		line = line.strip()
		if line == "":
			continue

		if line.startswith("OWNED="):
			payload = line[len("OWNED="):]
			if payload != "":
				playerBlocks = payload.split(";")
				for playerBlock in playerBlocks:
					playerBlock = playerBlock.strip()
					if playerBlock == "":
						continue
					parts = playerBlock.split(":")
					if len(parts) != 2:
						continue
					try:
						iPlayer = int(parts[0])
					except:
						continue
					pieces = {}
					if parts[1] != "":
						for pieceType in parts[1].split("|"):
							pieceType = pieceType.strip()
							if pieceType != "":
								pieces[pieceType] = 1
					state["owned"][iPlayer] = pieces

		elif line.startswith("HAPPY="):
			payload = line[len("HAPPY="):]
			if payload != "":
				for token in payload.split(","):
					token = token.strip()
					if token == "":
						continue
					parts = token.split(":")
					if len(parts) != 2:
						continue
					try:
						iPlayer = int(parts[0])
						iValue = int(parts[1])
					except:
						continue
					state["happy"][iPlayer] = iValue

		elif line.startswith("CLAIMED="):
			# Migration path from the old bonus-backed state format.
			payload = line[len("CLAIMED="):]
			if payload != "":
				for token in payload.split(","):
					token = token.strip()
					if token == "":
						continue
					pieceType = token.split(":")[0].strip()
					if pieceType != "":
						state["migrate_claimed"][pieceType] = 1

	_migrate_legacy_claimed(state)
	return state


def _migrate_legacy_claimed(state):
	if len(state["migrate_claimed"]) == 0:
		return
	if len(state["owned"]) > 0:
		state["migrate_claimed"] = {}
		return

	iActivePlayer = gc.getGame().getActivePlayer()
	if iActivePlayer < 0:
		iActivePlayer = 0

	state["owned"][iActivePlayer] = {}
	for pieceType in state["migrate_claimed"].keys():
		state["owned"][iActivePlayer][pieceType] = 1

	state["migrate_claimed"] = {}


def _build_state_block(state):
	ownedPairs = []
	for iPlayer in state["owned"].keys():
		pieces = state["owned"][iPlayer].keys()
		pieces.sort()
		ownedPairs.append((iPlayer, pieces))
	ownedPairs.sort()

	ownedLineParts = []
	for pair in ownedPairs:
		ownedLineParts.append("%d:%s" % (pair[0], "|".join(pair[1])))
	ownedLine = "OWNED=" + ";".join(ownedLineParts)

	happyPairs = []
	for iPlayer in state["happy"].keys():
		happyPairs.append((iPlayer, state["happy"][iPlayer]))
	happyPairs.sort()
	happyLine = "HAPPY=" + ",".join(["%d:%d" % (pair[0], pair[1]) for pair in happyPairs])
	return _STATE_BEGIN + "\n" + ownedLine + "\n" + happyLine + "\n" + _STATE_END


def _write_state(state):
	game = gc.getGame()
	raw = game.getScriptData()
	if raw is None:
		raw = ""

	block = _build_state_block(state)

	iStart = raw.find(_STATE_BEGIN)
	iEnd = raw.find(_STATE_END)
	if iStart != -1 and iEnd != -1 and iEnd >= iStart:
		iEnd += len(_STATE_END)
		newRaw = raw[:iStart] + block + raw[iEnd:]
	else:
		if raw != "" and not raw.endswith("\n"):
			raw += "\n"
		newRaw = raw + block

	game.setScriptData(newRaw)


def _era_bucket_from_index(iEra):
	if iEra < 0:
		return "ANTIQUITY"
	szEraType = gc.getEraInfo(iEra).getType()
	if _ERA_TO_BUCKET.has_key(szEraType):
		return _ERA_TO_BUCKET[szEraType]
	if iEra <= 1:
		return "ANTIQUITY"
	if iEra == 2:
		return "MEDIEVAL"
	if iEra == 3:
		return "RENAISSANCE"
	if iEra == 4:
		return "INDUSTRIAL"
	if iEra == 5:
		return "MODERN"
	return "CONTEMPORARY"


def _get_current_era_bucket(iPlayer = -1):
	iEra = -1
	if iPlayer >= 0 and iPlayer < gc.getMAX_PLAYERS():
		try:
			iEra = gc.getPlayer(iPlayer).getCurrentEra()
		except:
			iEra = -1

	if iEra < 0:
		iEra = gc.getGame().getCurrentEra()

	return _era_bucket_from_index(iEra)


def _get_player_owned_map(state, iPlayer):
	if not state["owned"].has_key(iPlayer):
		state["owned"][iPlayer] = {}
	return state["owned"][iPlayer]


def _build_claimed_lookup(state):
	claimed = {}
	for iPlayer in state["owned"].keys():
		for pieceType in state["owned"][iPlayer].keys():
			claimed[pieceType] = 1
	return claimed


def _pick_unclaimed_piece(state, iPlayer = -1):
	claimed = _build_claimed_lookup(state)
	currentEra = _get_current_era_bucket(iPlayer)
	eraOrder = CvArtMasterpieceData.ART_ERA_ORDER
	candidates = []

	# First pass: current era only.
	if CvArtMasterpieceData.ART_BY_ERA.has_key(currentEra):
		for pieceType in CvArtMasterpieceData.ART_BY_ERA[currentEra]:
			if not claimed.has_key(pieceType):
				candidates.append(pieceType)

	# Fallback: any era.
	if len(candidates) == 0:
		for era in eraOrder:
			if CvArtMasterpieceData.ART_BY_ERA.has_key(era):
				for pieceType in CvArtMasterpieceData.ART_BY_ERA[era]:
					if not claimed.has_key(pieceType):
						candidates.append(pieceType)

	if len(candidates) == 0:
		return None

	iPick = gc.getGame().getSorenRandNum(len(candidates), "Art Masterpiece Roll")
	return candidates[iPick]


def _count_owned_art_from_state(state, iPlayer):
	ownedMap = _get_player_owned_map(state, iPlayer)
	eraCounts = {}
	typeCounts = {}
	totalDistinct = 0

	for row in CvArtMasterpieceData.ART_MASTERPIECES:
		pieceType = row[0]
		era = row[1]
		artType = row[2]
		if ownedMap.has_key(pieceType):
			totalDistinct += 1
			eraCounts[era] = eraCounts.get(era, 0) + 1
			typeCounts[artType] = typeCounts.get(artType, 0) + 1

	return totalDistinct, eraCounts, typeCounts


def _compute_set_bonus_from_state(state, iPlayer):
	totalDistinct, eraCounts, typeCounts = _count_owned_art_from_state(state, iPlayer)
	iEraBonus = 0
	iTypeBonus = 0

	for era in eraCounts.keys():
		if eraCounts[era] >= 3:
			iEraBonus += 1
	for artType in typeCounts.keys():
		if typeCounts[artType] >= 4:
			iTypeBonus += 1

	iTotal = iEraBonus + iTypeBonus
	if iTotal > 8:
		iTotal = 8
	return iTotal


def _compute_happiness_from_state(state, iPlayer):
	totalDistinct, eraCounts, typeCounts = _count_owned_art_from_state(state, iPlayer)
	baseBonus = totalDistinct
	if baseBonus > _BASE_HAPPINESS_CAP:
		baseBonus = _BASE_HAPPINESS_CAP
	setBonus = _compute_set_bonus_from_state(state, iPlayer)
	return baseBonus + setBonus


def _reconcile_player_happiness(iPlayer, state):
	player = gc.getPlayer(iPlayer)
	current = state["happy"].get(iPlayer, 0)
	bChanged = False

	if not player.isAlive():
		if current != 0:
			state["happy"][iPlayer] = 0
			bChanged = True
		if state["owned"].has_key(iPlayer):
			del state["owned"][iPlayer]
			bChanged = True
		return bChanged

	target = _compute_happiness_from_state(state, iPlayer)
	delta = target - current
	if delta != 0:
		player.changeExtraHappiness(delta)
		state["happy"][iPlayer] = target
		return True
	return bChanged


def _piece_text_key(pieceType):
	return "TXT_KEY_" + pieceType


def _piece_name(pieceType):
	szKey = _piece_text_key(pieceType)
	szName = localText.getText(szKey, ())
	if szName == szKey:
		return pieceType
	return szName


def _notify_player(iPlayer, szMessage, szButton, iX, iY):
	CyInterface().addMessage(
		iPlayer,
		True,
		25,
		szMessage,
		"AS2D_DISCOVERBONUS",
		InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
		szButton,
		ColorTypes(8),
		iX,
		iY,
		True,
		True,
	)


def getOwnedPieces(iPlayer):
	state = _parse_state()
	owned = {}
	if state["owned"].has_key(iPlayer):
		for pieceType in state["owned"][iPlayer].keys():
			owned[pieceType] = 1
	return owned


def getOwnedCount(iPlayer, pieceType):
	state = _parse_state()
	if not state["owned"].has_key(iPlayer):
		return 0
	if state["owned"][iPlayer].has_key(pieceType):
		return 1
	return 0


def onGameStart():
	state = _parse_state()
	bChanged = False
	for iPlayer in range(gc.getMAX_PLAYERS()):
		if _reconcile_player_happiness(iPlayer, state):
			bChanged = True
	if bChanged:
		_write_state(state)


def onLoadGame():
	onGameStart()


def onBeginPlayerTurn(iPlayer):
	state = _parse_state()
	if _reconcile_player_happiness(iPlayer, state):
		_write_state(state)


def onBuildingBuilt(pCity, iBuildingType):
	iTrigger = _get_trigger_building()
	if iTrigger < 0 or iBuildingType != iTrigger:
		return False

	iOwner = pCity.getOwner()
	pCity.setNumRealBuilding(iTrigger, 0)

	state = _parse_state()
	pieceType = _pick_unclaimed_piece(state, iOwner)
	if pieceType is None:
		pCity.changeCulture(iOwner, 2000, True)
		_notify_player(
			iOwner,
			"Masterpiece archives are exhausted. %s gains +2000 culture." % pCity.getName(),
			"",
			pCity.getX(),
			pCity.getY(),
		)
		return True

	ownedMap = _get_player_owned_map(state, iOwner)
	ownedMap[pieceType] = 1

	_reconcile_player_happiness(iOwner, state)
	_write_state(state)

	szMessage = "Masterpiece created in %s: %s" % (pCity.getName(), _piece_name(pieceType))
	szButton = ""
	if CvArtMasterpieceData.ART_BUTTON_BY_BONUS.has_key(pieceType):
		szButton = CvArtMasterpieceData.ART_BUTTON_BY_BONUS[pieceType]
	_notify_player(
		iOwner,
		szMessage,
		szButton,
		pCity.getX(),
		pCity.getY(),
	)

	return True
