## Art Masterpiece system runtime hooks.
## Native bonus-backed mode:
## - each masterpiece is a real bonus resource for diplomacy trading
## - script data only tracks globally claimed pieces and the Python happiness offset

from CvPythonExtensions import *
import CvArtMasterpieceData
import time

gc = CyGlobalContext()
localText = CyTranslator()

_STATE_BEGIN = "__ARTSYS_BEGIN__"
_STATE_END = "__ARTSYS_END__"

_CACHE_TRIGGER_BUILDING = -2
_BASE_HAPPINESS_CAP = 10
_REFRESH_INTERVAL_SECONDS = 1.0
_LAST_UPDATE_AT = 0.0

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
        _BONUS_TYPE_CACHE[pieceType] = gc.getInfoTypeForString(pieceType)
    return _BONUS_TYPE_CACHE[pieceType]


def _parse_state():
    game = gc.getGame()
    raw = game.getScriptData()
    state = {"claimed": {}, "happy": {}, "owned": {}, "migrate_claimed": {}}

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
            payload = line[len("CLAIMED="):]
            if payload != "":
                for token in payload.split(","):
                    token = token.strip()
                    if token == "":
                        continue
                    pieceType = token.split(":")[0].strip()
                    if pieceType == "":
                        continue
                    state["claimed"][pieceType] = 1

    return state


def _build_state_block(state):
    claimedPieces = state["claimed"].keys()
    claimedPieces.sort()
    claimedLine = "CLAIMED=" + ",".join(claimedPieces)

    happyPairs = []
    for iPlayer in state["happy"].keys():
        happyPairs.append((iPlayer, state["happy"][iPlayer]))
    happyPairs.sort()
    happyLine = "HAPPY=" + ",".join(["%d:%d" % (pair[0], pair[1]) for pair in happyPairs])

    return _STATE_BEGIN + "\n" + claimedLine + "\n" + happyLine + "\n" + _STATE_END


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


def _get_migration_city(player):
    city = player.getCapitalCity()
    if city is not None:
        try:
            if not city.isNone():
                return city
        except:
            return city

    iLoop = 0
    loopCity = player.firstCity(False)[0]
    if loopCity is not None:
        try:
            if not loopCity.isNone():
                return loopCity
        except:
            return loopCity
    return None


def _migrate_legacy_inventory_to_bonus_network(state):
    bChanged = False
    remainingOwned = {}

    if len(state["migrate_claimed"]) > 0:
        for pieceType in state["migrate_claimed"].keys():
            if not state["claimed"].has_key(pieceType):
                state["claimed"][pieceType] = 1
                bChanged = True
        state["migrate_claimed"] = {}
        bChanged = True

    for iPlayer in state["owned"].keys():
        pieces = state["owned"][iPlayer]
        if len(pieces) == 0:
            continue

        player = gc.getPlayer(iPlayer)
        if not player.isAlive():
            for pieceType in pieces.keys():
                if not state["claimed"].has_key(pieceType):
                    state["claimed"][pieceType] = 1
                    bChanged = True
            continue

        city = _get_migration_city(player)
        if city is None:
            remainingOwned[iPlayer] = pieces
            continue

        for pieceType in pieces.keys():
            if not state["claimed"].has_key(pieceType):
                state["claimed"][pieceType] = 1
                bChanged = True

            eBonus = _get_bonus_type(pieceType)
            if eBonus < 0:
                continue
            if player.getNumAvailableBonuses(eBonus) > 0 or city.getFreeBonus(eBonus) > 0:
                continue

            city.changeFreeBonus(eBonus, 1)
            bChanged = True

    if len(remainingOwned) != len(state["owned"]):
        bChanged = True
    state["owned"] = remainingOwned
    return bChanged


def _sync_claimed_from_world(state):
    bChanged = False

    for row in CvArtMasterpieceData.ART_MASTERPIECES:
        pieceType = row[0]
        if state["claimed"].has_key(pieceType):
            continue

        eBonus = _get_bonus_type(pieceType)
        if eBonus < 0:
            continue

        for iPlayer in range(gc.getMAX_PLAYERS()):
            player = gc.getPlayer(iPlayer)
            if not player.isAlive():
                continue
            if player.getNumAvailableBonuses(eBonus) > 0 or player.getBonusExport(eBonus) > 0:
                state["claimed"][pieceType] = 1
                bChanged = True
                break

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
        for era in CvArtMasterpieceData.ART_ERA_ORDER:
            if not CvArtMasterpieceData.ART_BY_ERA.has_key(era):
                continue
            for pieceType in CvArtMasterpieceData.ART_BY_ERA[era]:
                if not state["claimed"].has_key(pieceType):
                    candidates.append(pieceType)

    if len(candidates) == 0:
        return None

    iPick = gc.getGame().getSorenRandNum(len(candidates), "Art Masterpiece Roll")
    return candidates[iPick]


