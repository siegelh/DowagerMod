## Art Masterpiece system runtime hooks.
## Inventory-backed mode:
## - each masterpiece belongs to a civilization's Art Gallery
## - script data tracks claimed pieces, per-player ownership, and the applied happiness offset

from CvPythonExtensions import *
import CvArtMasterpieceData


gc = CyGlobalContext()
localText = CyTranslator()

_STATE_BEGIN = "__ARTSYS_BEGIN__"
_STATE_END = "__ARTSYS_END__"

_CACHE_TRIGGER_BUILDING = -2
_BASE_HAPPINESS_CAP = 10
_BONUS_TYPE_CACHE = {}

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


def _get_bonus_type(pieceType):
    if not _BONUS_TYPE_CACHE.has_key(pieceType):
        try:
            _BONUS_TYPE_CACHE[pieceType] = gc.getInfoTypeForString(pieceType)
        except:
            _BONUS_TYPE_CACHE[pieceType] = -1
    return _BONUS_TYPE_CACHE[pieceType]


def _get_player_owned_map(state, iPlayer):
    if not state["owned"].has_key(iPlayer):
        state["owned"][iPlayer] = {}
    return state["owned"][iPlayer]


def _build_claimed_lookup_from_owned(state):
    claimed = {}
    for iPlayer in state["owned"].keys():
        for pieceType in state["owned"][iPlayer].keys():
            claimed[pieceType] = 1
    return claimed


def _parse_state():
    game = gc.getGame()
    raw = game.getScriptData()
    state = {"claimed": {}, "owned": {}, "happy": {}}

    if raw is None:
        raw = ""

    iStart = raw.find(_STATE_BEGIN)
    iEnd = raw.find(_STATE_END)
    if iStart == -1 or iEnd == -1 or iEnd < iStart:
        return state

    block = raw[iStart + len(_STATE_BEGIN):iEnd]
    for line in block.split("\n"):
        line = line.strip()
        if line == "":
            continue

        if line.startswith("OWNED="):
            payload = line[len("OWNED="):]
            if payload != "":
                for playerBlock in payload.split(";"):
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
            payload = line[len("CLAIMED="):]
            if payload != "":
                for token in payload.split(","):
                    token = token.strip()
                    if token == "":
                        continue
                    pieceType = token.split(":")[0].strip()
                    if pieceType != "":
                        state["claimed"][pieceType] = 1

    return state


def _build_state_block(state):
    ownedPairs = []
    for iPlayer in state["owned"].keys():
        pieces = state["owned"][iPlayer].keys()
        pieces.sort()
        ownedPairs.append((iPlayer, pieces))
    ownedPairs.sort()

    ownedParts = []
    for pair in ownedPairs:
        ownedParts.append("%d:%s" % (pair[0], "|".join(pair[1])))
    ownedLine = "OWNED=" + ";".join(ownedParts)

    happyPairs = []
    for iPlayer in state["happy"].keys():
        happyPairs.append((iPlayer, state["happy"][iPlayer]))
    happyPairs.sort()
    happyLine = "HAPPY=" + ",".join(["%d:%d" % (pair[0], pair[1]) for pair in happyPairs])

    claimedPieces = state["claimed"].keys()
    claimedPieces.sort()
    claimedLine = "CLAIMED=" + ",".join(claimedPieces)

    return _STATE_BEGIN + "\n" + ownedLine + "\n" + happyLine + "\n" + claimedLine + "\n" + _STATE_END


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


def _normalize_claimed_from_owned(state):
    desired = _build_claimed_lookup_from_owned(state)

    if len(desired) != len(state["claimed"]):
        state["claimed"] = desired
        return True

    for pieceType in desired.keys():
        if not state["claimed"].has_key(pieceType):
            state["claimed"] = desired
            return True

    return False


def _migrate_bonus_backed_art_to_inventory(state):
    bChanged = False
    foundOwnedFromBonus = {}

    for iPlayer in range(gc.getMAX_PLAYERS()):
        player = gc.getPlayer(iPlayer)
        if not player.isAlive():
            continue

        loopCity, iterCity = player.firstCity(False)
        while loopCity:
            for row in CvArtMasterpieceData.ART_MASTERPIECES:
                pieceType = row[0]
                eBonus = _get_bonus_type(pieceType)
                if eBonus < 0:
                    continue

                iFree = loopCity.getFreeBonus(eBonus)
                if iFree > 0:
                    if not foundOwnedFromBonus.has_key(iPlayer):
                        foundOwnedFromBonus[iPlayer] = {}
                    foundOwnedFromBonus[iPlayer][pieceType] = 1
                    loopCity.changeFreeBonus(eBonus, -iFree)
                    bChanged = True

            loopCity, iterCity = player.nextCity(iterCity, False)

    for iPlayer in foundOwnedFromBonus.keys():
        ownedMap = _get_player_owned_map(state, iPlayer)
        for pieceType in foundOwnedFromBonus[iPlayer].keys():
            if not ownedMap.has_key(pieceType):
                ownedMap[pieceType] = 1
                bChanged = True

    return bChanged


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


