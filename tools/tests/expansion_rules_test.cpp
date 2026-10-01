#include "CvExpansionRules.h"
#include <cstdio>
#include <climits>

int main()
{
	int iCases = 0;
	for (int iTurns = 0; iTurns <= 1000; ++iTurns)
	{
		for (int iReduction = 0; iReduction <= 100; ++iReduction)
		{
			const int iExpected = (iTurns * (100 - iReduction) + 99) / 100;
			if (ExpansionRules::conquestOccupationTurns(iTurns, iReduction) != iExpected)
			{
				std::printf("FAIL turns=%d reduction=%d expected=%d\n", iTurns, iReduction, iExpected);
				return 1;
			}
			++iCases;
		}
	}
	if (ExpansionRules::conquestOccupationTurns(INT_MAX, 50) != INT_MAX / 2 + 1)
		return 2;
	for (int iBits = 0; iBits < 128; ++iBits)
	{
		const bool bActual = ExpansionRules::eligibleResearchPartner(
			(iBits & 1) != 0, (iBits & 2) != 0, (iBits & 4) != 0,
			(iBits & 8) != 0, (iBits & 16) != 0, (iBits & 32) != 0, (iBits & 64) != 0);
		if (bActual != (iBits == (1 | 8 | 64)))
		{
			std::printf("FAIL research eligibility bits=%d\n", iBits);
			return 3;
		}
		++iCases;
	}
	std::printf("PASS: %d exact occupation/eligibility cases plus INT_MAX overflow boundary\n", iCases);
	return 0;
}
