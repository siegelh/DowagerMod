import os
import re
import shutil
import sys
import distutils.dir_util as dis
import filecmp
import winsound
from tqdm import tqdm

# Constants
version = '1.0'

print("""

***################***************###*******#*******************************************************
***################*********************************************************************************
****##########**************###*********************#***********************************************
****##########**************###*********************#***********************************************
***###########***##********#####***##*#####***+=****#**#******************************************##
##############***##********#######*###**+#**=*--=-++*=-*********************************************
###########****************######**#**#++++*=====++==-==+--+=+**************************************
##############************#####**#*+****++++#===+=-++==:=-:-:=-+************************************
##############*************##*******++++++++++++++++***=-+++=::-+==*********************************
##############*********#*#***####*##*##*****+++**#*#####**+-=-:=-:=-=*******************************
##****######***********######%#######*#****######*++++++****+-.:=+-----*****************************
#######*****************#%%%#%###%*+++=+=++***+===+++++==+******=-=+=--=****************************
#######****************#%%%#######+*+++=++**+**+++=++++++=+*****###**+=-=+**************************
***********************#%%%##%####+*++++++**#*************+++++*###**+==-=+*************************
*****************##***#%%%%%%%%##****++*++*******************+==+*****+===+*************************
***************##****#%@@%%%%%%%#***++=+=+++++++++++**++++******=+***#*++++****#********************
**************##****##%@@%%%@%%%%#*+++======------------==+++**###*+*++++***++*********************#
******###***********#%@@%%%%%%%%%#*++====---------:::------===+****++***+**++=+##*******************
*****#####**********#%%%%%%#%%%##**+=====----------:::::-----=====+++==+++*++=+##*******************
##***#######********#%%%%%##%####*++===-----------::::::::----===+++++++****+++##*******************
##***#######*******##%%#########**+====-=--------::::::::::::-=====++++++**++++*##******************
*****#######*******####%%%%#####*++===---==------:::::::::::::--==+**##*+**+++++**#*****************
*****#######*****###*#####%#####*++====---=-==-------:::::::::::-==***###*##**=++*******************
*****######*****####*#%%%%#####**++===-===--===---:::::--:::::::--=++**#*****++++*#*****************
*****####*##*****#**#%%%%%#####**+===----=--==----===---::-::::---=++*+++*#**+++=*%*****************
##***####***********#@%%%%#####*++=====-----=------====--:::::::---=+++++****+===*#*#***************
*******************##@@%%%%######**+====-==-----=======+=--:-:::--==+*+++**##*+=+###*************#**
*****************#**##%%%%%###*****+++*++=--::-==+++=---==-----:--=++++****##*++*###****************
******##*************##%%%%%##%#**+++++#*+-:::=+****##*++=---------=+==+***###*****###************##
####***************######%%%##%%#*%=-+%%#+-:::-+++==++-:-------:----===---*#%%###*******************
#######***##*********#####%#######*+=+#%#+-::::-+++====--::::----------=--##%%%#********************
##########***********####*######**++*#%##+-::::::===--::::::::-------:::--*%%%#*********************
############********##############*#####*=--::::::------:::::-------:::::+%%%##***#******#********##
############********####**######**######+=-::--:::::::::-:::----------::=@%%##%#*********#********##
############****###*####**######*#######+=---------:::::::----------::::#@@%#%%#*****************###
###################********#########%%%%#*+=+%*=-==-::::::----------:-=*%%%##%#********#*********###
###################*#####***########%%###*+-----:--=-----::---------=+=##%%##*********************##
###########**######*#######**#%########*+=---::::::-----------------==*%%%%#*#**********************
###########**######*########*#######***+=---:--::::---===----::::--=+=#%@%%##***********************
#######***##########**##*###*#%#######*++===--=--:::-------::------**=#%%%%#*******************###**
#######******#########**#**#*#%#######%##**+=====-----:--::::------+=+#%###*****#**************###**
#######******#########*******########%###****+==-----=-:-----------=%%*###**###*********************
###########**#########**####*#######%%##**+=-------:----------===##%**++#***************************
#######################################**+==-----::---=-----=+#*%#==++=-****************************
################################**#####*++==-----::--=----=*%#*+=++==+=-+##************************#
###############################****#####*+++====----=+***###**==+-+=--+**%%#******###**#***********#
###############################****##%%%###********##**#*****===-=-++*#%#%%@#***********************
################################**#%@@%%%%%%%%%%%######*==++*=*---**%%@%#%%%%%#*******************##
################################**#%@@@%%%%%%%%%%*+*+*#=+*+=+#-=-+#@%@@%%@%##%%#*****************###
######################***#######***#%%%@%%#@#***+#+++-+*--*++++++##@@@%#%@@@@@@@%#***************###
####################****#########**#%%%%%##+**#*+*+-=*-**+*-#**##%@@%%%%%##%%###%##**************###
####################****########***##%%%##%**+***+*==+++#****%%@%%@%%%@%#%@@@@%%%%%#*************###
##*######################**********##%%##**%+***#+=#+=+*=*#%@@@@@@@@@@@%%%#%%%%%%%%%##**********####
#########################*********##%%%%%%#%%***#*+*%%#%%%%%@@@%%@@@@%%####%%%%%%%%%%%##********####
########################**#**##%@@@@@@%%%%#*##*#%%@%%%%%#%#%@@@@%%@@%###%%@@@@@%%%%%%%%%#*******####
##########################%@@@@@@@@@@@@@@@@%@@@@%%%%%@##%%%%%@@@@@%##%@@@@@@%%%#####%%%%%%#****#####
######################%@@@@@@@@@@@@@@@@@@@@@@@@%%%%%%@@@@@%%@@@@%##%@%@@@%##***########%%%%##****###
###################%@@@@@@@@@@@@@@@@@@@@%%%%@@@%%%@@@@@@@@@@@@@%%@@%@@@%################%#%%%#***###
################%@@@@@@@@@@@@@@@@@@@@@@@%%%@@@@%%%%%@@@@@@@@@%%@@%@@%%%%####********####%%%%%%#**###
##############@@@@@@@@@@@@@@@@@@@@@@@@@@%%@@@@%###@@@%@@@@@%@@@%@@@%%%%%#************####%%%%@%#####
############%@@@@@@@@@@@@@@@@%@@@@@@@@@@@%@@@%%@@%@%@@@@@@@@%%@@@%%%%%####*************##%%%%%%#####
###########@@@@@@@@@@@@@@@@@@@@@@@@@%%@@@@@@%@@@@@@@@@@@@@@@@@@%%%%%##******************##%%%%@%####
##########@@@@@@@@@@@@@@@@%%@@@@@@@%@@@@@@@@@@@%@@@@@@@@@@@@@%%%%#######*******#********###%%%@%####
########%@@@@@@@@@%@@@@@@##@@@@@@%@@@@@@%%@@@@@%%@@@@@@@@@@@%%%############***#*****+****##%%%%%####
#######%@@%@@@@@@@@@@@@@%%@@@@@@@@@@@%#%%%@%%@@%@@@@@@@@%@@@%%%#%%%%%%%###**#****+++*****##%%%%%%##*
#####%@@%%@@@@@@@@%%@@@*%@@@@@@@@@@%%@@@%%%%@@@%@@@@@@%%@@@%%%%%%%@%%#######****+++******###%%%%%%##
#####@@@%@@@@@@@@%@@@##%@@@@@@@@@@%@@@@@@@@@@%@@@@@@@%%%@@@%%%%@@%%%#######****++********###%%%%%%##
#####@@@@@@@@@@%%@@%%*@@@@@@@@@@%@@@@@%@@@@@@@@@@@@@%%%@@@%%%@@%%%#######*****++*********###%%%%%%##
####%@@@@@@@@@@@%@@#%@@@@@@@@%##@@@@@@@%%%@@@@@%%@@%%%%@@@%%%%%%%%%#####******+**********###%%%%%%%#
####@@@@@@@%%@@%@#=*%%@@@%@%%#%@@%@%@@@@%@@@@@%%%%%#%@@@@@%%%%%%%%%%###*************+****###%%%%%%%%
###%@@@@@@%@@@@@+##%%@#*#%%%#@@@%%@%@@@@@@@@@%#%@###%@@@@%%%%@@%%%#####******************###%%%%%%%%
##@@@@@@%%@#%%%%#%#%@#+#%**@@@@@@@%@@@@@@@@%#%%%#**#@@@@%%%@@@%%%%%%%%#******************###%%%%%%%%
#%@@@@@@@@@%%%##%%%#*#%#%%@@@@@@@@@@%@@@@@%####%#*#%@@@@%@@@@%%%%%%%##*******************####%%%%%%%
      
__        __   _                            _                  
\ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___            
 \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \           
  \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |          
 __\_/\_/ \___|_|\___\___/|_| |_| |_|\___|__\__\___/       _ _ 
|  _ \  _____      ____ _  __ _  ___ _ __|  \/  | ___   __| | |
| | | |/ _ \ \ /\ / / _` |/ _` |/ _ \ '__| |\/| |/ _ \ / _` | |
| |_| | (_) \ V  V / (_| | (_| |  __/ |  | |  | | (_) | (_| |_|
|____/ \___/ \_/\_/ \__,_|\__, |\___|_|  |_|  |_|\___/ \__,_(_)
                          |___/                                
      
      """)

