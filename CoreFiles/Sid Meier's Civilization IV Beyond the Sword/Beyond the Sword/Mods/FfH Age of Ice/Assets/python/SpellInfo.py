from CvPythonExtensions import *
from PyHelpers import *
import CvGameUtils
import Popup as PyPopup
import PyHelpers
gc = CyGlobalContext()

ACTION_NUMBER = -1
spellAction = {}
class SpellInfo: #storage class for all the stuff describing a spell. Makes lots of use of passing functions around, probably a bad idea.
	def __init__(self,name,cannotCastFunc,spellFunc):
		" void - (string name(must correspond to a CvActionInfo's name),bool func(bool bTestVisible) cannotCastFunc, void func() spellFunc)"
		CvGameUtils.doprint("for %s: %i" % (name,gc.getInfoTypeForString(name)))
		CvGameUtils.doprint("for %s: %s" % (name,str(gc.getAutomateInfo(gc.getInfoTypeForString(name)))))
		#whee, no getActionInfoIndex on Automate info, so we do this the ugly way
		delta = gc.getNumCommandInfos()+InterfaceModeTypes.NUM_INTERFACEMODE_TYPES+gc.getNumBuildInfos()+gc.getNumPromotionInfos()+gc.getNumUnitInfos()+gc.getNumReligionInfos()+gc.getNumSpecialistInfos()+gc.getNumBuildingInfos()+gc.getNumControlInfos()
		self.__action = gc.getInfoTypeForString(name) +delta
		self.__name = name
		self.__cannotCastFunc = cannotCastFunc
		self.__spellFunc = spellFunc
		spellAction[self.__action]=self
	def getName(self):
		return self.__name
	def getActionNumber(self):
		return self.__action
	def getCannotCastFunction(self):
		return self.__cannotCastFunc
	def getSpellFunction(self):
		return self.__spellFunc
	def isDisabled(self):
		return self.__cannotCastFunc(False)
	def isInvisible(self):
		return self.__cannotCastFunc(True)
	def cast(self):
		self.__spellFunc()
	def __str__(self):
		return self.__name
gc = CyGlobalContext()
#ArtFileMgr = CyArtFileMgr() # unfortunately ArtFileMgr isn't initialized at the time this runs. Maybe buttonFile should be replaced with a key for this class, extracted later

def getEffectInfo(name):
	for i in range(gc.getNumEffectInfos()):
		item=gc.getEffectInfo(i)
		if(item.getType()==name):
			return i

def getHurtAllFunc(amount):# returns a function that hurts everyone in the target square a given amount
	def inner(caster,targetPlot):
		for i in range(targetPlot.getNumUnits()):
			targetPlot.getUnit(i).changeDamage(amount,gc.getGame().getActivePlayer()) # not sure what the second arg does
		CyEngine().triggerEffect(getEffectInfo("EFFECT_SPELL"),targetPlot.getPoint())
	return inner

def alwaysFunc(bTestVisible):
	return False

def disabledFunc(bTestVisible):
	return not bTestVisible

def getDistRangeFunc(maxDist,mustBeInSight=True):#returns a function that gives a list of all the squares within a given distance
	plotDiffs = [] #[(dx,dy)]
	#precalculate the actual points, the inner function just moves them around
	for x in range(-maxDist,maxDist+1): #need to include both
		for y in range(-maxDist,maxDist+1): #need to include both
			if(x*x+y*y<=maxDist*maxDist): #simple range formula
				plotDiffs.append((x,y))
	def inner(caster):
		start=caster.plot()
		startX=start.getX()
		startY=start.getY()
		plots=[]
		map = gc.getMap()
		for delta in plotDiffs:#move each point to center on the caster
			x=startX+delta[0]
			y=startY+delta[1]
			if(mustBeInSight):
				#map.plot(x,y).isRevealed(PyPlayer(caster.getOwner()).getTeamID(),false) - this just checks if it has been seen - fog can still be there
				if(map.plot(x,y).isVisible(PyPlayer(caster.getOwner()).getTeamID(),false)):
					plots.append((x,y))
			else:
				plots.append((x,y))
		return plots
	return inner

def needUnitCheckInRange(rangeFunc):#returns a function that requires the user to cast inside the given range function + requires units of any player to be on the given square
	def inner(caster,targetPlot):
		return targetPlot.getNumUnits()>0 and (targetPlot.getX(),targetPlot.getY()) in rangeFunc(caster)
	return inner

