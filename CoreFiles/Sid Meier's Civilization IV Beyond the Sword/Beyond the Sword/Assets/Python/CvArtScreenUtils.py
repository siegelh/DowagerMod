import CvScreenUtils
import CvArtAdvisor


class CvArtScreenUtils(CvScreenUtils.CvScreenUtils):
    def __init__(self):
        self.screen = CvArtAdvisor.getArtAdvisor()

    def _matchesArtScreen(self, screenRef):
        return screenRef == CvArtAdvisor.ART_ADVISOR_SCREEN or screenRef == self.screen.SCREEN_NAME

    def handleInput(self, argsList):
        screenEnum, inputClass = argsList
        if self._matchesArtScreen(screenEnum):
            return self.screen.handleInput(inputClass)
        return 0

    def update(self, argsList):
        screenEnum = argsList[0]
        if self._matchesArtScreen(screenEnum):
            self.screen.update(argsList[1])
            return 1
        return 0

    def onClose(self, argsList):
        screenEnum = argsList[0]
        if self._matchesArtScreen(screenEnum):
            self.screen.onClose()
            return 1
        return 0
