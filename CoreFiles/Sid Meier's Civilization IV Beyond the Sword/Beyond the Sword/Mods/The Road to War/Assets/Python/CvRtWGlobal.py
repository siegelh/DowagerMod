## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## 
## CvRtWGlobal


from CvPythonExtensions import *
from CvScreenEnums import *
from PyHelpers import PyPlayer
import CvEventManager
import CvUtil
import Popup as PyPopup
import pickle
import sys
import CvWonderMovieScreen
	
gc = CyGlobalContext()
game = CyGame()
localText = CyTranslator()
DefaultUnitAI = UnitAITypes.NO_UNITAI

# The main bits
###################################################
class CvRtWGlobal:
	def __init__(self):
                return
                
# RtW Global Setup
###################################################
        def globalInit(self):
		# Global setup civs
		self.pGermanyID = 0
		self.pItalyID = 1
		self.pJapanID = 2
		self.pChinaID = 3
		self.pFranceID = 4
		self.pEnglandID = 5
		self.pUSAID = 6
		self.pUSSRID = 7
		self.pArabiaID = 8
		self.pAustriaID = 9
		self.pAustraliaID = 10
		self.pBalticStatesID = 11
		self.pBrazilID = 12
		self.pCanadaID = 13
		self.pCentralAmericaID = 14
		self.pCzechID = 15
		self.pEastBalkanID = 16
		self.pFacistIberiaID = 17
		self.pFinlandID = 18
		self.pIrelandID = 19
		self.pLowCountriesID = 20
		self.pMexicoID = 21
		self.pMongoliaID = 22
		self.pNewZealandID = 23
		self.pNorwayID = 24
		self.pPersiaID = 25
		self.pPhilippinesID = 26
		self.pPolandID = 27
		self.pRepubIberiaID = 28
		self.pSiamID = 29
		self.pSouthAfricaID = 30
		self.pSouthAmericaID = 31
		self.pSwedenID = 32
		self.pTurkeyID = 33
		self.pWestBalkanID = 34
		self.pVichyFranceID = 35

                # Global Teams
                self.pGermanyTeam = gc.getTeam(gc.getPlayer(self.pGermanyID).getTeam())
		self.pItalyTeam = gc.getTeam(gc.getPlayer(self.pItalyID).getTeam())
		self.pJapanTeam = gc.getTeam(gc.getPlayer(self.pJapanID).getTeam())
		self.pChinaTeam = gc.getTeam(gc.getPlayer(self.pChinaID).getTeam())
		self.pFranceTeam = gc.getTeam(gc.getPlayer(self.pFranceID).getTeam())
		self.pEnglandTeam = gc.getTeam(gc.getPlayer(self.pEnglandID).getTeam())
		self.pUSATeam = gc.getTeam(gc.getPlayer(self.pUSAID).getTeam())
		self.pUSSRTeam = gc.getTeam(gc.getPlayer(self.pUSSRID).getTeam())
		self.pArabiaTeam = gc.getTeam(gc.getPlayer(self.pArabiaID).getTeam())
		self.pAustriaTeam = gc.getTeam(gc.getPlayer(self.pAustriaID).getTeam())
		self.pAustraliaTeam = gc.getTeam(gc.getPlayer(self.pAustraliaID).getTeam())
		self.pBalticStatesTeam = gc.getTeam(gc.getPlayer(self.pBalticStatesID).getTeam())
		self.pBrazilTeam = gc.getTeam(gc.getPlayer(self.pBrazilID).getTeam())
		self.pCanadaTeam = gc.getTeam(gc.getPlayer(self.pCanadaID).getTeam())
		self.pCentralAmericaTeam = gc.getTeam(gc.getPlayer(self.pCentralAmericaID).getTeam())
		self.pCzechTeam = gc.getTeam(gc.getPlayer(self.pCzechID).getTeam())
		self.pEastBalkanTeam = gc.getTeam(gc.getPlayer(self.pEastBalkanID).getTeam())
		self.pFacistIberiaTeam = gc.getTeam(gc.getPlayer(self.pFacistIberiaID).getTeam())
		self.pFinlandTeam = gc.getTeam(gc.getPlayer(self.pFinlandID).getTeam())
		self.pIrelandTeam = gc.getTeam(gc.getPlayer(self.pIrelandID).getTeam())
		self.pLowCountriesTeam = gc.getTeam(gc.getPlayer(self.pLowCountriesID).getTeam())
		self.pMexicoTeam = gc.getTeam(gc.getPlayer(self.pMexicoID).getTeam())
		self.pMongoliaTeam = gc.getTeam(gc.getPlayer(self.pMongoliaID).getTeam())
		self.pNewZealandTeam = gc.getTeam(gc.getPlayer(self.pNewZealandID).getTeam())
		self.pNorwayTeam = gc.getTeam(gc.getPlayer(self.pNorwayID).getTeam())
		self.pPersiaTeam = gc.getTeam(gc.getPlayer(self.pPersiaID).getTeam())
		self.pPhilippinesTeam = gc.getTeam(gc.getPlayer(self.pPhilippinesID).getTeam())
		self.pPolandTeam = gc.getTeam(gc.getPlayer(self.pPolandID).getTeam())
		self.pRepubIberiaTeam = gc.getTeam(gc.getPlayer(self.pRepubIberiaID).getTeam())
		self.pSiamTeam = gc.getTeam(gc.getPlayer(self.pSiamID).getTeam())
		self.pSouthAfricaTeam = gc.getTeam(gc.getPlayer(self.pSouthAfricaID).getTeam())
		self.pSouthAmericaTeam = gc.getTeam(gc.getPlayer(self.pSouthAmericaID).getTeam())
		self.pSwedenTeam = gc.getTeam(gc.getPlayer(self.pSwedenID).getTeam())
		self.pTurkeyTeam = gc.getTeam(gc.getPlayer(self.pTurkeyID).getTeam())
		self.pWestBalkanTeam = gc.getTeam(gc.getPlayer(self.pWestBalkanID).getTeam())
		self.pVichyFranceTeam = gc.getTeam(gc.getPlayer(self.pVichyFranceID).getTeam())

                # Define cities
                self.cReykjavik = gc.getMap().plot(3,76).getPlotCity()
                self.cNouakchott = gc.getMap().plot(5,39).getPlotCity()
                self.cTenerife = gc.getMap().plot(5,45).getPlotCity()
                self.cBoujdour = gc.getMap().plot(6,43).getPlotCity()
                self.cFreetown = gc.getMap().plot(7,33).getPlotCity()
                self.cLisbon = gc.getMap().plot(8,52).getPlotCity()
                self.cPorto = gc.getMap().plot(8,54).getPlotCity()
                self.cDublin = gc.getMap().plot(9,67).getPlotCity()
                self.cBelfast = gc.getMap().plot(9,69).getPlotCity()
                self.cRabat = gc.getMap().plot(10,47).getPlotCity()
                self.cOviedo = gc.getMap().plot(10,56).getPlotCity()
                self.cBrest = gc.getMap().plot(10,61).getPlotCity()
                self.cGibralter = gc.getMap().plot(11,50).getPlotCity()
                self.cPlymouth = gc.getMap().plot(11,64).getPlotCity()
                self.cCardiff = gc.getMap().plot(11,66).getPlotCity()
                self.cMadrid = gc.getMap().plot(12,54).getPlotCity()
                self.cNantes = gc.getMap().plot(12,60).getPlotCity()
                self.cEdinburgh = gc.getMap().plot(12,70).getPlotCity()
                self.cYamoussoukro = gc.getMap().plot(13,30).getPlotCity()
                self.cBamako = gc.getMap().plot(13,36).getPlotCity()
                self.cBordaeux = gc.getMap().plot(13,58).getPlotCity()
                self.cSunderland = gc.getMap().plot(13,68).getPlotCity()
                self.cLondon = gc.getMap().plot(14,65).getPlotCity()
                self.cInSalah = gc.getMap().plot(15,41).getPlotCity()
                self.cAlgiers = gc.getMap().plot(15,48).getPlotCity()
                self.cCartagena = gc.getMap().plot(15,52).getPlotCity()
                self.cBarcelona = gc.getMap().plot(15,55).getPlotCity()
                self.cToulouse = gc.getMap().plot(16,57).getPlotCity()
                self.cParis = gc.getMap().plot(16,61).getPlotCity()
                self.cCalais = gc.getMap().plot(16,63).getPlotCity()
                self.cReims = gc.getMap().plot(18,62).getPlotCity()
                self.cMarseille = gc.getMap().plot(19,56).getPlotCity()
                self.cLyon = gc.getMap().plot(19,59).getPlotCity()
                self.cBrussels = gc.getMap().plot(19,64).getPlotCity()
                self.cAmsterdam = gc.getMap().plot(19,66).getPlotCity()
                self.cStavanger = gc.getMap().plot(19,72).getPlotCity()
                self.cStrasbourg = gc.getMap().plot(20,61).getPlotCity()
                self.cCagliari = gc.getMap().plot(21,51).getPlotCity()
                self.cAjaccio = gc.getMap().plot(21,54).getPlotCity()
                self.cGenoa = gc.getMap().plot(21,57).getPlotCity()
                self.cCologne = gc.getMap().plot(21,63).getPlotCity()
                self.cTunis = gc.getMap().plot(22,49).getPlotCity()
                self.cStuttgart = gc.getMap().plot(22,61).getPlotCity()
                self.cHannover = gc.getMap().plot(22,64).getPlotCity()
                self.cKiel = gc.getMap().plot(22,66).getPlotCity()
                self.cAbuja = gc.getMap().plot(23,31).getPlotCity()
                self.cMilan = gc.getMap().plot(23,58).getPlotCity()
                self.cOslo = gc.getMap().plot(23,73).getPlotCity()
                self.cTrondheim = gc.getMap().plot(23,76).getPlotCity()
                self.cTripoli = gc.getMap().plot(24,45).getPlotCity()
                self.cRome = gc.getMap().plot(24,54).getPlotCity()
                self.cInnsbruck = gc.getMap().plot(24,60).getPlotCity()
                self.cFrankfurt = gc.getMap().plot(24,63).getPlotCity()
                self.cRostock = gc.getMap().plot(24,66).getPlotCity()
                self.cCopenhagen = gc.getMap().plot(24,68).getPlotCity()
                self.cLibreville = gc.getMap().plot(25,25).getPlotCity()
                self.cSabha = gc.getMap().plot(25,41).getPlotCity()
                self.cPalermo = gc.getMap().plot(25,50).getPlotCity()
                self.cVenice = gc.getMap().plot(25,58).getPlotCity()
                self.cMunich = gc.getMap().plot(25,61).getPlotCity()
                self.cBerlin = gc.getMap().plot(26,65).getPlotCity()
                self.cMoIRana = gc.getMap().plot(26,79).getPlotCity()
                self.cVienna = gc.getMap().plot(27,60).getPlotCity()
                self.cPrague = gc.getMap().plot(27,62).getPlotCity()
                self.cKalmar = gc.getMap().plot(27,69).getPlotCity()
                self.cLuanda = gc.getMap().plot(28,17).getPlotCity()
                self.cKinshasa = gc.getMap().plot(28,22).getPlotCity()
                self.cNdjamena = gc.getMap().plot(28,33).getPlotCity()
                self.cBrindisi = gc.getMap().plot(28,53).getPlotCity()
                self.cZagreb = gc.getMap().plot(28,58).getPlotCity()
                self.cWroclaw = gc.getMap().plot(28,64).getPlotCity()
                self.cKoszalin = gc.getMap().plot(28,66).getPlotCity()
                self.cTirane = gc.getMap().plot(29,55).getPlotCity()
                self.cBratislava = gc.getMap().plot(29,61).getPlotCity()
                self.cStockholm = gc.getMap().plot(29,73).getPlotCity()
                self.cCapeTown = gc.getMap().plot(30,5).getPlotCity()
                self.cAlKufrah = gc.getMap().plot(30,39).getPlotCity()
                self.cBanghazi = gc.getMap().plot(30,45).getPlotCity()
                self.cBelgrade = gc.getMap().plot(30,57).getPlotCity()
                self.cBudapest = gc.getMap().plot(30,59).getPlotCity()
                self.cDanzig = gc.getMap().plot(30,67).getPlotCity()
                self.cVisby = gc.getMap().plot(30,70).getPlotCity()
                self.cLulea = gc.getMap().plot(31,77).getPlotCity()
                self.cWindhoek = gc.getMap().plot(32,12).getPlotCity()
                self.cThessaloniki = gc.getMap().plot(32,55).getPlotCity()
                self.cKrakow = gc.getMap().plot(32,62).getPlotCity()
                self.cKisangani = gc.getMap().plot(33,26).getPlotCity()
                self.cIraklion = gc.getMap().plot(33,48).getPlotCity()
                self.cAthens = gc.getMap().plot(33,52).getPlotCity()
                self.cWarsaw = gc.getMap().plot(33,65).getPlotCity()
                self.cKonigsburg = gc.getMap().plot(33,67).getPlotCity()
                self.cVaasa = gc.getMap().plot(33,75).getPlotCity()
                self.cLusaka = gc.getMap().plot(35,17).getPlotCity()
                self.cAlexandria = gc.getMap().plot(35,45).getPlotCity()
                self.cBucharest = gc.getMap().plot(35,58).getPlotCity()
                self.cLviv = gc.getMap().plot(35,62).getPlotCity()
                self.cRiga = gc.getMap().plot(35,69).getPlotCity()
                self.cOulu = gc.getMap().plot(35,77).getPlotCity()
                self.cPretoria = gc.getMap().plot(36,9).getPlotCity()
                self.cIstanbul = gc.getMap().plot(36,56).getPlotCity()
                self.cVilnius = gc.getMap().plot(36,66).getPlotCity()
                self.cTallinn = gc.getMap().plot(36,71).getPlotCity()
                self.cAntalya = gc.getMap().plot(37,51).getPlotCity()
                self.cChisnau = gc.getMap().plot(37,60).getPlotCity()
                self.cHelsinki = gc.getMap().plot(37,73).getPlotCity()
                self.cKhartoum = gc.getMap().plot(38,35).getPlotCity()
                self.cAswan = gc.getMap().plot(38,39).getPlotCity()
                self.cMinsk = gc.getMap().plot(38,65).getPlotCity()
                self.cNicosia = gc.getMap().plot(39,49).getPlotCity()
                self.cAnkara = gc.getMap().plot(39,54).getPlotCity()
                self.cKiev = gc.getMap().plot(39,63).getPlotCity()
                self.cLenningrad = gc.getMap().plot(39,72).getPlotCity()
                self.cMaputo = gc.getMap().plot(40,10).getPlotCity()
                self.cVitsyebsk = gc.getMap().plot(40,68).getPlotCity()
                self.cQuelimane = gc.getMap().plot(42,14).getPlotCity()
                self.cDarEsSalaam = gc.getMap().plot(42,21).getPlotCity()
                self.cAddisAbaba = gc.getMap().plot(42,31).getPlotCity()
                self.cJerusalem = gc.getMap().plot(42,46).getPlotCity()
                self.cTartus = gc.getMap().plot(42,50).getPlotCity()
                self.cSevastopol = gc.getMap().plot(42,59).getPlotCity()
                self.cMecca = gc.getMap().plot(43,38).getPlotCity()
                self.cMoscow = gc.getMap().plot(44,67).getPlotCity()
                self.cTrabzon = gc.getMap().plot(45,55).getPlotCity()
                self.cRostov = gc.getMap().plot(45,60).getPlotCity()
                self.cVologda = gc.getMap().plot(45,72).getPlotCity()
                self.cMogadishu = gc.getMap().plot(46,26).getPlotCity()
                self.cSana = gc.getMap().plot(46,35).getPlotCity()
                self.cArkhangelsk = gc.getMap().plot(46,76).getPlotCity()
                self.cVan = gc.getMap().plot(47,52).getPlotCity()
                self.cToliara = gc.getMap().plot(48,11).getPlotCity()
                self.cAntananarivo = gc.getMap().plot(49,15).getPlotCity()
                self.cRiyadh = gc.getMap().plot(49,41).getPlotCity()
                self.cBaghdad = gc.getMap().plot(49,48).getPlotCity()
                self.cStalingrad = gc.getMap().plot(49,62).getPlotCity()
                self.cAlMukalla = gc.getMap().plot(50,34).getPlotCity()
                self.cKuwaitCity = gc.getMap().plot(52,45).getPlotCity()
                self.cBaku = gc.getMap().plot(52,55).getPlotCity()
                self.cTehran = gc.getMap().plot(53,51).getPlotCity()
                self.cKazan = gc.getMap().plot(53,68).getPlotCity()
                self.cSyktyvkar = gc.getMap().plot(53,72).getPlotCity()
                self.cDaha = gc.getMap().plot(55,41).getPlotCity()
                self.cGuryev = gc.getMap().plot(55,61).getPlotCity()
                self.cBandarAbbas = gc.getMap().plot(58,44).getPlotCity()
                self.cAshkhabad = gc.getMap().plot(58,53).getPlotCity()
                self.cMuscat = gc.getMap().plot(59,39).getPlotCity()
                self.cMashhad = gc.getMap().plot(59,50).getPlotCity()
                self.cChelyaninsk = gc.getMap().plot(60,65).getPlotCity()
                self.cSverdlovsk = gc.getMap().plot(61,70).getPlotCity()
                self.cKarachi = gc.getMap().plot(62,43).getPlotCity()
                self.cDushanbe = gc.getMap().plot(63,55).getPlotCity()
                self.cKabul = gc.getMap().plot(64,50).getPlotCity()
                self.cFrunze = gc.getMap().plot(65,58).getPlotCity()
                self.cGoa = gc.getMap().plot(67,37).getPlotCity()
                self.cIslamabad = gc.getMap().plot(67,50).getPlotCity()
                self.cKaraganda = gc.getMap().plot(67,66).getPlotCity()
                self.cOmsk = gc.getMap().plot(68,69).getPlotCity()
                self.cBishkek = gc.getMap().plot(69,61).getPlotCity()
                self.cBhopal = gc.getMap().plot(70,43).getPlotCity()
                self.cDelhi = gc.getMap().plot(71,48).getPlotCity()
                self.cMadras = gc.getMap().plot(72,34).getPlotCity()
                self.cKashi = gc.getMap().plot(72,59).getPlotCity()
                self.cNovosibirsk = gc.getMap().plot(72,70).getPlotCity()
                self.cNagpur = gc.getMap().plot(73,40).getPlotCity()
                self.cKathmandu = gc.getMap().plot(75,51).getPlotCity()
                self.cUrumqi = gc.getMap().plot(77,63).getPlotCity()
                self.cKrasnoyarsk = gc.getMap().plot(77,72).getPlotCity()
                self.cCalcutta = gc.getMap().plot(78,43).getPlotCity()
                self.cLhasa = gc.getMap().plot(80,50).getPlotCity()
                self.cRangoon = gc.getMap().plot(83,37).getPlotCity()
                self.cMandalay = gc.getMap().plot(83,42).getPlotCity()
                self.cMyitkyina = gc.getMap().plot(83,46).getPlotCity()
                self.cYumen = gc.getMap().plot(83,59).getPlotCity()
                self.cUliastay = gc.getMap().plot(83,66).getPlotCity()
                self.cTura = gc.getMap().plot(85,76).getPlotCity()
                self.cPadang = gc.getMap().plot(86,27).getPlotCity()
                self.cChiangMai = gc.getMap().plot(86,41).getPlotCity()
                self.cIrkutsk = gc.getMap().plot(86,70).getPlotCity()
                self.cPhuket = gc.getMap().plot(87,32).getPlotCity()
                self.cBangkok = gc.getMap().plot(87,36).getPlotCity()
                self.cChengdu = gc.getMap().plot(87,49).getPlotCity()
                self.cUdonThani = gc.getMap().plot(89,38).getPlotCity()
                self.cHanoi = gc.getMap().plot(89,43).getPlotCity()
                self.cLanzhou = gc.getMap().plot(90,57).getPlotCity()
                self.cUlanBator = gc.getMap().plot(90,65).getPlotCity()
                self.cSingapore = gc.getMap().plot(91,28).getPlotCity()
                self.cJakarta = gc.getMap().plot(92,23).getPlotCity()
                self.cSaigon = gc.getMap().plot(92,33).getPlotCity()
                self.cNanning = gc.getMap().plot(92,43).getPlotCity()
                self.cDaNang = gc.getMap().plot(93,37).getPlotCity()
                self.cBaotou = gc.getMap().plot(93,61).getPlotCity()
                self.cPontianak = gc.getMap().plot(94,26).getPlotCity()
                self.cXian = gc.getMap().plot(94,52).getPlotCity()
                self.cChita = gc.getMap().plot(94,71).getPlotCity()
                self.cBaruunUrt = gc.getMap().plot(95,65).getPlotCity()
                self.cHongKong = gc.getMap().plot(96,41).getPlotCity()
                self.cNanjing = gc.getMap().plot(96,59).getPlotCity()
                self.cLensk = gc.getMap().plot(96,74).getPlotCity()
                self.cBrunei = gc.getMap().plot(97,29).getPlotCity()
                self.cPerth = gc.getMap().plot(99,9).getPlotCity()
                self.cSamarinda = gc.getMap().plot(99,27).getPlotCity()
                self.cShantou = gc.getMap().plot(99,44).getPlotCity()
                self.cQingdao = gc.getMap().plot(99,56).getPlotCity()
                self.cBali = gc.getMap().plot(100,22).getPlotCity()
                self.cTynda = gc.getMap().plot(100,72).getPlotCity()
                self.cShanghai = gc.getMap().plot(101,49).getPlotCity()
                self.cAnshan = gc.getMap().plot(101,61).getPlotCity()
                self.cBroome = gc.getMap().plot(102,18).getPlotCity()
                self.cManila = gc.getMap().plot(102,36).getPlotCity()
                self.cIligan = gc.getMap().plot(103,32).getPlotCity()
                self.cTaipei = gc.getMap().plot(103,46).getPlotCity()
                self.cEsperance = gc.getMap().plot(104,8).getPlotCity()
                self.cPyongyang = gc.getMap().plot(104,59).getPlotCity()
                self.cHarbin = gc.getMap().plot(104,68).getPlotCity()
                self.cNagasaki = gc.getMap().plot(105,51).getPlotCity()
                self.cYosu = gc.getMap().plot(105,55).getPlotCity()
                self.cJilin = gc.getMap().plot(105,65).getPlotCity()
                self.cYakutsk = gc.getMap().plot(105,74).getPlotCity()
                self.cAmbon = gc.getMap().plot(106,27).getPlotCity()
                self.cDarwin = gc.getMap().plot(107,22).getPlotCity()
                self.cOkinawa = gc.getMap().plot(107,48).getPlotCity()
                self.cKimchaek = gc.getMap().plot(107,61).getPlotCity()
                self.cHiroshima = gc.getMap().plot(108,53).getPlotCity()
                self.cKhabarovsk = gc.getMap().plot(108,70).getPlotCity()
                self.cNagoya = gc.getMap().plot(110,54).getPlotCity()
                self.cVladivostok = gc.getMap().plot(110,64).getPlotCity()
                self.cPortAugusta = gc.getMap().plot(112,10).getPlotCity()
                self.cJayapura = gc.getMap().plot(112,29).getPlotCity()
                self.cBonin = gc.getMap().plot(113,51).getPlotCity()
                self.cAkita = gc.getMap().plot(113,60).getPlotCity()
                self.cSapporo = gc.getMap().plot(113,63).getPlotCity()
                self.cSakhalin = gc.getMap().plot(113,70).getPlotCity()
                self.cMagadah = gc.getMap().plot(113,74).getPlotCity()
                self.cAdelaide = gc.getMap().plot(114,7).getPlotCity()
                self.cTokyo = gc.getMap().plot(114,54).getPlotCity()
                self.cSendai = gc.getMap().plot(114,57).getPlotCity()
                self.cYuzhnoSakhalinsk = gc.getMap().plot(114,66).getPlotCity()
                self.cCairns = gc.getMap().plot(116,19).getPlotCity()
                self.cPortMoresby = gc.getMap().plot(116,25).getPlotCity()
                self.cLae = gc.getMap().plot(116,28).getPlotCity()
                self.cHagatna = gc.getMap().plot(116,37).getPlotCity()
                self.cMelbourne = gc.getMap().plot(117,7).getPlotCity()
                self.cJapCity1 = gc.getMap().plot(117,41).getPlotCity()
                self.cHobart = gc.getMap().plot(118,3).getPlotCity()
                self.cPetropavlovsk = gc.getMap().plot(118,69).getPlotCity()
                self.cEvensk = gc.getMap().plot(118,75).getPlotCity()
                self.cSydney = gc.getMap().plot(121,10).getPlotCity()
                self.cBrisbane = gc.getMap().plot(121,14).getPlotCity()
                self.cKieta = gc.getMap().plot(121,28).getPlotCity()
                self.cWakeIsland = gc.getMap().plot(122,46).getPlotCity()
                self.cHoniara = gc.getMap().plot(123,26).getPlotCity()
                self.cBikini = gc.getMap().plot(123,35).getPlotCity()
                self.cNoumea = gc.getMap().plot(126,16).getPlotCity()
                self.cYaren = gc.getMap().plot(126,32).getPlotCity()
                self.cPortVila = gc.getMap().plot(127,21).getPlotCity()
                self.cMidwayIsland = gc.getMap().plot(128,50).getPlotCity()
                self.cChristchurch = gc.getMap().plot(129,4).getPlotCity()
                self.cMajuro = gc.getMap().plot(129,34).getPlotCity()
                self.cAuckland = gc.getMap().plot(130,11).getPlotCity()
                self.cWellington = gc.getMap().plot(131,7).getPlotCity()
                self.cSuva = gc.getMap().plot(132,22).getPlotCity()
                self.cFongafale = gc.getMap().plot(133,27).getPlotCity()
                self.cHonolulu = gc.getMap().plot(134,48).getPlotCity()
                self.cAnchorage = gc.getMap().plot(134,75).getPlotCity()
                self.cNukuAlofa = gc.getMap().plot(135,19).getPlotCity()
                self.cPagoPago = gc.getMap().plot(136,24).getPlotCity()
                self.cAlofi = gc.getMap().plot(137,20).getPlotCity()
                self.cPapeete = gc.getMap().plot(140,19).getPlotCity()
                self.cWhitehorse = gc.getMap().plot(140,73).getPlotCity()
                self.cBairiki = gc.getMap().plot(141,33).getPlotCity()
                self.cAdamstown = gc.getMap().plot(144,18).getPlotCity()
                self.cSeattle = gc.getMap().plot(145,66).getPlotCity()
                self.cSanFrancisco = gc.getMap().plot(146,60).getPlotCity()
                self.cVancouver = gc.getMap().plot(146,68).getPlotCity()
                self.cLosAngeles = gc.getMap().plot(147,57).getPlotCity()
                self.cLaPaz = gc.getMap().plot(149,49).getPlotCity()
                self.cYellowknife = gc.getMap().plot(149,76).getPlotCity()
                self.cTaiohae = gc.getMap().plot(150,24).getPlotCity()
                self.cGuaymas = gc.getMap().plot(151,52).getPlotCity()
                self.cEdmonton = gc.getMap().plot(151,71).getPlotCity()
                self.cPuertoVallarta = gc.getMap().plot(153,46).getPlotCity()
                self.cHelena = gc.getMap().plot(153,65).getPlotCity()
                self.cHangaRoa = gc.getMap().plot(154,13).getPlotCity()
                self.cSanteFe = gc.getMap().plot(156,58).getPlotCity()
                self.cRegina = gc.getMap().plot(156,68).getPlotCity()
                self.cMexicoCity = gc.getMap().plot(157,45).getPlotCity()
                self.cTampico = gc.getMap().plot(159,48).getPlotCity()
                self.cFargo = gc.getMap().plot(159,65).getPlotCity()
                self.cSantaCruz = gc.getMap().plot(160,41).getPlotCity()
                self.cWinnipeg = gc.getMap().plot(160,68).getPlotCity()
                self.cHouston = gc.getMap().plot(162,52).getPlotCity()
                self.cLincoln = gc.getMap().plot(162,61).getPlotCity()
                self.cPuertoBaquerizoMoreno = gc.getMap().plot(163,31).getPlotCity()
                self.cSanSalvador = gc.getMap().plot(164,40).getPlotCity()
                self.cMinneapolis = gc.getMap().plot(164,65).getPlotCity()
                self.cMerida = gc.getMap().plot(165,46).getPlotCity()
                self.cMemphis = gc.getMap().plot(166,58).getPlotCity()
                self.cNewOrleans = gc.getMap().plot(167,53).getPlotCity()
                self.cPuertoCabezas = gc.getMap().plot(168,40).getPlotCity()
                self.cHavana = gc.getMap().plot(170,47).getPlotCity()
                self.cSaultSteMarie = gc.getMap().plot(170,67).getPlotCity()
                self.cPanamaCity = gc.getMap().plot(171,37).getPlotCity()
                self.cDetroit = gc.getMap().plot(171,62).getPlotCity()
                self.cLima = gc.getMap().plot(172,23).getPlotCity()
                self.cQuito = gc.getMap().plot(172,31).getPlotCity()
                self.cMiami = gc.getMap().plot(172,50).getPlotCity()
                self.cChisasibi = gc.getMap().plot(172,71).getPlotCity()
                self.cSantiago = gc.getMap().plot(173,44).getPlotCity()
                self.cBagota = gc.getMap().plot(174,35).getPlotCity()
                self.cCharleston = gc.getMap().plot(174,55).getPlotCity()
                self.cCoihaique = gc.getMap().plot(175,9).getPlotCity()
                self.cPuntaArenas = gc.getMap().plot(176,3).getPlotCity()
                self.cSantiag = gc.getMap().plot(176,14).getPlotCity()
                self.cIcana = gc.getMap().plot(176,33).getPlotCity()
                self.cWashingtonDC = gc.getMap().plot(176,60).getPlotCity()
                self.cOttawa = gc.getMap().plot(176,65).getPlotCity()
                self.cLaPazz = gc.getMap().plot(177,20).getPlotCity()
                self.cPortoVelho = gc.getMap().plot(178,27).getPlotCity()
                self.cCaracas = gc.getMap().plot(178,37).getPlotCity()
                self.cSantoDomingo = gc.getMap().plot(178,42).getPlotCity()
                self.cQuebec = gc.getMap().plot(179,66).getPlotCity()
                self.cManaus = gc.getMap().plot(180,30).getPlotCity()
                self.cIqaluit = gc.getMap().plot(180,77).getPlotCity()
                self.cNewYorkCity = gc.getMap().plot(181,63).getPlotCity()
                self.cStanley = gc.getMap().plot(182,4).getPlotCity()
                self.cBuenosAires = gc.getMap().plot(183,13).getPlotCity()
                self.cCuiaba = gc.getMap().plot(183,23).getPlotCity()
                self.cParamaribo = gc.getMap().plot(183,35).getPlotCity()
                self.cBarbados = gc.getMap().plot(184,40).getPlotCity()
                self.cMacapa = gc.getMap().plot(186,32).getPlotCity()
                self.cHalifax = gc.getMap().plot(186,65).getPlotCity()
                self.cFlorianopolis = gc.getMap().plot(187,16).getPlotCity()
                self.cBrasilia = gc.getMap().plot(188,23).getPlotCity()
                self.cSaoLuis = gc.getMap().plot(191,30).getPlotCity()
                self.cStJohns = gc.getMap().plot(191,67).getPlotCity()
                self.cRioDeJaneiro = gc.getMap().plot(192,20).getPlotCity()
                self.cRecife = gc.getMap().plot(195,27).getPlotCity()
                return

	def globalSetup(self):
                return

        def doEvent(self, numEvent):
                popup = PyPopup.PyPopup(-1)
                if (numEvent == 1):
                    # Cutscene movie
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                    popupInfo.setData1(0)
                    popupInfo.setData2(0)
                    popupInfo.setData3(4)
           	    popupInfo.setText(u"showWonderMovie")
           	    for i in range(gc.getMAX_CIV_PLAYERS()):
                        if (gc.getPlayer(i).isAlive()):
                            if(gc.getPlayer(i).isHuman()):
                                popupInfo.addPopup(i)
                    # Germany DOW Poland
                    szTitle = localText.getText("TXT_KEY_WW2_ESEP1_1939_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_ESEP1_1939_TEXT", ())
                    self.pGermanyTeam.declareWar(self.pPolandID, false, WarPlanTypes.WARPLAN_TOTAL)
                    self.pEnglandTeam.declareWar(self.pGermanyID, false, WarPlanTypes.WARPLAN_TOTAL)
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pFranceID).getTeam())
                    self.pFranceTeam = gc.getTeam(gc.getPlayer(self.pFranceID).getTeam())
                elif (numEvent == 2):
                    # USSR DOW Poland
                    szTitle = localText.getText("TXT_KEY_WW2_ESEP2_1939_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_ESEP2_1939_TEXT", ())
                    self.pUSSRTeam.declareWar(self.pPolandID, false, WarPlanTypes.WARPLAN_TOTAL)
                elif (numEvent == 3):
                    # USSR DOW Finland
                    szTitle = localText.getText("TXT_KEY_WW2_ENOV2_1939_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_ENOV2_1939_TEXT", ())
                    self.pUSSRTeam.declareWar(self.pFinlandID, false, WarPlanTypes.WARPLAN_TOTAL)
                elif (numEvent == 4):
                    # USSR Peace Finland
                    szTitle = localText.getText("TXT_KEY_WW2_EMAR1_1940_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EMAR1_1940_TEXT", ())
                    self.pUSSRTeam.makePeace(gc.getPlayer(self.pFinlandID).getTeam())
                elif (numEvent == 5):
                    # Germany DOW Scandinavia
                    szTitle = localText.getText("TXT_KEY_WW2_EAPR1_1940_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EAPR1_1940_TEXT", ())
                    self.pGermanyTeam.declareWar(self.pNorwayID, false, WarPlanTypes.WARPLAN_TOTAL)
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pNorwayID).getTeam())
                    self.pNorwayTeam = gc.getTeam(gc.getPlayer(self.pNorwayID).getTeam())
                elif (numEvent == 6):
                    # Germany DOW Lowlands
                    szTitle = localText.getText("TXT_KEY_WW2_EMAY1_1940_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EMAY1_1940_TEXT", ())
                    self.pGermanyTeam.declareWar(self.pLowCountriesID, false, WarPlanTypes.WARPLAN_TOTAL)
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pLowCountriesID).getTeam())
                    self.pLowCountriesTeam = gc.getTeam(gc.getPlayer(self.pLowCountriesID).getTeam())
                elif (numEvent == 7):
                    # Italy DOW Allies; Italy Ally Germany
                    szTitle = localText.getText("TXT_KEY_WW2_EJUN1_1940_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EJUN1_1940_TEXT", ())
                    self.pItalyTeam.declareWar(self.pEnglandID, false, WarPlanTypes.WARPLAN_TOTAL)
                    self.pGermanyTeam.addTeam(gc.getPlayer(self.pItalyID).getTeam())
                    self.pItalyTeam = gc.getTeam(gc.getPlayer(self.pItalyID).getTeam())
                elif (numEvent == 8):
                    # USSR DOW Baltic
                    szTitle = localText.getText("TXT_KEY_WW2_EJUL2_1940_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EJUL2_1940_TEXT", ())
                    self.pUSSRTeam.declareWar(self.pBalticStatesID, false, WarPlanTypes.WARPLAN_TOTAL)
                elif (numEvent == 9):
                    # East Balkan Ally Axis
                    szTitle = localText.getText("TXT_KEY_WW2_EOCT1_1940_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EOCT1_1940_TEXT", ())
                    self.pGermanyTeam.addTeam(gc.getPlayer(self.pEastBalkanID).getTeam())
                    self.pEastBalkanTeam = gc.getTeam(gc.getPlayer(self.pEastBalkanID).getTeam())
                elif (numEvent == 10):
                    # Axis DOW West Balkan
                    szTitle = localText.getText("TXT_KEY_WW2_EOCT2_1940_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EOCT2_1940_TEXT", ())
                    self.pGermanyTeam.declareWar(self.pWestBalkanID, false, WarPlanTypes.WARPLAN_TOTAL)
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pWestBalkanID).getTeam())
                    self.pWestBalkanTeam = gc.getTeam(gc.getPlayer(self.pWestBalkanID).getTeam())
                elif (numEvent == 11):
                    # Cutscene movie
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                    popupInfo.setData1(0)
                    popupInfo.setData2(0)
                    popupInfo.setData3(6)
                    popupInfo.setText(u"showWonderMovie")
                    for i in range(gc.getMAX_CIV_PLAYERS()):
                        if (gc.getPlayer(i).isAlive()):
                            if(gc.getPlayer(i).isHuman()):
                                popupInfo.addPopup(i)
                    # Axis DOW USSR
                    szTitle = localText.getText("TXT_KEY_WW2_EJUN2_1941_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EJUN2_1941_TEXT", ())
                    game.setBordersOpen(self.pGermanyID, self.pFinlandID)
                    self.pGermanyTeam.declareWar(self.pUSSRID, false, WarPlanTypes.WARPLAN_TOTAL)
                    self.pFinlandTeam.declareWar(self.pUSSRID, false, WarPlanTypes.WARPLAN_TOTAL)
                elif (numEvent == 12):
                    # Spanish Civil War
                    szTitle = localText.getText("TXT_KEY_WW2_EJUL2_1936_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EJUL2_1936_TEXT", ())
                    self.pFacistIberiaTeam.declareWar(self.pRepubIberiaID, false, WarPlanTypes.WARPLAN_TOTAL)
                elif (numEvent == 13):
                    # Axis DOW USA
                    szTitle = localText.getText("TXT_KEY_WW2_EDEC1_1941_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EDEC1_1941_TEXT", ())
                    self.pGermanyTeam.declareWar(self.pUSAID, false, WarPlanTypes.WARPLAN_TOTAL)
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pUSAID).getTeam())
                    self.pUSATeam = gc.getTeam(gc.getPlayer(self.pUSAID).getTeam())
                elif (numEvent == 14):
                    # Cutscene movie
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                    popupInfo.setData1(0)
                    popupInfo.setData2(0)
                    popupInfo.setData3(7)
                    popupInfo.setText(u"showWonderMovie")
                    for i in range(gc.getMAX_CIV_PLAYERS()):
                        if (gc.getPlayer(i).isAlive()):
                            if(gc.getPlayer(i).isHuman()):
                                popupInfo.addPopup(i)
                    # Japan DOW China
                    szTitle = localText.getText("TXT_KEY_WW2_AJUL1_1937_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_AJUL1_1937_TEXT", ())
                    self.pJapanTeam.declareWar(self.pChinaID, false, WarPlanTypes.WARPLAN_TOTAL)
                elif (numEvent == 15):
                    # Siam joins Japan versus France
                    szTitle = localText.getText("TXT_KEY_WW2_ASEP2_1940_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_ASEP2_1940_TEXT", ())
                    self.pJapanTeam.addTeam(gc.getPlayer(self.pSiamID).getTeam())
                    self.pSiamTeam = gc.getTeam(gc.getPlayer(self.pSiamID).getTeam())
                    self.pJapanTeam.declareWar(self.pFranceID, false, WarPlanTypes.WARPLAN_TOTAL)
                elif (numEvent == 16):
                    # Cutscene movie
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                    popupInfo.setData1(0)
                    popupInfo.setData2(0)
                    popupInfo.setData3(5)
                    popupInfo.setText(u"showWonderMovie")
                    for i in range(gc.getMAX_CIV_PLAYERS()):
                        if (gc.getPlayer(i).isAlive()):
                            if(gc.getPlayer(i).isHuman()):
                                popupInfo.addPopup(i)
                    # Japan DOW USA, England, Siam, Australia, Dutch, Philippines
                    szTitle = localText.getText("TXT_KEY_WW2_ADEC1_1941_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_ADEC1_1941_TEXT", ())
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pAustraliaID).getTeam())
                    self.pAustraliaTeam = gc.getTeam(gc.getPlayer(self.pAustraliaID).getTeam())
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pChinaID).getTeam())
                    self.pChinaTeam = gc.getTeam(gc.getPlayer(self.pChinaID).getTeam())
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pUSAID).getTeam())
                    self.pUSATeam = gc.getTeam(gc.getPlayer(self.pUSAID).getTeam())
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pFranceID).getTeam())
                    self.pFranceTeam = gc.getTeam(gc.getPlayer(self.pFranceID).getTeam())
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pPhilippinesID).getTeam())
                    self.pPhilippinesTeam = gc.getTeam(gc.getPlayer(self.pPhilippinesID).getTeam())
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pLowCountriesID).getTeam())
                    self.pLowCountriesTeam = gc.getTeam(gc.getPlayer(self.pLowCountriesID).getTeam())
                elif (numEvent == 17):
                    # USSR DOW Japan
                    szTitle = localText.getText("TXT_KEY_WW2_AAUG1_1945_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_AAUG1_1945_TEXT", ())
                    self.pUSSRTeam.addTeam(gc.getPlayer(self.pMongoliaID).getTeam())
                    self.pMongoliaTeam = gc.getTeam(gc.getPlayer(self.pMongoliaID).getTeam())
                    self.pEnglandTeam.addTeam(gc.getPlayer(self.pUSSRID).getTeam())
                    self.pUSSRTeam = gc.getTeam(gc.getPlayer(self.pUSSRID).getTeam())
                elif (numEvent == 18):
                    # Germany DOW Austria
                    szTitle = localText.getText("TXT_KEY_WW2_EMAR1_1938_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_EMAR1_1938_TEXT", ())
                    self.pGermanyTeam.declareWar(self.pAustriaID, false, WarPlanTypes.WARPLAN_TOTAL)
                elif (numEvent == 19):
                    # Germany DOW Czech
                    szTitle = localText.getText("TXT_KEY_WW2_ESEP2_1938_TITLE", ())
                    szText = localText.getText("TXT_KEY_WW2_ESEP2_1938_TEXT", ())
                    self.pGermanyTeam.declareWar(self.pCzechID, false, WarPlanTypes.WARPLAN_TOTAL)
#                elif (numEvent == 20):
                # Do popup
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                return

# RtW Setup City
###################################################
        def setupCity(self, player, city):
                gc.getPlayer(player).acquireCity(city, False, True)
                for i in range(0, 35):
                    city.setCulture(i, 0, True)
                city.setCulture(player, 500, True)
                if (player == self.pGermanyID or player == self.pItalyID or player == self.pJapanID or player == self.pFacistIberiaID):
                    city.setHasReligion(0, True, False, False)
                elif (player == self.pUSSRID or player == self.pMongoliaID):
                    city.setHasReligion(1, True, False, False)
                else:
                    city.setHasReligion(2, True, False, False)
                return