def nothing():
	CyInterface().addImmediateMessage("casted spell","")
#	
spells = None #done in onInit - problem is that promotions need to be loaded

def init():
	global spells
	if not spells:
		spells = [
			SpellInfo("SPELL_BARRAGE",reqBarrage,spellBarrage),
			SpellInfo("SPELL_DROP_BLADE",reqDropBlade,spellDropBlade),
			SpellInfo("SPELL_DROP_CROSSGUARD",reqDropCrossguard,spellDropCrossguard),
			SpellInfo("SPELL_DROP_HILT",reqDropHilt,spellDropHilt),
			SpellInfo("SPELL_DROP_ORB",reqDropOrb,spellDropOrb),
			SpellInfo("SPELL_ESCAPE",reqEscape,spellEscape),
			SpellInfo("SPELL_FIREBALL",reqFireball,spellFireball),
			SpellInfo("SPELL_GET_BLADE",reqGetBlade,spellGetBlade),
			SpellInfo("SPELL_GET_CROSSGUARD",reqGetCrossguard,spellGetCrossguard),
			SpellInfo("SPELL_GET_HILT",reqGetHilt,spellGetHilt),
			SpellInfo("SPELL_GET_ORB",reqGetOrb,spellGetOrb),
			SpellInfo("SPELL_HASTE",reqHaste,spellHaste),
			SpellInfo("SPELL_PIKEMAN_JOIN",reqPikemanJoin,spellPikemanJoin),
			SpellInfo("SPELL_PIKEMAN_SPLIT",reqPikemanSplit,spellPikemanSplit),
			SpellInfo("SPELL_RAISE_SKELETON",reqRaiseSkeleton,spellRaiseSkeleton),
			SpellInfo("SPELL_REFORGE_THE_GODSLAYER",reqReforgeTheGodslayer,spellReforgeTheGodslayer),
			SpellInfo("SPELL_SET_TRAP",reqSetTrap,spellSetTrap),
			SpellInfo("SPELL_SUMMON_FLOATING_EYE",reqSummonFloatingEye,spellSummonFloatingEye),
			SpellInfo("SPELL_UPGRADE_ASSASSIN",reqUpgradeAssassin,spellUpgradeAssassin),
			SpellInfo("SPELL_UPGRADE_MACEMAN",reqUpgradeMaceman,spellUpgradeMaceman),
			SpellInfo("SPELL_UPGRADE_PIKEMAN",reqUpgradePikeman,spellUpgradePikeman),
			SpellInfo("SPELL_UPGRADE_RANGER",reqUpgradeRanger,spellUpgradeRanger),
			SpellInfo("SPELL_UPGRADE_SORCERESS",reqUpgradeSorceress,spellUpgradeSorceress),
			SpellInfo("SPELL_WARMTH",reqWarmth,spellWarmth)
			]

def getSpellFromAction(action):
	return spellAction.get(action)

def getSpells():
	return spells

def canCarry(pUnit):
	if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_BLADE'):
		return False
	if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_CROSSGUARD'):
		return False
	if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_HILT'):
		return False
	if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GIANT_SPIDER'):
		return False
	if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GALLEON'):
		return False
	if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_FIREBALL'):
		return False
	if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_FLOATING_EYE'):
		return False
	if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_ORB_OF_SUCELLUS'):
		return False
	return True

def canCast(pUnit):
	if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_HAS_CASTED')):
		return False
	return True

def doCast(pUnit):
	pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HAS_CASTED'), True)

