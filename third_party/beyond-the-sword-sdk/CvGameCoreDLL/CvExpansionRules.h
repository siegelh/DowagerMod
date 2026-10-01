#ifndef CV_EXPANSION_RULES_H
#define CV_EXPANSION_RULES_H

#include <cassert>

namespace ExpansionRules
{
	inline int cappedContribution(int iCount, int iPerItem, int iCap)
	{
		assert(iCount >= 0 && iPerItem >= 0 && iCap >= 0);
		if (iPerItem == 0)
			return 0;
		return iCount > iCap / iPerItem ? iCap : iCount * iPerItem;
	}

	inline int distinctForeignTeams(const int* aiTeams, int iCount, int iOwnTeam)
	{
		int iResult = 0;
		for (int i = 0; i < iCount; ++i)
		{
			if (aiTeams[i] < 0 || aiTeams[i] == iOwnTeam)
				continue;
			int j = 0;
			for (; j < i; ++j)
			{
				if (aiTeams[j] == aiTeams[i])
					break;
			}
			if (j == i)
				++iResult;
		}
		return iResult;
	}

	inline bool eligibleResearchPartner(bool bAlive, bool bSameTeam, bool bAtWar,
		bool bOpenBorders, bool bOurVassal, bool bTheirVassal, bool bKnowsTech)
	{
		return bAlive && !bSameTeam && !bAtWar && bOpenBorders &&
			!bOurVassal && !bTheirVassal && bKnowsTech;
	}

	inline int conquestOccupationTurns(int iNativeTurns, int iReductionPercent)
	{
		assert(iNativeTurns >= 0);
		assert(iReductionPercent >= 0 && iReductionPercent <= 100);
		// Subtract floor(reduction) to round remaining turns up without overflow.
		return iNativeTurns - (iNativeTurns / 100) * iReductionPercent -
			((iNativeTurns % 100) * iReductionPercent) / 100;
	}
}

#endif
