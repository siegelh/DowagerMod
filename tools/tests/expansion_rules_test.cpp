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
	for (int iCondition = -1; iCondition <= 4; ++iCondition)
	{
		for (int iBits = 0; iBits < 2048; ++iBits)
		{
			const bool bBase = (iBits & 31) == 7;
			const bool bExpected = bBase &&
				((iCondition == ExpansionRules::RIVERSIDE_IMPROVEMENT && (iBits & 96) == 96) ||
				(iCondition == ExpansionRules::WOODLAND && (iBits & 128) != 0) ||
				(iCondition == ExpansionRules::DESERT_ROAD_IMPROVEMENT && (iBits & 1792) == 1792));
			const bool bActual = ExpansionRules::eligibleWorkedPlot(
				(ExpansionRules::WorkedPlotCondition)iCondition, (iBits & 1) != 0,
				(iBits & 2) != 0, (iBits & 4) != 0, (iBits & 8) != 0,
				(iBits & 16) != 0, (iBits & 32) != 0, (iBits & 64) != 0,
				(iBits & 128) != 0, (iBits & 256) != 0, (iBits & 512) != 0, (iBits & 1024) != 0);
			if (bActual != bExpected)
			{
				std::printf("FAIL worked plot condition=%d bits=%d\n", iCondition, iBits);
				return 7;
			}
			++iCases;
		}
	}
	for (int iOthers = 0; iOthers <= 21; ++iOthers)
	{
		for (int iPerItem = 0; iPerItem <= 100; ++iPerItem)
		{
			for (int iCap = 0; iCap <= 100; ++iCap)
			{
				const int iBefore = iOthers * iPerItem < iCap ? iOthers * iPerItem : iCap;
				const int iAfter = (iOthers + 1) * iPerItem < iCap ? (iOthers + 1) * iPerItem : iCap;
				if (ExpansionRules::cappedMarginal(iOthers, true, iPerItem, iCap) != iAfter - iBefore ||
					ExpansionRules::cappedMarginal(iOthers, false, iPerItem, iCap) != 0)
				{
					std::printf("FAIL marginal others=%d per=%d cap=%d\n", iOthers, iPerItem, iCap);
					return 8;
				}
				iCases += 2;
			}
		}
	}
	if (ExpansionRules::cappedMarginal(INT_MAX, true, 1, INT_MAX) != 0 ||
		ExpansionRules::cappedMarginal(0, true, INT_MAX, INT_MAX) != INT_MAX ||
		ExpansionRules::cappedMarginal(INT_MAX, true, 0, INT_MAX) != 0 ||
		ExpansionRules::cappedMarginal(INT_MAX - 1, true, 1, INT_MAX) != 1)
	{
		std::printf("FAIL: overflow-safe marginal boundary\n");
		return 9;
	}
	for (int iBits = 0; iBits < 64; ++iBits)
	{
		for (int iMinimum = 0; iMinimum <= 100; ++iMinimum)
		{
			for (int iLevel = 0; iLevel <= 110; ++iLevel)
			{
				const bool bExpected = iBits == 7 && iMinimum > 0 && iLevel >= iMinimum;
				const bool bActual = ExpansionRules::eligibleVeteranGarrison(
					(iBits & 1) != 0, (iBits & 2) != 0, (iBits & 4) != 0,
					(iBits & 8) != 0, (iBits & 16) != 0, (iBits & 32) != 0, iLevel, iMinimum);
				if (bActual != bExpected)
				{
					std::printf("FAIL veteran bits=%d minimum=%d level=%d\n", iBits, iMinimum, iLevel);
					return 10;
				}
				++iCases;
			}
		}
	}
	if (!ExpansionRules::eligibleVeteranGarrison(true, true, true, false, false, false, INT_MAX, INT_MAX) ||
		ExpansionRules::eligibleVeteranGarrison(true, true, true, false, false, false, INT_MAX - 1, INT_MAX))
	{
		std::printf("FAIL: veteran level boundary\n");
		return 11;
	}
	std::printf("PASS: %d exact occupation/research/cap/route/worked-plot/marginal/veteran cases plus empty and INT_MAX boundaries\n", iCases);
	return 0;
}