# Check for Windows OS
if os.name != 'nt':
    print("Windows is required to run this installer. Sorry for the inconvenience.")
    sys.exit(0)
else:
    print("You are installing HarrisonMod version %s, please wait..." % version)
    winsound.PlaySound('install_noise.wav', winsound.SND_FILENAME)

## Functions
def _looks_like_bts_install(path):
    """Return True if path looks like a real Civ4 BtS install (has the BtS subdir or Assets)."""
    if not path or not os.path.isdir(path):
        return False
    bts_marker = os.path.join(path, "Beyond the Sword", "Assets")
    return os.path.isdir(bts_marker)

def _candidate_steam_paths(civ_drive):
    """Return an ordered list of likely Civ 4 BTS install paths to probe."""
    drive = civ_drive.rstrip("\\:").upper() + ":\\"
    name = "Sid Meier's Civilization IV Beyond the Sword"
    candidates = []

    # 1) Explicit override via env var — instant exit, no prompt
    env_path = os.environ.get("CIV4_BTS_PATH")
    if env_path:
        candidates.append(env_path)

    # 2) Common Steam library locations on the chosen drive
    common_roots = [
        os.path.join(drive, "Program Files (x86)", "Steam"),
        os.path.join(drive, "Program Files", "Steam"),
        os.path.join(drive, "Steam"),
        os.path.join(drive, "SteamLibrary"),
        os.path.join(drive, "Games", "Steam"),
    ]
    for root in common_roots:
        candidates.append(os.path.join(root, "steamapps", "common", name))

    # 3) Parse Steam's libraryfolders.vdf (each Steam install lists every library across all drives).
    #    This finds installs even on drives the user didn't pick.
    vdf_candidates = [
        r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf",
        r"C:\Program Files\Steam\steamapps\libraryfolders.vdf",
    ]
    for vdf in vdf_candidates:
        if not os.path.isfile(vdf):
            continue
        try:
            with open(vdf, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except Exception:
            continue
        # libraryfolders.vdf has lines like:    "path"    "D:\\SteamLibrary"
        for match in re.finditer(r'"path"\s*"([^"]+)"', text):
            lib_path = match.group(1).replace("\\\\", "\\")
            candidates.append(os.path.join(lib_path, "steamapps", "common", name))

    # Dedupe while preserving order
    seen = set()
    unique = []
    for c in candidates:
        key = os.path.normcase(os.path.normpath(c))
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique

def findPath(civ_drive):
    """
    Returns either the path where Civ 4 BtS is installed or 'Failed'.

    Strategy:
      1. Try CIV4_BTS_PATH env var.
      2. Try common Steam library paths on the chosen drive (~instant).
      3. Try every Steam library listed in libraryfolders.vdf (~instant).
      4. Fall back to a full os.walk of the chosen drive (slow last resort).
    """
    # Fast path: probe known candidates first
    for candidate in _candidate_steam_paths(civ_drive):
        if _looks_like_bts_install(candidate):
            print("""
                ---------------------------------
                Civ 4 BTS install found (fast path)
                ---------------------------------

                {0}

                """.format(candidate))
            response = input("Is this the correct directory? [y / n]: ").strip().lower()
            if response == "y":
                return candidate

    # Slow fallback: original drive walk
    print("Fast-path candidates exhausted. Falling back to a full drive scan (this can take a while)...")
    for root, directories, filenames in os.walk(civ_drive.upper()):
        for directory in directories:
            current_path = os.path.join(root, directory).replace("\n", '\\')
            if "\\Sid Meier's Civilization IV Beyond the Sword" in current_path and "steamapps" in current_path.lower():
                print("""
                ---------------------------------
                Civ 4 BTS Assets Directory found!
                ---------------------------------

                {0}

                """.format(current_path))
                response = input("Is this the correct directory? [y / n]: ")
                response = response.lower()
                if response == "y":
                    return current_path
    return "Failed"

def copy_file(src, dst):
    """Copy file from src to dst if it has been modified."""
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
    else:
        src_stat = os.stat(src)
        dst_stat = os.stat(dst)
        if src_stat.st_mtime > dst_stat.st_mtime or src_stat.st_size != dst_stat.st_size:
            shutil.copy2(src, dst)

def installMod(src_path, civ_path):
    # Calculate the total number of files
    total_files = sum(len(files) for _, _, files in os.walk(src_path))
    progress_bar = tqdm(total=total_files, desc='Installing HarrisonMod', unit='file')
    
    for root, dirs, files in os.walk(src_path):
        relative_path = os.path.relpath(root, src_path)
        dest_path = os.path.join(civ_path, relative_path)
        
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_path, file)
            copy_file(src_file, dst_file)
            progress_bar.update(1)
    
    progress_bar.close()
    print('Finished installing HarrisonMod version %s!' % version)

## Fetch install path
src_path = sys.argv[0][:-16].replace('/', '\\') + "Sid Meier's Civilization IV Beyond the Sword"

# Prompt the user for the drive where they think the game is installed.
civ_drive = input('Type the letter drive name (caps insensitive) where Civ Beyond the Sword is installed (e.g., C): ')
civ_path = findPath(civ_drive + ":\\")
if civ_path == "Failed":
    print("Could not find Assets directory. Installation failed. Goodbye!")
else:
    print("""
    
    Installing HarrisonMod to {0}
          
    Beginning installation. This may take a few minutes, please wait.
    
    """.format(civ_path))
    installMod(src_path, civ_path)
    input('Success! Click enter to exit setup.')
