import imp
import os


def _loadMainInterfaceImplementation():
    currentDir = os.path.dirname(os.path.abspath(__file__))
    implementationPath = os.path.normpath(os.path.join(
        currentDir,
        "..",
        "..",
        "Art",
        "Leaderheads",
        "new",
        "petromod_v1",
        "Assets",
        "Python",
        "Screens",
        "CvMainInterface.py",
    ))
    return imp.load_source("DowagerModCvMainInterfaceImpl", implementationPath)


_impl = _loadMainInterfaceImplementation()

for _name in dir(_impl):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_impl, _name)
