import CvScreenUtils
import CvIndustryAdvisor

class CvIndustryScreenUtils(CvScreenUtils.CvScreenUtils):
    def __init__(self):
        self.screen = CvIndustryAdvisor.getIndustryAdvisor()

    def _matchesIndustryScreen(self, screenRef):
        return screenRef == CvIndustryAdvisor.INDUSTRY_ADVISOR_SCREEN or screenRef == self.screen.SCREEN_NAME

    def handleInput(self, argsList):
        screenEnum, inputClass = argsList
        if self._matchesIndustryScreen(screenEnum):
            return self.screen.handleInput(inputClass)
        return 0

    def update(self, argsList):
        screenEnum = argsList[0]
        if self._matchesIndustryScreen(screenEnum):
            self.screen.update(argsList[1])
            return 1
        return 0

    def onClose(self, argsList):
        screenEnum = argsList[0]
        if self._matchesIndustryScreen(screenEnum):
            self.screen.onClose()
            return 1
        return 0
