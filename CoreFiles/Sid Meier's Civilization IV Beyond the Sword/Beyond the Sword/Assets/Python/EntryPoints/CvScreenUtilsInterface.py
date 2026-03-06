import CvScreenUtils

industryScreenUtils = None
artScreenUtils = None

try:
    import CvIndustryScreenUtils
    industryScreenUtils = CvIndustryScreenUtils.CvIndustryScreenUtils()
except:
    industryScreenUtils = None

try:
    import CvArtScreenUtils
    artScreenUtils = CvArtScreenUtils.CvArtScreenUtils()
except:
    artScreenUtils = None


class CompositeScreenUtils:
    def __init__(self):
        self.defaultScreenUtils = CvScreenUtils.CvScreenUtils()
        self.industryScreenUtils = industryScreenUtils
        self.artScreenUtils = artScreenUtils

    def _dispatchIndustry(self, methodName, argsList):
        if self.industryScreenUtils is None:
            return 0
        try:
            return getattr(self.industryScreenUtils, methodName)(argsList)
        except:
            return 0

    def _dispatchArt(self, methodName, argsList):
        if self.artScreenUtils is None:
            return 0
        try:
            return getattr(self.artScreenUtils, methodName)(argsList)
        except:
            return 0

    def handleInput(self, argsList):
        if self._dispatchIndustry("handleInput", argsList):
            return 1
        if self._dispatchArt("handleInput", argsList):
            return 1
        return self.defaultScreenUtils.handleInput(argsList)

    def update(self, argsList):
        if self._dispatchIndustry("update", argsList):
            return 1
        if self._dispatchArt("update", argsList):
            return 1
        return self.defaultScreenUtils.update(argsList)

    def onClose(self, argsList):
        if self._dispatchIndustry("onClose", argsList):
            return 1
        if self._dispatchArt("onClose", argsList):
            return 1
        return self.defaultScreenUtils.onClose(argsList)

    def __getattr__(self, name):
        return getattr(self.defaultScreenUtils, name)


normalScreenUtils = CompositeScreenUtils()


def getScreenUtils():
    return normalScreenUtils