def reqBarrage(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	pPlayer = gc.getPlayer(caster.getOwner())
	eTeam = gc.getTeam(pPlayer.getTeam())
	iDamageLimit = caster.collateralDamageLimit()
	bValid = False
	iX = caster.getX()
	iY = caster.getY()
	for iiX in range(iX-1, iX+2, 1):
		for iiY in range(iY-1, iY+2, 1):
			pPlot = CyMap().plot(iiX,iiY)
			if pPlot.getNumUnits() > 0:
				for i in range(pPlot.getNumUnits()):
					pUnit = pPlot.getUnit(i)
					e2Team = gc.getPlayer(pUnit.getOwner()).getTeam()
					if (eTeam.isAtWar(e2Team) and pUnit.getDamage() < iDamageLimit):
						bValid = True
	if caster.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ARCHER'):
		if (bTestVisible or (caster.isMadeAttack() == False and bValid)):
			return False
	return True

def spellBarrage():
	caster=CyInterface().getHeadSelectedUnit()
	caster.setMadeAttack(True)
	iPlayer = caster.getOwner()
	pPlayer = gc.getPlayer(iPlayer)
	eTeam = gc.getTeam(pPlayer.getTeam())
	iDamageLimit = caster.collateralDamageLimit()
	iMaxUnits = caster.collateralDamageMaxUnits()
	iX = caster.getX()
	iY = caster.getY()
	for iiX in range(iX-1, iX+2, 1):
		for iiY in range(iY-1, iY+2, 1):
			pPlot = CyMap().plot(iiX,iiY)
			if pPlot.getNumUnits() > 0:
				bHit = False
				for i in range(pPlot.getNumUnits()):
					pUnit = pPlot.getUnit(i)
					e2Team = gc.getPlayer(pUnit.getOwner()).getTeam()
					if (eTeam.isAtWar(e2Team) and pUnit.getDamage() < iDamageLimit and iMaxUnits > 0):
						iMaxUnits -= 1
						iDmg = CyGame().getSorenRandNum(8 * caster.baseCombatStr(), "Barrage")
						iDmg -= 2 * pUnit.baseCombatStr()
						if iDmg < 1:
							iDmg = 1
						if iDmg + pUnit.getDamage() > iDamageLimit:
							iDmg = iDamageLimit - pUnit.getDamage()
						pUnit.changeDamage(iDmg, iPlayer)
						sMessage = PyHelpers.PyInfo.UnitInfo(pUnit.getUnitType()).getDescription() + " " + CyTranslator().getText("TXT_KEY_MESSAGE_BARRAGE", (iDmg, ()))
						CyInterface().addMessage(iPlayer,True,25,sMessage,'AS2D_ARCHERY_BARRAGE',1,'Art/Interface/Buttons/Spells/Barrage.dds',ColorTypes(8),pUnit.getX(),pUnit.getY(),True,True)
						CyInterface().addMessage(pUnit.getOwner(),True,25,sMessage,'AS2D_ARCHERY_BARRAGE',1,'Art/Interface/Buttons/Spells/Barrage.dds',ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
						bHit = True
				if bHit == True:
					point = pPlot.getPoint()
					CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_DIGDIRT'),point)
	CyInterface().selectUnit(caster, true, true, true)

def reqDropBlade(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_BLADE')):
		return False
	return True

def spellDropBlade():
	caster=CyInterface().getHeadSelectedUnit()
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_BLADE'), False)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_GODSLAYER_BLADE'), caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	CyInterface().selectUnit(newUnit, true, true, true)

def reqDropCrossguard(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_CROSSGUARD')):
		return False
	return True

def spellDropCrossguard():
	caster=CyInterface().getHeadSelectedUnit()
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_CROSSGUARD'), False)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_GODSLAYER_CROSSGUARD'), caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	CyInterface().selectUnit(newUnit, true, true, true)

def reqDropHilt(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_HILT')):
		return False
	return True

def spellDropHilt():
	caster=CyInterface().getHeadSelectedUnit()
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_HILT'), False)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_GODSLAYER_HILT'), caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	CyInterface().selectUnit(newUnit, true, true, true)

def reqDropOrb(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ORB_OF_SUCELLUS')):
		return False
	return True

def spellDropOrb():
	caster=CyInterface().getHeadSelectedUnit()
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ORB_OF_SUCELLUS'), False)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_ORB_OF_SUCELLUS'), caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	CyInterface().selectUnit(newUnit, true, true, true)

def reqEscape(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.getUnitType() == gc.getInfoTypeForString('UNIT_CAERBULIN_ASSASSIN'):
		if (bTestVisible or canCast(caster)):
			return False
	return True

def spellEscape():
	caster=CyInterface().getHeadSelectedUnit()
	doCast(caster)
	pPlayer = gc.getPlayer(caster.getOwner())
	pCity = pPlayer.getCapitalCity()
	caster.setXY(pCity.getX(), pCity.getY(), true, true, true)
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	CyInterface().selectUnit(caster, true, true, true)

def reqFireball(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.getUnitType() == gc.getInfoTypeForString('UNIT_EPONA_SORCERESS'):
		if (bTestVisible or canCast(caster)):
			return False
	return True

def spellFireball():
	caster=CyInterface().getHeadSelectedUnit()
	doCast(caster)
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_FIREBALL'), caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT1')):
		newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT1'), true)
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT2')):
		newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT2'), true)
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT3')):
		newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT3'), true)
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT4')):
		newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT4'), true)
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT5')):
		newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT5'), true)
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT6')):
		newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT6'), true)
	CyInterface().selectUnit(newUnit, true, true, true)

def reqGetBlade(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	if canCarry(caster):
		for i in range(pPlot.getNumUnits()):
			pUnit = pPlot.getUnit(i)
			if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_BLADE'):
				return False
	return True

def spellGetBlade():
	caster=CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	for i in range(pPlot.getNumUnits()):
		pUnit = pPlot.getUnit(i)
		if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_BLADE'):
			pTarget = pUnit
	pPlayer = gc.getPlayer(caster.getOwner())
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_BLADE'), True)
	CyInterface().selectUnit(pTarget, true, true, true)
	pTarget.kill(True,0)

def reqGetCrossguard(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	if canCarry(caster):
		for i in range(pPlot.getNumUnits()):
			pUnit = pPlot.getUnit(i)
			if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_CROSSGUARD'):
				return False
	return True

def spellGetCrossguard():
	caster=CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	for i in range(pPlot.getNumUnits()):
		pUnit = pPlot.getUnit(i)
		if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_CROSSGUARD'):
			pTarget = pUnit
	pPlayer = gc.getPlayer(caster.getOwner())
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_CROSSGUARD'), True)
	CyInterface().selectUnit(pTarget, true, true, true)
	pTarget.kill(True,0)

def reqGetHilt(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	if canCarry(caster):
		for i in range(pPlot.getNumUnits()):
			pUnit = pPlot.getUnit(i)
			if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_HILT'):
				return False
	return True

def spellGetHilt():
	caster=CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	for i in range(pPlot.getNumUnits()):
		pUnit = pPlot.getUnit(i)
		if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_HILT'):
			pTarget = pUnit
	pPlayer = gc.getPlayer(caster.getOwner())
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_HILT'), True)
	CyInterface().selectUnit(pTarget, true, true, true)
	pTarget.kill(True,0)

def reqGetOrb(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	if canCarry(caster):
		for i in range(pPlot.getNumUnits()):
			pUnit = pPlot.getUnit(i)
			if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_ORB_OF_SUCELLUS'):
				return False
	return True

def spellGetOrb():
	caster=CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	for i in range(pPlot.getNumUnits()):
		pUnit = pPlot.getUnit(i)
		if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_ORB_OF_SUCELLUS'):
			pTarget = pUnit
	pPlayer = gc.getPlayer(caster.getOwner())
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ORB_OF_SUCELLUS'), True)
	CyInterface().selectUnit(pTarget, true, true, true)
	pTarget.kill(True,0)

def reqHaste(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MARK_OF_THE_BAT')):
		if (bTestVisible or canCast(caster)):
			return False
	return True

def spellHaste():
	caster=CyInterface().getHeadSelectedUnit()
	doCast(caster)
	pPlot = caster.plot()
	for i in range(pPlot.getNumUnits()):
		pUnit = pPlot.getUnit(i)
		if pUnit.baseMoves() > 0:
			pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HASTED'), True)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	CyInterface().selectUnit(caster, true, true, true)

def reqPikemanJoin(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	iCount = 0
	for i in range(pPlot.getNumUnits()):
		pUnit = pPlot.getUnit(i)
		if (pUnit.getUnitClassType() == gc.getInfoTypeForString('UNITCLASS_PIKEMAN') and pUnit.getUnitType() != gc.getInfoTypeForString('UNIT_PIKEMAN5') and pUnit.getOwner() == caster.getOwner() and pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_HAS_CASTED')) == False):
			iCount = iCount + 1
	if caster.getUnitType() == gc.getInfoTypeForString('UNIT_PIKEMAN1'):
		if (bTestVisible or (canCast(caster) and iCount > 1)):
			return False
	return True

def spellPikemanJoin():
	caster=CyInterface().getHeadSelectedUnit()
	doCast(caster)
	pPlot = caster.plot()
	iBestStr = 0
	for i in range(pPlot.getNumUnits()):
		pUnit = pPlot.getUnit(i)
		if (pUnit.getUnitClassType() == gc.getInfoTypeForString('UNITCLASS_PIKEMAN') and pUnit.getUnitType() != gc.getInfoTypeForString('UNIT_PIKEMAN5') and pUnit.getOwner() == caster.getOwner() and pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_HAS_CASTED')) == False):
			if pUnit.baseCombatStr() > iBestStr:
				pTarget = pUnit
				iBestStr = pUnit.baseCombatStr()
	iUnit = -1
	if pTarget.getUnitType() == gc.getInfoTypeForString('UNIT_PIKEMAN1'):
		iUnit = gc.getInfoTypeForString('UNIT_PIKEMAN2')
	if pTarget.getUnitType() == gc.getInfoTypeForString('UNIT_PIKEMAN2'):
		iUnit = gc.getInfoTypeForString('UNIT_PIKEMAN3')
	if pTarget.getUnitType() == gc.getInfoTypeForString('UNIT_PIKEMAN3'):
		iUnit = gc.getInfoTypeForString('UNIT_PIKEMAN4')
	if pTarget.getUnitType() == gc.getInfoTypeForString('UNIT_PIKEMAN4'):
		iUnit = gc.getInfoTypeForString('UNIT_PIKEMAN5')
	pPlayer = gc.getPlayer(caster.getOwner())
	if iUnit != -1:
		newUnit = pPlayer.initUnit(iUnit, caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit.convert(pTarget)
		newUnit.setDamage(newUnit.getDamage() + (pTarget.getDamage()/2), True)
		for iCount in range(gc.getNumPromotionInfos()):
			if caster.isHasPromotion(iCount):
				newUnit.setHasPromotion(iCount, True)
		caster.kill(True,0)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	CyInterface().selectUnit(newUnit, true, true, true)

def reqPikemanSplit(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if (caster.getUnitClassType() == gc.getInfoTypeForString('UNITCLASS_PIKEMAN') and caster.getUnitType() != gc.getInfoTypeForString('UNIT_PIKEMAN1')):
		return False
	return True

def spellPikemanSplit():
	caster=CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	iUnit = -1
	if caster.getUnitType() == gc.getInfoTypeForString('UNIT_PIKEMAN5'):
		iUnit = gc.getInfoTypeForString('UNIT_PIKEMAN4')
	if caster.getUnitType() == gc.getInfoTypeForString('UNIT_PIKEMAN4'):
		iUnit = gc.getInfoTypeForString('UNIT_PIKEMAN3')
	if caster.getUnitType() == gc.getInfoTypeForString('UNIT_PIKEMAN3'):
		iUnit = gc.getInfoTypeForString('UNIT_PIKEMAN2')
	if caster.getUnitType() == gc.getInfoTypeForString('UNIT_PIKEMAN2'):
		iUnit = gc.getInfoTypeForString('UNIT_PIKEMAN1')
	pPlayer = gc.getPlayer(caster.getOwner())
	if iUnit != -1:
		newUnit = pPlayer.initUnit(iUnit, caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit.setMadeAttack(True)
		newUnit.convert(caster)
		newUnit2 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_PIKEMAN1'), caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit2.setDamage(newUnit.getDamage(), True)
		newUnit2.setMadeAttack(True)
		newUnit2.setMoves(newUnit.getMoves())
		caster.kill(True,0)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	CyInterface().selectUnit(newUnit, true, true, true)

def reqRaiseSkeleton(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	iMarkoftheRaven = gc.getInfoTypeForString('PROMOTION_MARK_OF_THE_RAVEN')
	if caster.isHasPromotion(iMarkoftheRaven):
		pPlayer = gc.getPlayer(caster.getOwner())
		py = PyPlayer(caster.getOwner())
		iNum = 0
		for pUnit in py.getUnitList():
			if pUnit.isHasPromotion(iMarkoftheRaven):
				iNum = iNum + 1
		if (bTestVisible or (canCast(caster) and pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_SKELETON')) < iNum)):
			return False
	return True

def spellRaiseSkeleton():
	caster=CyInterface().getHeadSelectedUnit()
	doCast(caster)
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_SKELETON'), caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	newUnit.setMadeAttack(True)
	CyInterface().selectUnit(newUnit, true, true, true)

def reqReforgeTheGodslayer(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if (caster.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_BLADE') or caster.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_CROSSGUARD') or caster.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_HILT')):
		return True
	if caster.getUnitClassType() == gc.getInfoTypeForString('UNITCLASS_KYLORIN'):
		return True
	pPlot = caster.plot()
	if pPlot.isCity() == False:
		return True
	pCity = pPlot.getPlotCity()
	if pCity.getNumBuilding(gc.getInfoTypeForString('BUILDING_FORGE')) == 0:
		return True
	bBlade = False
	bCrossguard = False
	bHilt = False
	for i in range(pPlot.getNumUnits()):
		pUnit = pPlot.getUnit(i)
		if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_BLADE'):
			bBlade = True
		if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_CROSSGUARD'):
			bCrossguard = True
		if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_HILT'):
			bHilt = True
		if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_BLADE')):
			bBlade = True
		if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_CROSSGUARD')):
			bCrossguard = True
		if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_HILT')):
			bHilt = True
	if (bBlade and bCrossguard and bHilt):
		return False
	return True

def spellReforgeTheGodslayer():
	caster=CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	for i in range(pPlot.getNumUnits()):
		pUnit = pPlot.getUnit(i)
		if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_BLADE')):
			pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_BLADE'), False)
		if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_CROSSGUARD')):
			pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_CROSSGUARD'), False)
		if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_HILT')):
			pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_HILT'), False)
		if (pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_BLADE') or pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_CROSSGUARD') or pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_HILT')):
			pUnit.kill(True,0)
	pPlayer = gc.getPlayer(caster.getOwner())
	point = pPlot.getPoint()
	bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
	iHandicap = CyGame().getHandicapType()
	if iHandicap >= 1:
		for i in range(4):
			if i == 0:
				iUnit = gc.getInfoTypeForString('UNIT_FROST_GIANT')
			if i == 1:
				iUnit = gc.getInfoTypeForString('UNIT_MAMMOTH_RIDER')
			if i == 2:
				iUnit = gc.getInfoTypeForString('UNIT_ICE_GOLEM')
			if i == 3:
				iUnit = gc.getInfoTypeForString('UNIT_MACEMAN')
			for ii in range((iHandicap+1) / 2):
				newUnit2 = bPlayer.initUnit(iUnit, 2, 17, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
				if CyGame().getHandicapType() >= 2:
					newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_MOBILITY'), true)
				if CyGame().getHandicapType() >= 3:
					newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT1'), true)
				if CyGame().getHandicapType() >= 4:
					newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT2'), true)
				if CyGame().getHandicapType() >= 5:
					newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT3'), true)
				if CyGame().getHandicapType() >= 6:
					newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT4'), true)
				if CyGame().getHandicapType() >= 7:
					newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT5'), true)
				if CyGame().getHandicapType() >= 8:
					newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMBAT6'), true)
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	iUnit = gc.getInfoTypeForString('UNIT_KYLORIN')
	iStag = gc.getInfoTypeForString('UNITCLASS_STAG')
	if (bPlayer.getUnitClassCount(iStag) == 1 and CyGame().getUnitClassCreatedCount(iStag) > 1):
		iUnit = gc.getInfoTypeForString('UNIT_KYLORIN_MOUNTED')
		py = PyPlayer(gc.getBARBARIAN_PLAYER())
		for pUnit in py.getUnitList():
			if pUnit.getUnitClassType() == iStag:
				pUnit.kill(True,0)
		szText = CyTranslator().getText("TXT_KEY_POPUP_STAG_RETURNS",())
		szTitle = CyGameTextMgr().getTimeStr(CyGame().getGameTurn(), false)
		popup = PyPopup.PyPopup(-1)
		popup.setHeaderString(szTitle)
		popup.setBodyString(szText)
		popup.launch(true, PopupStates.POPUPSTATE_QUEUED)
	newUnit = pPlayer.initUnit(iUnit, caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	CyInterface().selectUnit(newUnit, true, true, true)
	popup = PyPopup.PyPopup(-1)
	popup.setHeaderString(CyGameTextMgr().getTimeStr(CyGame().getGameTurn(), false))
	popup.setBodyString(CyTranslator().getText("TXT_KEY_POPUP_KYLORIN_CREATED",()))
	popup.launch(true, PopupStates.POPUPSTATE_QUEUED)

def reqSetTrap(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.getUnitType() != gc.getInfoTypeForString('UNIT_CAERBULIN_RANGER'):
		return True
	pPlot = caster.plot()
	if pPlot.getFeatureType() != -1:
		return True
	iCount = 0
	for i in range (CyMap().numPlots()):
		pPlot = CyMap().plotByIndex(i)
		if pPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_TRAP'):
			iCount = iCount + 1
	if iCount >= 3:
		return True
	return False

def spellSetTrap():
	caster=CyInterface().getHeadSelectedUnit()
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	pPlot.setFeatureType(gc.getInfoTypeForString('FEATURE_TRAP'), -1)

def reqSummonFloatingEye(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MARK_OF_THE_RABBIT')):
		if (bTestVisible or canCast(caster)):
			return False
	return True

def spellSummonFloatingEye():
	caster=CyInterface().getHeadSelectedUnit()
	doCast(caster)
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_FLOATING_EYE'), caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	CyInterface().selectUnit(newUnit, true, true, true)

def reqUpgradeAssassin(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_CAERBULIN')
	iTech = gc.getInfoTypeForString('TECH_STEALTH')
	if caster.getUnitType() == iUnit:
		pPlayer = gc.getPlayer(caster.getOwner())
		eTeam = gc.getTeam(pPlayer.getTeam())
		if (bTestVisible or eTeam.isHasTech(iTech)):
			return False
	return True

def spellUpgradeAssassin():
	caster=CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_CAERBULIN_ASSASSIN')
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	newUnit = pPlayer.initUnit(iUnit, caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	newUnit.convert(caster)
	caster.kill(True,0)

def reqUpgradeMaceman(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_BELENUS')
	iTech = gc.getInfoTypeForString('TECH_IRON_WORKING')
	if caster.getUnitType() == iUnit:
		pPlayer = gc.getPlayer(caster.getOwner())
		eTeam = gc.getTeam(pPlayer.getTeam())
		if (bTestVisible or eTeam.isHasTech(iTech)):
			return False
	return True

def spellUpgradeMaceman():
	caster=CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_BELENUS_MACEMAN')
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	newUnit = pPlayer.initUnit(iUnit, caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	newUnit.convert(caster)
	caster.kill(True,0)

def reqUpgradePikeman(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_BELENUS')
	iTech = gc.getInfoTypeForString('TECH_METAL_CASTING')
	if caster.getUnitType() == iUnit:
		pPlayer = gc.getPlayer(caster.getOwner())
		eTeam = gc.getTeam(pPlayer.getTeam())
		if (bTestVisible or eTeam.isHasTech(iTech)):
			return False
	return True

def spellUpgradePikeman():
	caster=CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_BELENUS_PIKEMAN')
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	newUnit = pPlayer.initUnit(iUnit, caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	newUnit.convert(caster)
	caster.kill(True,0)

def reqUpgradeRanger(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_CAERBULIN')
	iTech = gc.getInfoTypeForString('TECH_ANIMAL_HANDLING')
	if caster.getUnitType() == iUnit:
		pPlayer = gc.getPlayer(caster.getOwner())
		eTeam = gc.getTeam(pPlayer.getTeam())
		if (bTestVisible or eTeam.isHasTech(iTech)):
			return False
	return True

def spellUpgradeRanger():
	caster=CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_CAERBULIN_RANGER')
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	newUnit = pPlayer.initUnit(iUnit, caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	newUnit.convert(caster)
	caster.kill(True,0)

def reqUpgradeSorceress(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_EPONA')
	iTech = gc.getInfoTypeForString('TECH_KNOWLEDGE_OF_THE_ETHER')
	if caster.getUnitType() == iUnit:
		pPlayer = gc.getPlayer(caster.getOwner())
		eTeam = gc.getTeam(pPlayer.getTeam())
		if (bTestVisible or eTeam.isHasTech(iTech)):
			return False
	return True

def spellUpgradeSorceress():
	caster=CyInterface().getHeadSelectedUnit()
	iUnit = gc.getInfoTypeForString('UNIT_EPONA_SORCERESS')
	pPlayer = gc.getPlayer(caster.getOwner())
	pPlot = caster.plot()
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	newUnit = pPlayer.initUnit(iUnit, caster.getX(), caster.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
	newUnit.convert(caster)
	caster.kill(True,0)

def reqWarmth(bTestVisible):
	caster = CyInterface().getHeadSelectedUnit()
	if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MARK_OF_THE_SCORPION')):
		pPlot = caster.plot()
		if (bTestVisible or (canCast(caster) and pPlot.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_BLIZZARD'))):
			return False
	return True

def spellWarmth():
	caster=CyInterface().getHeadSelectedUnit()
	doCast(caster)
	pPlot = caster.plot()
	pPlot.setImprovementType(-1)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
	CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
	CyInterface().selectUnit(caster, true, true, true)