def _count_accessible_art(iPlayer):
    eraCounts = {}
    typeCounts = {}
    totalDistinct = 0

    if iPlayer < 0 or iPlayer >= gc.getMAX_PLAYERS():
        return totalDistinct, eraCounts, typeCounts

    player = gc.getPlayer(iPlayer)

    for row in CvArtMasterpieceData.ART_MASTERPIECES:
        pieceType = row[0]
        eBonus = _get_bonus_type(pieceType)
        if eBonus < 0:
            continue
        if player.getNumAvailableBonuses(eBonus) <= 0:
            continue

        totalDistinct += 1
        eraCounts[row[1]] = eraCounts.get(row[1], 0) + 1
        typeCounts[row[2]] = typeCounts.get(row[2], 0) + 1

    return totalDistinct, eraCounts, typeCounts


def _compute_set_bonus(iPlayer):
    totalDistinct, eraCounts, typeCounts = _count_accessible_art(iPlayer)
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


def _compute_extra_happiness_target(iPlayer):
    totalDistinct, eraCounts, typeCounts = _count_accessible_art(iPlayer)
    setBonus = _compute_set_bonus(iPlayer)

    if totalDistinct <= _BASE_HAPPINESS_CAP:
        return setBonus

    return setBonus - (totalDistinct - _BASE_HAPPINESS_CAP)


def _reconcile_player_happiness(iPlayer, state):
    player = gc.getPlayer(iPlayer)
    current = state["happy"].get(iPlayer, 0)

    if not player.isAlive():
        if current != 0:
            player.changeExtraHappiness(-current)
            state["happy"][iPlayer] = 0
            return True
        return False

    target = _compute_extra_happiness_target(iPlayer)
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
    owned = {}
    if iPlayer < 0 or iPlayer >= gc.getMAX_PLAYERS():
        return owned

    player = gc.getPlayer(iPlayer)
    for row in CvArtMasterpieceData.ART_MASTERPIECES:
        pieceType = row[0]
        eBonus = _get_bonus_type(pieceType)
        if eBonus >= 0 and player.getNumAvailableBonuses(eBonus) > 0:
            owned[pieceType] = 1
    return owned


def getOwnedCount(iPlayer, pieceType):
    if iPlayer < 0 or iPlayer >= gc.getMAX_PLAYERS():
        return 0

    eBonus = _get_bonus_type(pieceType)
    if eBonus < 0:
        return 0

    if gc.getPlayer(iPlayer).getNumAvailableBonuses(eBonus) > 0:
        return 1
    return 0


def getImportCount(iPlayer, pieceType):
    if iPlayer < 0 or iPlayer >= gc.getMAX_PLAYERS():
        return 0

    eBonus = _get_bonus_type(pieceType)
    if eBonus < 0:
        return 0
    return gc.getPlayer(iPlayer).getBonusImport(eBonus)


def _run_full_reconcile():
    state = _parse_state()
    bChanged = False

    if _migrate_legacy_inventory_to_bonus_network(state):
        bChanged = True
    if _sync_claimed_from_world(state):
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

    if _migrate_legacy_inventory_to_bonus_network(state):
        bChanged = True
    if _sync_claimed_from_world(state):
        bChanged = True
    if _reconcile_player_happiness(iPlayer, state):
        bChanged = True

    if bChanged:
        _write_state(state)


def onUpdate(fDeltaTime):
    global _LAST_UPDATE_AT

    now = time.time()
    if (now - _LAST_UPDATE_AT) < _REFRESH_INTERVAL_SECONDS:
        return
    _LAST_UPDATE_AT = now

    state = _parse_state()
    bChanged = False

    if _migrate_legacy_inventory_to_bonus_network(state):
        bChanged = True
    if _sync_claimed_from_world(state):
        bChanged = True

    for iPlayer in range(gc.getMAX_PLAYERS()):
        if _reconcile_player_happiness(iPlayer, state):
            bChanged = True

    if bChanged:
        _write_state(state)


def onBuildingBuilt(pCity, iBuildingType):
    iTrigger = _get_trigger_building()
    if iTrigger < 0 or iBuildingType != iTrigger:
        return False

    iOwner = pCity.getOwner()
    pCity.setNumRealBuilding(iTrigger, 0)

    state = _parse_state()
    if _migrate_legacy_inventory_to_bonus_network(state):
        _write_state(state)

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

    eBonus = _get_bonus_type(pieceType)
    if eBonus < 0:
        pCity.changeCulture(iOwner, 2000, True)
        _notify_player(
            iOwner,
            "Masterpiece registration failed for %s. %s gains +2000 culture." % (pieceType, pCity.getName()),
            "",
            pCity.getX(),
            pCity.getY(),
        )
        return True

    pCity.changeFreeBonus(eBonus, 1)
    state["claimed"][pieceType] = 1

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
