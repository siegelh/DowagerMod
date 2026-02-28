from __future__ import annotations

from pathlib import Path
from xml.dom import minidom, Node
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml"
BCP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingClassInfos.xml"
BAP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Building.xml"
BONP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Assets/XML/Terrain/CIV4BonusInfos.xml"
BONP_BTS = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Terrain/CIV4BonusInfos.xml"
BOAP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Bonus.xml"
BOAP_BTS = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Bonus.xml"
CP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/GameInfo/CIV4CorporationInfo.xml"
NCP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/BasicInfos/CIV4NewConceptInfos.xml"
ITP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Text/CIV4GameText_IndustryBuildings.xml"
STP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Text/ZZZ_CIV4GameText_IndustrySupplyChains.xml"
BBTN = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Interface/Buttons/Buildings/Industries"
SBTN = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Assets/Art/Interface/Buttons/Bonuses/Synthetic"
SBTN_BTS = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Interface/Buttons/Bonuses/Synthetic"
WAR_BONP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Warlords/Assets/XML/Terrain/CIV4BonusInfos.xml"
GOLD, RESEARCH, CULTURE, ESPIONAGE = 0, 1, 2, 3
FOOD, HAMMER, COMMERCE = 0, 1, 2

def strip_ws(n):
    dead=[]
    for c in n.childNodes:
        if c.nodeType==Node.TEXT_NODE and not c.data.strip(): dead.append(c)
        elif c.hasChildNodes(): strip_ws(c)
    for c in dead: n.removeChild(c)

def parse(path):
    d=minidom.parse(str(path)); strip_ws(d); return d

def write(doc,path):
    x=doc.toprettyxml(indent='\t',newl='\n',encoding='utf-8')
    path.write_bytes(b'\n'.join(l for l in x.splitlines() if l.strip())+b'\n')

def els(n,tag=None): return [c for c in n.childNodes if c.nodeType==Node.ELEMENT_NODE and (tag is None or c.tagName==tag)]
def child(n,tag):
    e=els(n,tag); return e[0] if e else None

def txt(n): return ''.join(c.data for c in n.childNodes if c.nodeType in (Node.TEXT_NODE,Node.CDATA_SECTION_NODE))
def settxt(n,v):
    while n.firstChild: n.removeChild(n.firstChild)
    n.appendChild(n.ownerDocument.createTextNode(str(v)))
def mk(doc,tag,val=None):
    e=doc.createElement(tag)
    if val is not None: e.appendChild(doc.createTextNode(str(val)))
    return e

def setc(n,tag,val,before=None):
    c=child(n,tag)
    if c is None:
        c=n.ownerDocument.createElement(tag)
        r=child(n,before) if before else None
        n.insertBefore(c,r) if r is not None else n.appendChild(c)
    settxt(c,val); return c

def rep(parent,new,before=None):
    old=child(parent,new.tagName)
    if old is not None: parent.replaceChild(new,old); return
    r=child(parent,before) if before else None
    parent.insertBefore(new,r) if r is not None else parent.appendChild(new)

def setlist(n,tag,item,vals,before=None):
    c=n.ownerDocument.createElement(tag)
    for v in vals: c.appendChild(mk(n.ownerDocument,item,v))
    rep(n,c,before)

def empty(n,tag,before=None): rep(n,n.ownerDocument.createElement(tag),before)
def by_type(doc,tag,t):
    for e in doc.getElementsByTagName(tag):
        c=child(e,'Type')
        if c is not None and txt(c)==t: return e
    return None

def ensure(doc,container,tag,t,tmpl=None):
    e=by_type(doc,tag,t)
    if e is not None: return e
    c=doc.getElementsByTagName(container)[0]
    e=tmpl.cloneNode(True)
    setc(e,'Type',t)
    c.appendChild(e)
    return e

def neededs(n,classes):
    c=n.ownerDocument.createElement('BuildingClassNeededs')
    for bc in classes:
        e=n.ownerDocument.createElement('BuildingClassNeeded')
        e.appendChild(mk(n.ownerDocument,'BuildingClassType',bc)); e.appendChild(mk(n.ownerDocument,'bNeededInCity',1)); c.appendChild(e)
    rep(n,c,'SpecialistYieldChanges')

def local_bonus_prereqs(n,prs):
    c=n.ownerDocument.createElement('LocalBonusPrereqs')
    for p in prs:
        e=n.ownerDocument.createElement('LocalBonusPrereq'); bt=n.ownerDocument.createElement('BonusTypes')
        for b in p['bonuses']: bt.appendChild(mk(n.ownerDocument,'BonusType',b))
        e.appendChild(bt); e.appendChild(mk(n.ownerDocument,'iMinCount',p.get('min',1))); e.appendChild(mk(n.ownerDocument,'bImprovedOnly',int(p.get('improved',1)))); e.appendChild(mk(n.ownerDocument,'bConnectedOnly',int(p.get('connected',1)))); e.appendChild(mk(n.ownerDocument,'bCityRadiusOnly',int(p.get('city',1)))); c.appendChild(e)
    rep(n,c,'ConnectedBonusPrereqs')

def connected_bonus_prereqs(n,prs):
    c=n.ownerDocument.createElement('ConnectedBonusPrereqs')
    for p in prs:
        e=n.ownerDocument.createElement('ConnectedBonusPrereq'); bt=n.ownerDocument.createElement('BonusTypes')
        for b in p['bonuses']: bt.appendChild(mk(n.ownerDocument,'BonusType',b))
        e.appendChild(bt); e.appendChild(mk(n.ownerDocument,'iMinCount',p.get('min',1))); c.appendChild(e)
    rep(n,c,'Flavors')

def specialists(n,m):
    c=n.ownerDocument.createElement('SpecialistCounts')
    for s,v in m.items():
        e=n.ownerDocument.createElement('SpecialistCount'); e.appendChild(mk(n.ownerDocument,'SpecialistType',s)); e.appendChild(mk(n.ownerDocument,'iSpecialistCount',v)); c.appendChild(e)
    rep(n,c,'FreeSpecialistCounts')

def flavors(n,m):
    c=n.ownerDocument.createElement('Flavors')
    for f,v in m.items():
        e=n.ownerDocument.createElement('Flavor'); e.appendChild(mk(n.ownerDocument,'FlavorType',f)); e.appendChild(mk(n.ownerDocument,'iFlavor',v)); c.appendChild(e)
    rep(n,c,'HotKey')

