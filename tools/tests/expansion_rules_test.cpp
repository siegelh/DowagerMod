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
	{
		std::printf("FAIL: INT_MAX occupation boundary\n");
		return 2;
	}
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
	for (int iCount = 0; iCount <= 100; ++iCount)
	{
		for (int iPerItem = 0; iPerItem <= 10; ++iPerItem)
		{
			for (int iCap = 0; iCap <= 100; ++iCap)
			{
				const int iProduct = iCount * iPerItem;
				const int iExpected = iProduct < iCap ? iProduct : iCap;
				if (ExpansionRules::cappedContribution(iCount, iPerItem, iCap) != iExpected)
				{
					std::printf("FAIL cap count=%d per=%d cap=%d\n", iCount, iPerItem, iCap);
					return 4;
				}
				++iCases;
			}
		}
	}
	for (int iCase = 0; iCase < 7776; ++iCase)
	{
		int aiTeams[5];
		int iDigits = iCase;
		int iMask = 0;
		for (int i = 0; i < 5; ++i)
		{
			aiTeams[i] = iDigits % 6 - 1;
			iDigits /= 6;
			if (aiTeams[i] > 0)
				iMask |= 1 << aiTeams[i];
		}
		int iExpected = 0;
		for (int iTeam = 1; iTeam <= 4; ++iTeam)
			if ((iMask & (1 << iTeam)) != 0)
				++iExpected;
		const int iActual = ExpansionRules::distinctForeignTeams(aiTeams, 5, 0);
		if (iActual != iExpected ||
			ExpansionRules::cappedContribution(iActual, 1, 3) != (iExpected < 3 ? iExpected : 3))
		{
			std::printf("FAIL route configuration=%d expected=%d actual=%d\n", iCase, iExpected, iActual);
			return 5;
		}
		++iCases;
	}
	if (ExpansionRules::distinctForeignTeams(NULL, 0, 0) != 0 ||
		ExpansionRules::cappedContribution(INT_MAX, INT_MAX, 3) != 3 ||
		ExpansionRules::cappedContribution(INT_MAX, 1, INT_MAX) != INT_MAX)
	{
		std::printf("FAIL: empty routes or overflow-safe cap boundary\n");
		return 6;
	}
	std::printf("PASS: %d exact occupation/eligibility/cap/route cases plus empty and INT_MAX boundaries\n", iCases);
	return 0;
}