def _pick_unclaimed_piece(state, iPlayer = -1):
    currentEra = _get_current_era_bucket(iPlayer)
    candidates = []

    if CvArtMasterpieceData.ART_BY_ERA.has_key(currentEra):
        for pieceType in CvArtMasterpieceData.ART_BY_ERA[currentEra]:
            if not state["claimed"].has_key(pieceType):
                candidates.append(pieceType)

    if len(candidates) == 0:
        for szEra in CvArtMasterpieceData.ART_ERA_ORDER:
            if not CvArtMasterpieceData.ART_BY_ERA.has_key(szEra):
                continue
            for pieceType in CvArtMasterpieceData.ART_BY_ERA[szEra]:
                if not state["claimed"].has_key(pieceType):
                    candidates.append(pieceType)

    if len(candidates) == 0:
        return None

    iPick = gc.getGame().getSorenRandNum(len(candidates), "Art Masterpiece Roll")
    return candidates[iPick]


def _count_owned_art_from_state(state, iPlayer):
    eraCounts = {}
    typeCounts = {}
    totalDistinct = 0

    if iPlayer < 0 or iPlayer >= gc.getMAX_PLAYERS():
        return totalDistinct, eraCounts, typeCounts

    ownedMap = _get_player_owned_map(state, iPlayer)
    for row in CvArtMasterpieceData.ART_MASTERPIECES:
        pieceType = row[0]
        if not ownedMap.has_key(pieceType):
            continue

        totalDistinct += 1
        eraCounts[row[1]] = eraCounts.get(row[1], 0) + 1
        typeCounts[row[2]] = typeCounts.get(row[2], 0) + 1

    return totalDistinct, eraCounts, typeCounts


def _compute_set_bonus_from_state(state, iPlayer):
    totalDistinct, eraCounts, typeCounts = _count_owned_art_from_state(state, iPlayer)
    iEraBonus = 0
    iTypeBonus = 0

    for szEra in eraCounts.keys():
        if eraCounts[szEra] >= 3:
            iEraBonus += 1

    for szType in typeCounts.keys():
        if typeCounts[szType] >= 4:
            iTypeBonus += 1

    iTotal = iEraBonus + iTypeBonus
    if iTotal > 8:
        iTotal = 8
    return iTotal


def _compute_happiness_from_state(state, iPlayer):
    totalDistinct, eraCounts, typeCounts = _count_owned_art_from_state(state, iPlayer)
    iBaseBonus = totalDistinct
    if iBaseBonus > _BASE_HAPPINESS_CAP:
        iBaseBonus = _BASE_HAPPINESS_CAP
    return iBaseBonus + _compute_set_bonus_from_state(state, iPlayer)


def _reconcile_player_happiness(iPlayer, state):
    player = gc.getPlayer(iPlayer)
    current = state["happy"].get(iPlayer, 0)

    if not player.isAlive():
        if current != 0:
            player.changeExtraHappiness(-current)
            state["happy"][iPlayer] = 0
            return True
        return False

    target = _compute_happiness_from_state(state, iPlayer)
    delta = target - current
    if delta != 0:
        player.changeExtraHappiness(delta)
        state["happy"][iPlayer] = target
        return True

    return False


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


def getImportCount(iPlayer, pieceType):
    return 0


def _run_full_reconcile():
    state = _parse_state()
    bChanged = False

    if _migrate_bonus_backed_art_to_inventory(state):
        bChanged = True
    if _normalize_claimed_from_owned(state):
        bChanged = True

    for iPlayer in range(gc.getMAX_PLAYERS()):
        if _reconcile_player_happiness(iPlayer, state):
            bChanged = True

    if bChanged:
        _write_state(state)


def onGameStart():
    _run_full_reconcile()


def onLoadGame():
    _run_full_reconcile()


def onBeginPlayerTurn(iPlayer):
    state = _parse_state()
    bChanged = False

    if _migrate_bonus_backed_art_to_inventory(state):
        bChanged = True
    if _normalize_claimed_from_owned(state):
        bChanged = True
    if _reconcile_player_happiness(iPlayer, state):
        bChanged = True

    if bChanged:
        _write_state(state)


def onUpdate(fDeltaTime):
    return


def onBuildingBuilt(pCity, iBuildingType):
    iTrigger = _get_trigger_building()
    if iTrigger < 0 or iBuildingType != iTrigger:
        return False

    iOwner = pCity.getOwner()
    pCity.setNumRealBuilding(iTrigger, 0)

    state = _parse_state()
    bChanged = False

    if _migrate_bonus_backed_art_to_inventory(state):
        bChanged = True
    if _normalize_claimed_from_owned(state):
        bChanged = True

    pieceType = _pick_unclaimed_piece(state, iOwner)
    if pieceType is None:
        pCity.changeCulture(iOwner, 2000, True)
        if bChanged:
            _write_state(state)
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
    state["claimed"][pieceType] = 1

    if _reconcile_player_happiness(iOwner, state):
        bChanged = True

    _write_state(state)

    szButton = ""
    if CvArtMasterpieceData.ART_BUTTON_BY_BONUS.has_key(pieceType):
        szButton = CvArtMasterpieceData.ART_BUTTON_BY_BONUS[pieceType]

    _notify_player(
        iOwner,
        "Masterpiece curated in %s: %s" % (pCity.getName(), _piece_name(pieceType)),
        szButton,
        pCity.getX(),
        pCity.getY(),
    )

    return True