def bonus_name(b): return b.replace('BONUS_','').replace('_',' ').title()
PALETTES={
'dyes':((63,31,102),(125,76,182),(113,65,181),(191,106,232),(41,18,64),(236,212,255)),'furs':((73,46,24),(135,95,52),(164,120,71),(224,191,142),(53,31,13),(247,227,194)),'gems':((11,56,83),(26,121,138),(54,176,184),(142,245,233),(7,33,49),(220,255,255)),'bullion':((106,68,4),(182,124,18),(224,174,42),(255,224,120),(82,47,4),(255,246,190)),'incense':((88,56,23),(171,120,56),(210,166,88),(255,222,165),(48,27,8),(255,239,208)),'ivory':((171,157,124),(219,205,168),(235,224,196),(255,247,228),(104,86,58),(255,250,236)),'silk':((87,14,38),(158,35,71),(205,66,109),(255,155,192),(53,7,22),(255,220,233)),'silver':((68,80,96),(123,146,168),(183,197,212),(240,246,250),(39,46,57),(255,255,255)),'spices':((97,45,12),(171,80,20),(221,111,30),(255,183,84),(58,23,5),(255,230,184)),'confections':((104,35,58),(171,87,116),(230,153,184),(255,227,238),(63,18,34),(255,245,248)),'wine':((69,10,27),(128,21,49),(180,45,79),(244,146,173),(38,5,14),(255,218,228)),'oil':((54,53,66),(112,98,55),(202,162,61),(255,227,133),(21,20,27),(255,240,175)),'plays':((46,28,77),(96,63,145),(178,121,221),(245,210,255),(24,11,41),(255,238,255)),'recordings':((34,28,33),(94,42,49),(164,72,84),(255,193,205),(9,9,10),(255,233,236)),'film':((36,35,32),(93,84,69),(164,149,118),(248,236,196),(17,16,14),(255,247,225)),'flour':((130,104,49),(206,174,99),(237,223,180),(255,247,228),(78,57,19),(255,252,240)),'meats':((78,18,20),(137,37,41),(201,78,67),(255,181,163),(45,7,9),(255,219,210)),'seafood':((16,62,86),(25,112,136),(62,175,190),(184,245,255),(8,34,47),(227,255,255)),'preserves':((83,33,74),(146,66,123),(208,118,170),(255,216,239),(43,13,38),(255,242,250)),'millers':((102,75,31),(176,137,67),(224,190,101),(255,235,163),(54,35,10),(255,249,210)),'smokehouse':((72,32,18),(126,62,31),(182,92,54),(255,197,155),(33,12,4),(255,224,200)),'cannery':((49,75,88),(96,141,155),(171,199,206),(238,248,250),(26,38,47),(255,255,255)),'fruit_market':((89,46,16),(164,87,30),(232,149,78),(255,220,175),(45,20,5),(255,240,214)),'bakers':((110,80,35),(173,127,55),(225,179,92),(255,236,170),(60,38,10),(255,247,214)),'festival_kitchen':((92,38,54),(150,74,94),(224,149,136),(255,226,207),(48,16,25),(255,247,236)),'royal_kitchen':((79,56,18),(142,104,36),(221,183,70),(255,241,191),(44,27,6),(255,250,221)),'carvery':((90,27,20),(155,66,32),(219,121,62),(255,215,164),(48,12,7),(255,238,217)),'maritime_supper':((20,54,75),(58,108,138),(123,176,203),(231,245,255),(8,22,34),(255,255,255))}
SYN=[('BONUS_FINE_DYES','Fine Dyes','ART_DEF_BONUS_FINE_DYES','ART_DEF_BONUS_DYE','fine_dyes.dds','dyes'),('BONUS_FINE_FURS','Fine Furs','ART_DEF_BONUS_FINE_FURS','ART_DEF_BONUS_FUR','fine_furs.dds','furs'),('BONUS_CUT_GEMS','Cut Gems','ART_DEF_BONUS_CUT_GEMS','ART_DEF_BONUS_GEMS','cut_gems.dds','gems'),('BONUS_GOLD_BULLION','Gold Bullion','ART_DEF_BONUS_GOLD_BULLION','ART_DEF_BONUS_GOLD','gold_bullion.dds','bullion'),('BONUS_TEMPLE_INCENSE','Temple Incense','ART_DEF_BONUS_TEMPLE_INCENSE','ART_DEF_BONUS_INCENSE','temple_incense.dds','incense'),('BONUS_IVORY_CARVINGS','Ivory Carvings','ART_DEF_BONUS_IVORY_CARVINGS','ART_DEF_BONUS_IVORY','ivory_carvings.dds','ivory'),('BONUS_FINE_SILK','Fine Silk','ART_DEF_BONUS_FINE_SILK','ART_DEF_BONUS_SILK','fine_silk.dds','silk'),('BONUS_WORKED_SILVER','Worked Silver','ART_DEF_BONUS_WORKED_SILVER','ART_DEF_BONUS_SILVER','worked_silver.dds','silver'),('BONUS_SPICE_BLENDS','Spice Blends','ART_DEF_BONUS_SPICE_BLENDS','ART_DEF_BONUS_SPICES','spice_blends.dds','spices'),('BONUS_CONFECTIONS','Confections','ART_DEF_BONUS_CONFECTIONS','ART_DEF_BONUS_SUGAR','confections.dds','confections'),('BONUS_VINTAGE_WINE','Vintage Wine','ART_DEF_BONUS_VINTAGE_WINE','ART_DEF_BONUS_WINE','vintage_wine.dds','wine'),('BONUS_LAMP_OIL','Lamp Oil','ART_DEF_BONUS_LAMP_OIL','ART_DEF_BONUS_WHALE','lamp_oil.dds','oil'),('BONUS_STAGE_PLAYS','Stage Plays','ART_DEF_BONUS_STAGE_PLAYS','ART_DEF_BONUS_DRAMA','stage_plays.dds','plays'),('BONUS_MASTER_RECORDINGS','Master Recordings','ART_DEF_BONUS_MASTER_RECORDINGS','ART_DEF_BONUS_MUSIC','master_recordings.dds','recordings'),('BONUS_FILM_PRINTS','Film Prints','ART_DEF_BONUS_FILM_PRINTS','ART_DEF_BONUS_MOVIES','film_prints.dds','film'),('BONUS_FLOUR','Flour','ART_DEF_BONUS_FLOUR','ART_DEF_BONUS_WHEAT','flour.dds','flour'),('BONUS_CURED_MEATS','Cured Meats','ART_DEF_BONUS_CURED_MEATS','ART_DEF_BONUS_COW','cured_meats.dds','meats'),('BONUS_PRESERVED_SEAFOOD','Preserved Seafood','ART_DEF_BONUS_PRESERVED_SEAFOOD','ART_DEF_BONUS_FISH','preserved_seafood.dds','seafood'),('BONUS_FRUIT_PRESERVES','Fruit Preserves','ART_DEF_BONUS_FRUIT_PRESERVES','ART_DEF_BONUS_BANANA','fruit_preserves.dds','preserves')]
EXIST_PROC={'BUILDING_INDUSTRY_DYE_WORKS':'BONUS_FINE_DYES','BUILDING_INDUSTRY_FURRIERS_HALL':'BONUS_FINE_FURS','BUILDING_INDUSTRY_JEWELERS_QUARTER':'BONUS_CUT_GEMS','BUILDING_INDUSTRY_MINTING_HOUSE':'BONUS_GOLD_BULLION','BUILDING_INDUSTRY_PERFUMERS_SANCTUARY':'BONUS_TEMPLE_INCENSE','BUILDING_INDUSTRY_IVORY_CARVERS_ATELIER':'BONUS_IVORY_CARVINGS','BUILDING_INDUSTRY_SILK_WEAVERS_WORKSHOP':'BONUS_FINE_SILK','BUILDING_INDUSTRY_SILVERSMITHS_HALL':'BONUS_WORKED_SILVER','BUILDING_INDUSTRY_SPICE_EXCHANGE':'BONUS_SPICE_BLENDS','BUILDING_INDUSTRY_CONFECTIONERS_GUILD':'BONUS_CONFECTIONS','BUILDING_INDUSTRY_VINTNERS_GUILD':'BONUS_VINTAGE_WINE','BUILDING_INDUSTRY_WHALE_OIL_CHANDLERY':'BONUS_LAMP_OIL','BUILDING_INDUSTRY_PLAYWRIGHTS_GUILD':'BONUS_STAGE_PLAYS','BUILDING_INDUSTRY_RECORDING_HOUSE':'BONUS_MASTER_RECORDINGS','BUILDING_INDUSTRY_FILM_STUDIO_DISTRICT':'BONUS_FILM_PRINTS'}
EXIST_COMP={'BUILDING_INDUSTRY_ROYAL_GARMENTS_HOUSE':['BONUS_FINE_SILK','BONUS_FINE_DYES'],'BUILDING_INDUSTRY_NOBLE_TAILORS_HALL':['BONUS_FINE_SILK','BONUS_FINE_FURS'],'BUILDING_INDUSTRY_COURT_REGALIA_ATELIER':['BONUS_FINE_SILK','BONUS_IVORY_CARVINGS'],'BUILDING_INDUSTRY_DYED_FUR_SALON':['BONUS_FINE_DYES','BONUS_FINE_FURS'],'BUILDING_INDUSTRY_CROWN_JEWELER':['BONUS_GOLD_BULLION','BONUS_CUT_GEMS'],'BUILDING_INDUSTRY_ROYAL_MINT':['BONUS_GOLD_BULLION','BONUS_WORKED_SILVER'],'BUILDING_INDUSTRY_GEMCUTTERS_EXCHANGE':['BONUS_WORKED_SILVER','BONUS_CUT_GEMS'],'BUILDING_INDUSTRY_REGAL_TREASURES_COURT':['BONUS_GOLD_BULLION','BONUS_IVORY_CARVINGS'],'BUILDING_INDUSTRY_PERFUMERS_QUARTER':['BONUS_TEMPLE_INCENSE','BONUS_SPICE_BLENDS'],'BUILDING_INDUSTRY_GRAND_BANQUET_HALL':['BONUS_VINTAGE_WINE','BONUS_CONFECTIONS'],'BUILDING_INDUSTRY_CONFECTIONERS_EXCHANGE':['BONUS_CONFECTIONS','BONUS_SPICE_BLENDS'],'BUILDING_INDUSTRY_CEREMONIAL_CELLARS':['BONUS_VINTAGE_WINE','BONUS_TEMPLE_INCENSE'],'BUILDING_INDUSTRY_FESTIVAL_MARKET':['BONUS_VINTAGE_WINE','BONUS_SPICE_BLENDS'],'BUILDING_INDUSTRY_IMPERIAL_OUTFITTERS':['BONUS_FINE_FURS','BONUS_IVORY_CARVINGS'],'BUILDING_INDUSTRY_ADMIRALTY_CURIOS_HOUSE':['BONUS_LAMP_OIL','BONUS_IVORY_CARVINGS'],'BUILDING_INDUSTRY_NAVIGATORS_INSTRUMENT_WORKS':['BONUS_LAMP_OIL','BONUS_WORKED_SILVER'],'BUILDING_INDUSTRY_OPERA_HOUSE':['BONUS_STAGE_PLAYS','BONUS_MASTER_RECORDINGS'],'BUILDING_INDUSTRY_CINEMA_PALACE':['BONUS_STAGE_PLAYS','BONUS_FILM_PRINTS'],'BUILDING_INDUSTRY_SOUNDSTAGE_COMPLEX':['BONUS_MASTER_RECORDINGS','BONUS_FILM_PRINTS'],'BUILDING_INDUSTRY_MASS_ENTERTAINMENT_NETWORK':['BONUS_STAGE_PLAYS','BONUS_MASTER_RECORDINGS','BONUS_FILM_PRINTS']}
NEW_PROC=[
{'type':'BUILDING_INDUSTRY_MILLERS_GUILD','class':'BUILDINGCLASS_INDUSTRY_MILLERS_GUILD','name':"Millers' Guild",'art':'ART_DEF_BUILDING_INDUSTRY_MILLERS_GUILD','button':'millers_guild.dds','kind':'millers','tech':'TECH_CURRENCY','free':'BONUS_FLOUR','cost':120,'needs':['BUILDINGCLASS_GRANARY'],'local':[{'bonuses':['BONUS_WHEAT','BONUS_CORN','BONUS_RICE'],'min':1,'improved':1,'connected':1,'city':1}],'health':1,'foodkept':10,'flv':{'FLAVOR_GROWTH':8,'FLAVOR_GOLD':3},'tmpl':'ART_DEF_BUILDING_INDUSTRY_CONFECTIONERS_GUILD'},
{'type':'BUILDING_INDUSTRY_SMOKEHOUSE','class':'BUILDINGCLASS_INDUSTRY_SMOKEHOUSE','name':'Smokehouse','art':'ART_DEF_BUILDING_INDUSTRY_SMOKEHOUSE','button':'smokehouse.dds','kind':'smokehouse','tech':'TECH_CURRENCY','free':'BONUS_CURED_MEATS','cost':120,'needs':['BUILDINGCLASS_GRANARY'],'local':[{'bonuses':['BONUS_COW','BONUS_PIG','BONUS_SHEEP','BONUS_DEER'],'min':1,'improved':1,'connected':1,'city':1}],'health':1,'hammer':1,'flv':{'FLAVOR_PRODUCTION':7,'FLAVOR_GROWTH':4},'tmpl':'ART_DEF_BUILDING_INDUSTRY_FURRIERS_HALL'},
{'type':'BUILDING_INDUSTRY_CANNERY','class':'BUILDINGCLASS_INDUSTRY_CANNERY','name':'Cannery','art':'ART_DEF_BUILDING_INDUSTRY_CANNERY','button':'cannery.dds','kind':'cannery','tech':'TECH_COMPASS','free':'BONUS_PRESERVED_SEAFOOD','cost':150,'needs':['BUILDINGCLASS_HARBOR'],'local':[{'bonuses':['BONUS_FISH','BONUS_CLAM','BONUS_CRAB'],'min':1,'improved':1,'connected':1,'city':1}],'health':1,'gold':2,'flv':{'FLAVOR_GROWTH':5,'FLAVOR_GOLD':6},'tmpl':'ART_DEF_BUILDING_INDUSTRY_WHALE_OIL_CHANDLERY'},
{'type':'BUILDING_INDUSTRY_FRUIT_PRESERVERS','class':'BUILDINGCLASS_INDUSTRY_FRUIT_PRESERVERS','name':'Fruit Preservers','art':'ART_DEF_BUILDING_INDUSTRY_FRUIT_PRESERVERS','button':'fruit_preservers.dds','kind':'fruit_market','tech':'TECH_CALENDAR','free':'BONUS_FRUIT_PRESERVES','cost':120,'needs':['BUILDINGCLASS_MARKET'],'local':[{'bonuses':['BONUS_BANANA'],'min':1,'improved':1,'connected':1,'city':1}],'health':1,'gold':1,'culture':1,'flv':{'FLAVOR_GOLD':5,'FLAVOR_CULTURE':3,'FLAVOR_GROWTH':3},'tmpl':'ART_DEF_BUILDING_INDUSTRY_CONFECTIONERS_GUILD'}]
NEW_COMP=[
{'type':'BUILDING_INDUSTRY_BAKERS_EXCHANGE','class':'BUILDINGCLASS_INDUSTRY_BAKERS_EXCHANGE','name':"Bakers' Exchange",'art':'ART_DEF_BUILDING_INDUSTRY_BAKERS_EXCHANGE','button':'bakers_exchange.dds','kind':'bakers','tech':'TECH_CURRENCY','cost':180,'conn':['BONUS_FLOUR','BONUS_SPICE_BLENDS'],'health':1,'happy':1,'cmods':{GOLD:10},'flv':{'FLAVOR_GOLD':7,'FLAVOR_GROWTH':4},'tmpl':'ART_DEF_BUILDING_INDUSTRY_FESTIVAL_MARKET'},
{'type':'BUILDING_INDUSTRY_FESTIVAL_KITCHENS','class':'BUILDINGCLASS_INDUSTRY_FESTIVAL_KITCHENS','name':'Festival Kitchens','art':'ART_DEF_BUILDING_INDUSTRY_FESTIVAL_KITCHENS','button':'festival_kitchens.dds','kind':'festival_kitchen','tech':'TECH_MONARCHY','cost':180,'conn':['BONUS_FLOUR','BONUS_VINTAGE_WINE'],'health':1,'happy':1,'culture':2,'cmods':{GOLD:15},'flv':{'FLAVOR_GOLD':7,'FLAVOR_CULTURE':5},'tmpl':'ART_DEF_BUILDING_INDUSTRY_GRAND_BANQUET_HALL'},
{'type':'BUILDING_INDUSTRY_ROYAL_KITCHENS','class':'BUILDINGCLASS_INDUSTRY_ROYAL_KITCHENS','name':'Royal Kitchens','art':'ART_DEF_BUILDING_INDUSTRY_ROYAL_KITCHENS','button':'royal_kitchens.dds','kind':'royal_kitchen','tech':'TECH_MONARCHY','cost':190,'conn':['BONUS_CURED_MEATS','BONUS_VINTAGE_WINE'],'health':2,'happy':1,'cmods':{GOLD:15},'flv':{'FLAVOR_GOLD':6,'FLAVOR_GROWTH':5},'tmpl':'ART_DEF_BUILDING_INDUSTRY_GRAND_BANQUET_HALL'},
{'type':'BUILDING_INDUSTRY_SPICED_CARVERY','class':'BUILDINGCLASS_INDUSTRY_SPICED_CARVERY','name':'Spiced Carvery','art':'ART_DEF_BUILDING_INDUSTRY_SPICED_CARVERY','button':'spiced_carvery.dds','kind':'carvery','tech':'TECH_CALENDAR','cost':180,'conn':['BONUS_CURED_MEATS','BONUS_SPICE_BLENDS'],'health':1,'happy':1,'hammer':1,'cmods':{GOLD:10},'flv':{'FLAVOR_GOLD':6,'FLAVOR_PRODUCTION':4},'tmpl':'ART_DEF_BUILDING_INDUSTRY_CONFECTIONERS_EXCHANGE'},
{'type':'BUILDING_INDUSTRY_MARITIME_SUPPER_CLUB','class':'BUILDINGCLASS_INDUSTRY_MARITIME_SUPPER_CLUB','name':'Maritime Supper Club','art':'ART_DEF_BUILDING_INDUSTRY_MARITIME_SUPPER_CLUB','button':'maritime_supper_club.dds','kind':'maritime_supper','tech':'TECH_COMPASS','cost':190,'conn':['BONUS_PRESERVED_SEAFOOD','BONUS_VINTAGE_WINE'],'health':1,'happy':1,'culture':2,'cmods':{GOLD:10},'flv':{'FLAVOR_GOLD':6,'FLAVOR_CULTURE':5},'tmpl':'ART_DEF_BUILDING_INDUSTRY_GRAND_BANQUET_HALL'},
{'type':'BUILDING_INDUSTRY_PRESERVES_MARKET','class':'BUILDINGCLASS_INDUSTRY_PRESERVES_MARKET','name':'Preserves Market','art':'ART_DEF_BUILDING_INDUSTRY_PRESERVES_MARKET','button':'preserves_market.dds','kind':'fruit_market','tech':'TECH_CALENDAR','cost':180,'conn':['BONUS_FRUIT_PRESERVES','BONUS_CONFECTIONS'],'health':1,'happy':1,'culture':2,'cmods':{GOLD:15},'flv':{'FLAVOR_GOLD':7,'FLAVOR_CULTURE':4},'tmpl':'ART_DEF_BUILDING_INDUSTRY_CONFECTIONERS_EXCHANGE'}]
CORPS=[
('CORPORATION_1','Continental Provisions Company','TXT_KEY_CORPORATION_1','TXT_KEY_CORPORATION_1_PEDIA','TECH_REFRIGERATION',180,50,90,[4,0,0,0],['BONUS_FLOUR','BONUS_CURED_MEATS','BONUS_PRESERVED_SEAFOOD','BONUS_FRUIT_PRESERVES'],[100,0,0],[0,0,0,0],['BUILDINGCLASS_INDUSTRY_BAKERS_EXCHANGE','BUILDINGCLASS_INDUSTRY_FESTIVAL_KITCHENS','BUILDINGCLASS_INDUSTRY_ROYAL_KITCHENS','BUILDINGCLASS_INDUSTRY_SPICED_CARVERY','BUILDINGCLASS_INDUSTRY_MARITIME_SUPPER_CLUB','BUILDINGCLASS_INDUSTRY_PRESERVES_MARKET']),
('CORPORATION_2','Grand Hospitality Company','TXT_KEY_CORPORATION_2','TXT_KEY_CORPORATION_2_PEDIA','TECH_MEDICINE',180,55,100,[4,0,0,0],['BONUS_VINTAGE_WINE','BONUS_CONFECTIONS','BONUS_TEMPLE_INCENSE','BONUS_SPICE_BLENDS'],[50,0,0],[100,0,100,0],['BUILDINGCLASS_INDUSTRY_GRAND_BANQUET_HALL','BUILDINGCLASS_INDUSTRY_FESTIVAL_MARKET','BUILDINGCLASS_INDUSTRY_CEREMONIAL_CELLARS','BUILDINGCLASS_INDUSTRY_MARITIME_SUPPER_CLUB','BUILDINGCLASS_INDUSTRY_ROYAL_KITCHENS']),
('CORPORATION_3','Imperial Luxury Exchange','TXT_KEY_CORPORATION_3','TXT_KEY_CORPORATION_3_PEDIA','TECH_BANKING',170,60,110,[4,0,0,0],['BONUS_FINE_SILK','BONUS_FINE_DYES','BONUS_CUT_GEMS','BONUS_GOLD_BULLION','BONUS_WORKED_SILVER','BONUS_FINE_FURS'],[0,0,0],[250,0,100,0],['BUILDINGCLASS_INDUSTRY_ROYAL_GARMENTS_HOUSE','BUILDINGCLASS_INDUSTRY_NOBLE_TAILORS_HALL','BUILDINGCLASS_INDUSTRY_CROWN_JEWELER','BUILDINGCLASS_INDUSTRY_ROYAL_MINT','BUILDINGCLASS_INDUSTRY_GEMCUTTERS_EXCHANGE']),
('CORPORATION_4','Courtly Arts & Regalia Consortium','TXT_KEY_CORPORATION_4','TXT_KEY_CORPORATION_4_PEDIA','TECH_MASS_MEDIA',160,60,105,[4,0,0,0],['BONUS_IVORY_CARVINGS','BONUS_LAMP_OIL','BONUS_WORKED_SILVER','BONUS_FINE_FURS','BONUS_FINE_SILK'],[0,25,0],[0,0,150,100],['BUILDINGCLASS_INDUSTRY_COURT_REGALIA_ATELIER','BUILDINGCLASS_INDUSTRY_REGAL_TREASURES_COURT','BUILDINGCLASS_INDUSTRY_IMPERIAL_OUTFITTERS','BUILDINGCLASS_INDUSTRY_ADMIRALTY_CURIOS_HOUSE','BUILDINGCLASS_INDUSTRY_NAVIGATORS_INSTRUMENT_WORKS']),
('CORPORATION_5','Aromatics & Festival Consortium','TXT_KEY_CORPORATION_5','TXT_KEY_CORPORATION_5_PEDIA','TECH_BANKING',180,55,100,[4,0,0,0],['BONUS_TEMPLE_INCENSE','BONUS_SPICE_BLENDS','BONUS_CONFECTIONS','BONUS_VINTAGE_WINE'],[0,0,0],[150,0,150,0],['BUILDINGCLASS_INDUSTRY_PERFUMERS_QUARTER','BUILDINGCLASS_INDUSTRY_CONFECTIONERS_EXCHANGE','BUILDINGCLASS_INDUSTRY_CEREMONIAL_CELLARS','BUILDINGCLASS_INDUSTRY_FESTIVAL_MARKET']),
('CORPORATION_6','World Media Syndicate','TXT_KEY_CORPORATION_6','TXT_KEY_CORPORATION_6_PEDIA','TECH_MASS_MEDIA',160,65,110,[4,0,0,0],['BONUS_STAGE_PLAYS','BONUS_MASTER_RECORDINGS','BONUS_FILM_PRINTS'],[0,0,0],[100,0,200,0],['BUILDINGCLASS_INDUSTRY_OPERA_HOUSE','BUILDINGCLASS_INDUSTRY_CINEMA_PALACE','BUILDINGCLASS_INDUSTRY_SOUNDSTAGE_COMPLEX','BUILDINGCLASS_INDUSTRY_MASS_ENTERTAINMENT_NETWORK']),
('CORPORATION_7','Reserved Charter','TXT_KEY_CORPORATION_7','TXT_KEY_CORPORATION_7_PEDIA','NONE',0,0,0,[0,0,0,0],[],[0,0,0],[0,0,0,0],[])]
CORP_BLD={'BUILDING_CORPORATION_1':('TXT_KEY_CORPORATION_1','TECH_REFRIGERATION','UNITCLASS_MERCHANT','CORPORATION_1','CORPORATION_1'),'BUILDING_CORPORATION_2':('TXT_KEY_CORPORATION_2','TECH_MEDICINE','UNITCLASS_MERCHANT','CORPORATION_2','CORPORATION_2'),'BUILDING_CORPORATION_3':('TXT_KEY_CORPORATION_3','TECH_BANKING','UNITCLASS_MERCHANT','CORPORATION_3','CORPORATION_3'),'BUILDING_CORPORATION_4':('TXT_KEY_CORPORATION_4','TECH_MASS_MEDIA','UNITCLASS_ARTIST','CORPORATION_4','CORPORATION_4'),'BUILDING_CORPORATION_5':('TXT_KEY_CORPORATION_5','TECH_BANKING','UNITCLASS_MERCHANT','CORPORATION_5','CORPORATION_5'),'BUILDING_CORPORATION_6':('TXT_KEY_CORPORATION_6','TECH_MASS_MEDIA','UNITCLASS_ARTIST','CORPORATION_6','CORPORATION_6'),'BUILDING_CORPORATION_7':('TXT_KEY_CORPORATION_7','NONE','NONE','NONE','NONE')}
def blend(a,b,t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
def grad(sz,top,bot):
    img=Image.new('RGBA',(sz,sz)); p=img.load()
    for y in range(sz):
        r=blend(top,bot,y/max(1,sz-1))
        for x in range(sz): p[x,y]=r+(255,)
    return img

def goldmark(draw):
    import math
    pts=[]
    for i in range(10):
        a=-math.pi/2+i*math.pi/5; r=9 if i%2==0 else 4
        pts.append((52+math.cos(a)*r,12+math.sin(a)*r))
    draw.polygon(pts,fill=(245,205,80,255),outline=(120,74,14,255)); draw.ellipse((44,4,60,20),outline=(255,237,170,180),width=1)

def frame(img):
    d=ImageDraw.Draw(img)
    for i,a in ((0,180),(1,255)): d.rounded_rectangle((i,i,63-i,63-i),radius=10,outline=(233,198,92,a),width=1)
    v=Image.new('L',(64,64),0); dv=ImageDraw.Draw(v); dv.ellipse((-12,-12,76,76),fill=255); v=v.filter(ImageFilter.GaussianBlur(14)); q=Image.new('RGBA',(64,64),(0,0,0,0)); q.putalpha(Image.eval(v,lambda p:max(0,160-p//2))); return Image.alpha_composite(img,q)

def icon(kind):
    top,bot,main,acc,dark,light=PALETTES[kind]; img=frame(grad(64,top,bot)); d=ImageDraw.Draw(img)
    if kind in ('gems','silver','bullion'):
        if kind=='gems': d.polygon([(32,10),(48,22),(42,45),(22,45),(16,22)],fill=main,outline=light); d.line((32,10,32,45),fill=light,width=2); d.line((16,22,48,22),fill=light,width=2)
        elif kind=='silver': d.polygon([(24,16),(40,16),(36,34),(28,34)],fill=light,outline=dark); d.arc((24,28,40,48),0,180,fill=main,width=4); d.rectangle((28,34,36,46),fill=main,outline=dark)
        else: d.rounded_rectangle((14,28,36,44),radius=4,fill=main,outline=light,width=2); d.rounded_rectangle((26,18,50,34),radius=4,fill=acc,outline=light,width=2)
    elif kind in ('wine','oil','incense'):
        if kind=='wine': d.polygon([(24,12),(40,12),(36,24),(28,24)],fill=acc,outline=light); d.rectangle((30,24,34,38),fill=light); d.arc((22,34,42,48),0,180,fill=light,width=3); d.ellipse((26,12,38,20),fill=main)
        elif kind=='oil': d.polygon([(24,16),(40,16),(44,30),(20,30)],fill=main,outline=light); d.arc((24,28,40,46),0,180,fill=light,width=4)
        else: d.rounded_rectangle((16,30,48,42),radius=6,fill=dark,outline=light,width=2); d.arc((20,18,44,34),0,180,fill=light,width=3); d.arc((24,8,36,26),160,360,fill=main,width=3); d.arc((34,10,46,30),160,360,fill=acc,width=3)
    elif kind in ('plays','recordings','film'):
        if kind=='plays': d.ellipse((14,18,34,42),fill=main,outline=light); d.ellipse((30,16,50,40),fill=acc,outline=light)
        elif kind=='recordings': d.ellipse((14,14,50,50),fill=dark,outline=light,width=2); d.ellipse((28,28,36,36),fill=acc,outline=light)
        else: d.ellipse((14,14,38,38),fill=dark,outline=light,width=2); d.ellipse((26,26,50,50),fill=acc,outline=light,width=2)
    elif kind in ('flour','meats','seafood','preserves'):
        if kind=='flour': d.rounded_rectangle((18,14,46,46),radius=5,fill=main,outline=light,width=2); d.ellipse((26,26,38,34),fill=light)
        elif kind=='meats': d.polygon([(22,14),(38,14),(44,28),(32,48),(20,28)],fill=main,outline=light); d.line((32,8,32,16),fill=light,width=3)
        elif kind=='seafood': d.rounded_rectangle((14,18,50,44),radius=4,fill=dark,outline=light,width=2); d.polygon([(20,31),(32,22),(42,26),(46,31),(42,36),(32,40),(20,31)],fill=main,outline=light)
        else: d.rounded_rectangle((20,18,44,46),radius=6,fill=main,outline=light,width=2); d.rectangle((24,12,40,20),fill=dark,outline=light); d.ellipse((26,28,38,40),fill=acc,outline=light)
    else:
        if kind=='dyes': d.rounded_rectangle((14,30,48,45),radius=6,fill=dark,outline=light,width=2); d.arc((18,18,44,42),0,180,fill=light,width=3); d.polygon([(18,28),(32,14),(46,28),(42,34),(22,34)],fill=main,outline=light)
        elif kind=='furs': d.polygon([(19,14),(26,18),(32,12),(38,18),(45,14),(48,25),(40,46),(24,46),(16,25)],fill=main,outline=light)
        elif kind=='ivory': d.pieslice((16,12,46,44),220,20,fill=light,outline=dark); d.pieslice((28,18,50,50),200,20,fill=main,outline=dark)
        elif kind=='silk': d.polygon([(16,20),(44,14),(50,24),(26,30),(18,26)],fill=main,outline=light); d.polygon([(18,28),(44,22),(50,32),(26,38),(18,34)],fill=acc,outline=light)
        elif kind=='spices': d.ellipse((16,28,48,44),fill=dark,outline=light,width=2); d.polygon([(22,26),(30,18),(36,26)],fill=main,outline=light); d.polygon([(32,26),(40,18),(46,26)],fill=acc,outline=light)
        elif kind=='confections': d.rounded_rectangle((16,18,48,44),radius=6,fill=dark,outline=light,width=2); [d.ellipse((cx-5,cy-5,cx+5,cy+5),fill=main,outline=light) for cx,cy in ((24,26),(40,26),(24,38),(40,38))]
        elif kind=='millers': d.ellipse((18,16,46,44),fill=dark,outline=light,width=2); [d.line((32,30,32+dx,30+dy),fill=main,width=3) for dx,dy in ((0,-10),(10,0),(0,10),(-10,0))]
        elif kind=='smokehouse': d.polygon([(16,30),(32,16),(48,30)],fill=dark,outline=light); d.rectangle((18,30,46,46),fill=main,outline=light)
        elif kind=='cannery': d.rounded_rectangle((18,14,46,42),radius=4,fill=light,outline=dark,width=2); d.polygon([(18,28),(30,20),(42,24),(46,28),(42,32),(30,36),(18,28)],fill=main,outline=dark)
        elif kind=='fruit_market': d.rounded_rectangle((18,16,46,46),radius=5,fill=main,outline=light,width=2); d.rectangle((22,12,42,20),fill=dark,outline=light); d.ellipse((24,28,38,42),fill=acc,outline=light)
        elif kind=='bakers': d.ellipse((16,24,48,44),fill=main,outline=light); d.arc((18,14,46,34),0,180,fill=light,width=3)
        elif kind=='festival_kitchen': d.ellipse((16,28,48,42),fill=light,outline=dark,width=2); d.rectangle((28,14,36,30),fill=main,outline=light)
        elif kind=='royal_kitchen': d.arc((18,26,46,46),0,180,fill=light,width=4); d.rectangle((20,18,44,30),fill=dark,outline=light); d.polygon([(20,18),(26,10),(32,18),(38,10),(44,18)],fill=main,outline=light)
        elif kind=='carvery': d.ellipse((16,22,48,42),fill=main,outline=light); d.arc((32,12,48,28),180,360,fill=light,width=3)
        elif kind=='maritime_supper': d.ellipse((14,30,50,44),fill=light,outline=dark,width=2); d.polygon([(16,24),(28,18),(40,24),(46,30),(40,36),(28,42),(16,30)],fill=main,outline=dark)
    goldmark(d); d.rounded_rectangle((0,0,63,63),radius=10,outline=(233,198,92,255),width=1); return img
def build_effects(n,meta,gpp=0):
    setlist(n,'YieldChanges','iYield',[0,meta.get('hammer',0),0],'YieldModifiers'); setlist(n,'YieldModifiers','iYield',[0,0,0],'PowerYieldModifiers'); setlist(n,'CommerceChanges','iCommerce',[meta.get('gold',0),0,meta.get('culture',0),0],'ObsoleteSafeCommerceChanges'); setlist(n,'ObsoleteSafeCommerceChanges','iCommerce',[0,0,0,0],'CommerceChangeDoubleTimes'); setlist(n,'CommerceChangeDoubleTimes','iCommerce',[0,0,0,0],'CommerceModifiers'); mods=[0,0,0,0]
    for k,v in meta.get('cmods',{}).items(): mods[k]=v
    setlist(n,'CommerceModifiers','iCommerce',mods,'GlobalCommerceModifiers'); setc(n,'iHealth',meta.get('health',0)); setc(n,'iHappiness',meta.get('happy',0)); setc(n,'iFoodKept',meta.get('foodkept',0)); setc(n,'iGreatPeopleRateChange',gpp); specialists(n,meta.get('spec',{}))

def patch_bonus_files():
    d=parse(BONP); tmpl=by_type(d,'BonusInfo','BONUS_DRAMA')
    for b,name,art,src,btn,kind in SYN:
        n=ensure(d,'BonusInfos','BonusInfo',b,tmpl); [setc(n,t,v) for t,v in [('Type',b),('Description',f'TXT_KEY_{b}'),('Civilopedia',f'TXT_KEY_{b}_PEDIA'),('BonusClassType','BONUSCLASS_GENERAL'),('ArtDefineTag',art),('TechReveal','NONE'),('TechCityTrade','NONE'),('TechObsolete','NONE'),('iAITradeModifier',0),('iHealth',0),('iHappiness',0),('iPlacementOrder',-1),('iConstAppearance',0),('iMinAreaSize',-1),('iMinLatitude',0),('iMaxLatitude',90),('iPlayer',0),('iTilesPer',0),('iMinLandPercent',0),('iUnique',0),('iGroupRange',0),('iGroupRand',0),('bArea',0),('bHills',0),('bFlatlands',0),('bNoRiverSide',0),('bNormalize',0)]]; empty(n,'YieldChanges','iAITradeModifier');
        r=n.ownerDocument.createElement('Rands'); [r.appendChild(mk(n.ownerDocument,t,0)) for t in ('iRandApp1','iRandApp2','iRandApp3','iRandApp4')]; rep(n,r,'iPlayer'); empty(n,'TerrainBooleans','FeatureBooleans'); empty(n,'FeatureBooleans','FeatureTerrainBooleans'); empty(n,'FeatureTerrainBooleans')
    write(d,BONP)

    # Build a BtS-valid bonus file from the root source by inserting iAIObjective for every bonus.
    d=parse(BONP)
    for n in d.getElementsByTagName('BonusInfo'):
        setc(n,'iAIObjective',0,'iHealth')
    # Preserve BtS/Warlords-only synthetic-adjacent extras that buildings still reference.
    war=parse(WAR_BONP)
    have={txt(child(n,'Type')) for n in d.getElementsByTagName('BonusInfo') if child(n,'Type') is not None}
    for n in war.getElementsByTagName('BonusInfo'):
        t=txt(child(n,'Type')) if child(n,'Type') is not None else ''
        if t == 'BONUS_ASOKA' and t not in have:
            d.getElementsByTagName('BonusInfos')[0].appendChild(n.cloneNode(True))
    write(d,BONP_BTS)

    d=parse(BOAP); arts={txt(child(n,'Type')):n for n in d.getElementsByTagName('BonusArtInfo')}
    for b,name,art,src,btn,kind in SYN:
        s=arts[src]; n=ensure(d,'BonusArtInfos','BonusArtInfo',art,s); [setc(n,t,v) for t,v in [('Type',art),('fScale','1.0'),('fInterfaceScale','1.0'),('NIF',txt(child(s,'NIF'))),('KFM',txt(child(s,'KFM'))),('Button',f'Art/Interface/Buttons/Bonuses/Synthetic/{btn}')]]; sh=child(n,'SHADERNIF'); n.removeChild(sh) if sh is not None else None
    write(d,BOAP)

    # BtS art schema requires FontButtonIndex; preserve existing indices and assign new ones to synthetic entries.
    d=parse(BOAP_BTS); arts={txt(child(n,'Type')):n for n in d.getElementsByTagName('BonusArtInfo')}
    iFontMax=-1
    for n in d.getElementsByTagName('BonusArtInfo'):
        f=child(n,'FontButtonIndex')
        if f is not None:
            try: iFontMax=max(iFontMax,int(txt(f)))
            except ValueError: pass
    base=parse(BOAP); baseArts={txt(child(n,'Type')):n for n in base.getElementsByTagName('BonusArtInfo')}
    for b,name,art,src,btn,kind in SYN:
        s=baseArts[art] if art in baseArts else baseArts[src]
        n=ensure(d,'BonusArtInfos','BonusArtInfo',art,s); [setc(n,t,v) for t,v in [('Type',art),('fScale',txt(child(s,'fScale'))),('fInterfaceScale',txt(child(s,'fInterfaceScale'))),('NIF',txt(child(s,'NIF'))),('KFM',txt(child(s,'KFM'))),('Button',f'Art/Interface/Buttons/Bonuses/Synthetic/{btn}')]]; sh=child(n,'SHADERNIF'); n.removeChild(sh) if sh is not None else None
        if child(n,'FontButtonIndex') is None:
            iFontMax += 1
            setc(n,'FontButtonIndex',iFontMax)
    write(d,BOAP_BTS)

def patch_building_classes_art():
    d=parse(BCP); tmpl=by_type(d,'BuildingClassInfo','BUILDINGCLASS_INDUSTRY_DYE_WORKS')
    for meta in NEW_PROC+NEW_COMP:
        n=ensure(d,'BuildingClassInfos','BuildingClassInfo',meta['class'],tmpl); [setc(n,t,v) for t,v in [('Type',meta['class']),('Description',f'TXT_KEY_{meta["type"]}'),('iMaxGlobalInstances',-1),('iMaxTeamInstances',-1),('iMaxPlayerInstances',-1),('iExtraPlayerInstances',0),('bNoLimit',0),('bMonument',0),('DefaultBuilding',meta['type'])]]; empty(n,'VictoryThresholds')
    write(d,BCP)
    d=parse(BAP); arts={txt(child(n,'Type')):n for n in d.getElementsByTagName('BuildingArtInfo')}
    for meta in NEW_PROC+NEW_COMP:
        s=arts[meta['tmpl']]; n=ensure(d,'BuildingArtInfos','BuildingArtInfo',meta['art'],s); setc(n,'Type',meta['art']); setc(n,'Button',f'Art/Interface/Buttons/Buildings/Industries/{meta["button"]}')
    write(d,BAP)

def patch_buildings():
    d=parse(BP); idx={txt(child(n,'Type')):n for n in d.getElementsByTagName('BuildingInfo')}
    for t,b in EXIST_PROC.items():
        n=idx[t]; setc(n,'FreeBonus',b); setc(n,'iNumFreeBonuses',1); setc(n,'IndustryCategory','LUXURY'); setc(n,'bRequiresActiveLocalPrereqs',1); setc(n,'iPlayerMaxInstances',0,'iAIWeight')
    for t,bs in EXIST_COMP.items():
        n=idx[t]; setc(n,'IndustryCategory','COMPOSITE'); setc(n,'bRequiresActiveLocalPrereqs',1); setc(n,'iPlayerMaxInstances',1,'iAIWeight'); neededs(n,[]); connected_bonus_prereqs(n,[{'bonuses':[b],'min':1} for b in bs])
    tloc=idx['BUILDING_INDUSTRY_DYE_WORKS']; twh=idx['BUILDING_INDUSTRY_WHALE_OIL_CHANDLERY']; tcmp=idx['BUILDING_INDUSTRY_GRAND_BANQUET_HALL']
    for meta in NEW_PROC:
        n=ensure(d,'BuildingInfos','BuildingInfo',meta['type'],twh if meta['type']=='BUILDING_INDUSTRY_CANNERY' else tloc); [setc(n,t,v) for t,v in [('BuildingClass',meta['class']),('Type',meta['type']),('Description',f'TXT_KEY_{meta["type"]}'),('Civilopedia',f'TXT_KEY_{meta["type"]}_PEDIA'),('Strategy',f'TXT_KEY_{meta["type"]}_STRATEGY'),('Advisor','ADVISOR_ECONOMY'),('ArtDefineTag',meta['art']),('PrereqTech',meta['tech']),('Bonus','NONE'),('FreeBonus',meta['free']),('iNumFreeBonuses',1),('IndustryCategory','LUXURY'),('bRequiresActiveLocalPrereqs',1),('iCost',meta['cost']),('GreatPeopleUnitClass','NONE'),('iPlayerMaxInstances',0)]]; build_effects(n,meta); neededs(n,meta['needs']); local_bonus_prereqs(n,meta['local']); connected_bonus_prereqs(n,[]); empty(n,'LocalImprovementCountPrereqs','LocalBonusPrereqs'); flavors(n,meta['flv'])
    for meta in NEW_COMP:
        n=ensure(d,'BuildingInfos','BuildingInfo',meta['type'],tcmp); [setc(n,t,v) for t,v in [('BuildingClass',meta['class']),('Type',meta['type']),('Description',f'TXT_KEY_{meta["type"]}'),('Civilopedia',f'TXT_KEY_{meta["type"]}_PEDIA'),('Strategy',f'TXT_KEY_{meta["type"]}_STRATEGY'),('Advisor','ADVISOR_ECONOMY'),('ArtDefineTag',meta['art']),('PrereqTech',meta['tech']),('Bonus','NONE'),('FreeBonus','NONE'),('iNumFreeBonuses',0),('IndustryCategory','COMPOSITE'),('bRequiresActiveLocalPrereqs',1),('iCost',meta['cost']),('GreatPeopleUnitClass','NONE'),('iPlayerMaxInstances',1)]]; build_effects(n,meta,3); neededs(n,[]); empty(n,'LocalImprovementCountPrereqs','LocalBonusPrereqs'); empty(n,'LocalBonusPrereqs','ConnectedBonusPrereqs'); connected_bonus_prereqs(n,[{'bonuses':[b],'min':1} for b in meta['conn']]); flavors(n,meta['flv'])
    for t,(desc,tech,gp,founds,glob) in CORP_BLD.items():
        n=idx[t]; [setc(n,a,b) for a,b in [('Description',desc),('PrereqTech',tech),('GreatPeopleUnitClass',gp),('FoundsCorporation',founds),('GlobalCorporationCommerce',glob)]]
    write(d,BP)

def patch_corps_concepts():
    d=parse(CP)
    for n,meta in zip(d.getElementsByTagName('CorporationInfo'),CORPS):
        ctype,name,tag,pedia,tech,spread,cost,maint,hq,reqs,yld,com,found=meta
        [setc(n,t,v) for t,v in [('Type',ctype),('Description',tag),('Civilopedia',pedia),('TechPrereq',tech),('FreeUnitClass','NONE'),('iSpreadFactor',spread),('iSpreadCost',cost),('iMaintenance',maint),('iFoundingMinActiveBuildingClasses',99 if ctype=='CORPORATION_7' else 2),('bCountDistinctPrereqBonusesOnly',0 if ctype=='CORPORATION_7' else 1),('iMaxPrereqBonusCountPerType',0 if ctype=='CORPORATION_7' else 1),('BonusProduced','NONE'),('Button',f',Art/Interface/Buttons/TechTree/Corporation.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,{ctype[-1]},6'),('MovieFile','NONE'),('MovieSound','NONE'),('Sound','AS2D_BUILD_BANK')]]
        c=n.ownerDocument.createElement('FoundingBuildingClasses'); [c.appendChild(mk(n.ownerDocument,'BuildingClassType',b)) for b in found]; rep(n,c,'PrereqBonuses'); p=n.ownerDocument.createElement('PrereqBonuses'); [p.appendChild(mk(n.ownerDocument,'BonusType',b)) for b in reqs]; rep(n,p,'HeadquarterCommerces'); setlist(n,'HeadquarterCommerces','iHeadquarterCommerce',hq,'BonusProduced'); setlist(n,'CommercesProduced','iCommerceProduced',com,'YieldsProduced'); setlist(n,'YieldsProduced','iYieldProduced',yld,'Button')
    write(d,CP)
    d=parse(NCP); n=ensure(d,'NewConceptInfos','NewConceptInfo','CONCEPT_INDUSTRY_SUPPLY_CHAINS',d.getElementsByTagName('NewConceptInfo')[0]); [setc(n,t,v) for t,v in [('Type','CONCEPT_INDUSTRY_SUPPLY_CHAINS'),('Description','TXT_KEY_CONCEPT_INDUSTRY_SUPPLY_CHAINS'),('Civilopedia','TXT_KEY_CONCEPT_INDUSTRY_SUPPLY_CHAINS_PEDIA')]]; write(d,NCP)

def generate_art():
    BBTN.mkdir(parents=True,exist_ok=True); SBTN.mkdir(parents=True,exist_ok=True); SBTN_BTS.mkdir(parents=True,exist_ok=True)
    for b,name,art,src,btn,kind in SYN: icon(kind).save(SBTN/btn)
    for b,name,art,src,btn,kind in SYN: icon(kind).save(SBTN_BTS/btn)
    for meta in NEW_PROC+NEW_COMP: icon(meta['kind']).save(BBTN/meta['button'])

def main():
    generate_art(); patch_bonus_files(); patch_building_classes_art(); patch_buildings(); patch_corps_concepts(); print('Applied supply-chain XML/art patch set.')
if __name__=='__main__': main()
