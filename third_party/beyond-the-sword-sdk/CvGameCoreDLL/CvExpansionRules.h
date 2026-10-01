#ifndef CV_EXPANSION_RULES_H
#define CV_EXPANSION_RULES_H

#include <cassert>

namespace ExpansionRules
{
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
