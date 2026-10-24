from CvPythonExtensions import *

gc = CyGlobalContext()

GUILD_REMOVE_MESSAGE = 0x4755494C


def requestBranchRemoval(iRequestingPlayer, iCityOwner, iCityId, iGuild):
	CyMessageControl().sendModNetMessage(
		GUILD_REMOVE_MESSAGE, iRequestingPlayer, iCityOwner, iCityId, iGuild
	)


def onModNetMessage(iData1, iData2, iData3, iData4, iData5):
	if iData1 != GUILD_REMOVE_MESSAGE:
		return False
	if iData2 < 0 or iData2 >= gc.getMAX_PLAYERS():
		return True
	if iData3 < 0 or iData3 >= gc.getMAX_PLAYERS():
		return True
	if iData5 < 0 or iData5 >= gc.getNumGuildInfos():
		return True

	city = gc.getPlayer(iData3).getCity(iData4)
	if city is None or city.isNone() or not city.hasGuildBranch(iData5):
		return True
	if city.getOwner() != iData2 and city.getGuildSponsor(iData5) != iData2:
		return True
	city.removeGuildBranch(iData5)
	return True
