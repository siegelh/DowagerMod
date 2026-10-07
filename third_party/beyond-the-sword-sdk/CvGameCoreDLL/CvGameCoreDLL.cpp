#include "CvGameCoreDLL.h"

#include "CvGameCoreDLLUndefNew.h"

#include <new>

#include "CvGlobals.h"
#include "FProfiler.h"
#include "CvDLLInterfaceIFaceBase.h"
#include <stdarg.h>
#include <DbgHelp.h>

namespace
{
	const int MAX_CRASH_DUMP_FILES = 3;
	const ULONGLONG MAX_CRASH_DUMP_BYTES = 250ULL * 1024ULL * 1024ULL;
	char g_szDllTracePath[MAX_PATH] = "";
	char g_szDllTraceDir[MAX_PATH] = "";
	char g_szCrashDumpDir[MAX_PATH] = "";
	volatile LONG g_iDllTraceSequence = 0;
	LPTOP_LEVEL_EXCEPTION_FILTER g_pPreviousUnhandledExceptionFilter = NULL;
	bool g_bDllTraceEnabled = false;
	bool g_bCityTraceEnabled = false;

	bool isEnvVarTruthy(const char* pszName)
	{
		char szValue[32];
		DWORD iLength = GetEnvironmentVariableA(pszName, szValue, sizeof(szValue));
		if (iLength == 0 || iLength >= sizeof(szValue))
		{
			return false;
		}

		szValue[sizeof(szValue) - 1] = '\0';
		return (_stricmp(szValue, "1") == 0
			|| _stricmp(szValue, "true") == 0
			|| _stricmp(szValue, "yes") == 0
			|| _stricmp(szValue, "on") == 0);
	}

	bool fileExists(const char* pszPath)
	{
		if (pszPath == NULL || pszPath[0] == '\0')
		{
			return false;
		}

		DWORD dwAttributes = GetFileAttributesA(pszPath);
		return (dwAttributes != INVALID_FILE_ATTRIBUTES) && !(dwAttributes & FILE_ATTRIBUTE_DIRECTORY);
	}

	void buildTraceControlPath(char* pszOut, size_t iOutSize, const char* pszFileName)
	{
		if (pszOut == NULL || iOutSize == 0)
		{
			return;
		}

		pszOut[0] = '\0';
		if (g_szDllTraceDir[0] == '\0' || pszFileName == NULL)
		{
			return;
		}

		_snprintf(pszOut, iOutSize - 1, "%s%s", g_szDllTraceDir, pszFileName);
		pszOut[iOutSize - 1] = '\0';
	}

	void refreshDllTraceSettings()
	{
		char szGlobalToggle[MAX_PATH];
		char szCityToggle[MAX_PATH];
		buildTraceControlPath(szGlobalToggle, sizeof(szGlobalToggle), "CvGameCoreDLL_trace.on");
		buildTraceControlPath(szCityToggle, sizeof(szCityToggle), "CvGameCoreDLL_city_trace.on");

		g_bCityTraceEnabled = isEnvVarTruthy("CIV4_DLL_CITY_TRACE") || fileExists(szCityToggle);
		g_bDllTraceEnabled = g_bCityTraceEnabled || isEnvVarTruthy("CIV4_DLL_TRACE") || fileExists(szGlobalToggle);
	}

	void initDllTracePath(HMODULE hModule)
	{
		DWORD iLength = GetModuleFileNameA((HMODULE)hModule, g_szDllTracePath, MAX_PATH);
		if (iLength == 0 || iLength >= MAX_PATH)
		{
			lstrcpyA(g_szDllTracePath, "CvGameCoreDLL_trace.log");
			g_szDllTraceDir[0] = '\0';
			return;
		}

		char* pszFileName = strrchr(g_szDllTracePath, '\\');
		if (pszFileName != NULL)
		{
			*(pszFileName + 1) = '\0';
			lstrcpyA(g_szDllTraceDir, g_szDllTracePath);
			*(pszFileName + 1) = '\0';
			lstrcatA(g_szDllTracePath, "CvGameCoreDLL_trace.log");
		}
		else
		{
			lstrcpyA(g_szDllTracePath, "CvGameCoreDLL_trace.log");
			g_szDllTraceDir[0] = '\0';
		}
	}

	void appendDllTraceLine(const char* pszLine)
	{
		if (g_szDllTracePath[0] == '\0' || pszLine == NULL)
		{
			return;
		}

		HANDLE hFile = CreateFileA(g_szDllTracePath, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
		if (hFile == INVALID_HANDLE_VALUE)
		{
			return;
		}

		SetFilePointer(hFile, 0, NULL, FILE_END);

		DWORD dwWritten = 0;
		WriteFile(hFile, pszLine, (DWORD)strlen(pszLine), &dwWritten, NULL);
		FlushFileBuffers(hFile);
		CloseHandle(hFile);
	}

	void resetDllTraceLog()
	{
		if (g_szDllTracePath[0] == '\0')
		{
			return;
		}

		HANDLE hFile = CreateFileA(g_szDllTracePath, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
		if (hFile != INVALID_HANDLE_VALUE)
		{
			CloseHandle(hFile);
		}
	}

	bool createDirectoryIfMissing(const char* pszPath)
	{
		if (pszPath == NULL || pszPath[0] == '\0')
		{
			return false;
		}

		if (CreateDirectoryA(pszPath, NULL))
		{
			return true;
		}

		return GetLastError() == ERROR_ALREADY_EXISTS;
	}

	void initCrashDumpDirectory()
	{
		char szLocalAppData[MAX_PATH];
		DWORD iLength = GetEnvironmentVariableA("LOCALAPPDATA", szLocalAppData, sizeof(szLocalAppData));
		if (iLength == 0 || iLength >= sizeof(szLocalAppData))
		{
			g_szCrashDumpDir[0] = '\0';
			return;
		}

		szLocalAppData[sizeof(szLocalAppData) - 1] = '\0';

		char szDowagerDir[MAX_PATH];
		char szReportsDir[MAX_PATH];
		_snprintf(szDowagerDir, sizeof(szDowagerDir) - 1, "%s\\DowagerMod", szLocalAppData);
		szDowagerDir[sizeof(szDowagerDir) - 1] = '\0';
		_snprintf(szReportsDir, sizeof(szReportsDir) - 1, "%s\\CrashReports", szDowagerDir);
		szReportsDir[sizeof(szReportsDir) - 1] = '\0';
		_snprintf(g_szCrashDumpDir, sizeof(g_szCrashDumpDir) - 1, "%s\\Pending", szReportsDir);
		g_szCrashDumpDir[sizeof(g_szCrashDumpDir) - 1] = '\0';

		if (!createDirectoryIfMissing(szDowagerDir)
			|| !createDirectoryIfMissing(szReportsDir)
			|| !createDirectoryIfMissing(g_szCrashDumpDir))
		{
			g_szCrashDumpDir[0] = '\0';
		}
	}

	bool scanCrashDumps(
		int& iCount,
		ULONGLONG& iTotalBytes,
		char* pszOldestPath,
		size_t iOldestPathSize)
	{
		iCount = 0;
		iTotalBytes = 0;
		if (pszOldestPath != NULL && iOldestPathSize > 0)
		{
			pszOldestPath[0] = '\0';
		}

		if (g_szCrashDumpDir[0] == '\0')
		{
			return false;
		}

		char szPattern[MAX_PATH];
		_snprintf(szPattern, sizeof(szPattern) - 1, "%s\\*.dmp", g_szCrashDumpDir);
		szPattern[sizeof(szPattern) - 1] = '\0';

		WIN32_FIND_DATAA kFindData;
		HANDLE hFind = FindFirstFileA(szPattern, &kFindData);
		if (hFind == INVALID_HANDLE_VALUE)
		{
			return true;
		}

		FILETIME kOldestWriteTime;
		kOldestWriteTime.dwLowDateTime = 0;
		kOldestWriteTime.dwHighDateTime = 0;
		bool bHaveOldest = false;

		do
		{
			if ((kFindData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0)
			{
				continue;
			}

			++iCount;
			ULARGE_INTEGER kFileSize;
			kFileSize.LowPart = kFindData.nFileSizeLow;
			kFileSize.HighPart = kFindData.nFileSizeHigh;
			iTotalBytes += kFileSize.QuadPart;

			if (!bHaveOldest || CompareFileTime(&kFindData.ftLastWriteTime, &kOldestWriteTime) < 0)
			{
				kOldestWriteTime = kFindData.ftLastWriteTime;
				bHaveOldest = true;
				if (pszOldestPath != NULL && iOldestPathSize > 0)
				{
					_snprintf(pszOldestPath, iOldestPathSize - 1, "%s\\%s", g_szCrashDumpDir, kFindData.cFileName);
					pszOldestPath[iOldestPathSize - 1] = '\0';
				}
			}
		}
		while (FindNextFileA(hFind, &kFindData));

		FindClose(hFind);
		return true;
	}

	void pruneCrashDumps()
	{
		if (g_szCrashDumpDir[0] == '\0')
		{
			return;
		}

		for (;;)
		{
			int iCount = 0;
			ULONGLONG iTotalBytes = 0;
			char szOldestPath[MAX_PATH];
			if (!scanCrashDumps(iCount, iTotalBytes, szOldestPath, sizeof(szOldestPath)))
			{
				return;
			}
			if (iCount <= MAX_CRASH_DUMP_FILES && iTotalBytes <= MAX_CRASH_DUMP_BYTES)
			{
				return;
			}
			if (szOldestPath[0] == '\0' || !DeleteFileA(szOldestPath))
			{
				return;
			}
		}
	}

	bool writeCrashDump(EXCEPTION_POINTERS* pExceptionInfo, char* pszDumpPath, size_t iDumpPathSize, DWORD& iError)
	{
		iError = ERROR_SUCCESS;
		if (pszDumpPath != NULL && iDumpPathSize > 0)
		{
			pszDumpPath[0] = '\0';
		}
		if (pExceptionInfo == NULL || g_szCrashDumpDir[0] == '\0')
		{
			iError = ERROR_INVALID_PARAMETER;
			return false;
		}

		SYSTEMTIME kTime;
		GetLocalTime(&kTime);
		char szDumpPath[MAX_PATH];
		_snprintf(
			szDumpPath,
			sizeof(szDumpPath) - 1,
			"%s\\DowagerMod-Crash-%04d%02d%02d-%02d%02d%02d-%03d-pid%lu.dmp",
			g_szCrashDumpDir,
			kTime.wYear,
			kTime.wMonth,
			kTime.wDay,
			kTime.wHour,
			kTime.wMinute,
			kTime.wSecond,
			kTime.wMilliseconds,
			GetCurrentProcessId());
		szDumpPath[sizeof(szDumpPath) - 1] = '\0';

		HANDLE hDump = CreateFileA(
			szDumpPath,
			GENERIC_WRITE,
			FILE_SHARE_READ,
			NULL,
			CREATE_NEW,
			FILE_ATTRIBUTE_NORMAL,
			NULL);
		if (hDump == INVALID_HANDLE_VALUE)
		{
			iError = GetLastError();
			return false;
		}

		MINIDUMP_EXCEPTION_INFORMATION kExceptionInfo;
		kExceptionInfo.ThreadId = GetCurrentThreadId();
		kExceptionInfo.ExceptionPointers = pExceptionInfo;
		kExceptionInfo.ClientPointers = FALSE;

		BOOL bWroteDump = MiniDumpWriteDump(
			GetCurrentProcess(),
			GetCurrentProcessId(),
			hDump,
			MiniDumpNormal,
			&kExceptionInfo,
			NULL,
			NULL);
		if (!bWroteDump)
		{
			iError = GetLastError();
		}
		CloseHandle(hDump);

		if (!bWroteDump)
		{
			DeleteFileA(szDumpPath);
			return false;
		}

		if (pszDumpPath != NULL && iDumpPathSize > 0)
		{
			lstrcpynA(pszDumpPath, szDumpPath, (int)iDumpPathSize);
		}
		return true;
	}

	LONG WINAPI CvGameCoreUnhandledExceptionFilter(EXCEPTION_POINTERS* pExceptionInfo)
	{
		if (pExceptionInfo != NULL && pExceptionInfo->ExceptionRecord != NULL)
		{
			EXCEPTION_RECORD* pRecord = pExceptionInfo->ExceptionRecord;
			void* pInstruction = NULL;
			#if defined(_M_IX86)
			if (pExceptionInfo->ContextRecord != NULL)
			{
				pInstruction = (void*)pExceptionInfo->ContextRecord->Eip;
			}
			#endif
			dllTrace("CRASH", "Unhandled exception code=0x%08X address=%p flags=0x%08X instruction=%p", pRecord->ExceptionCode, pRecord->ExceptionAddress, pRecord->ExceptionFlags, pInstruction);
		}
		else
		{
			dllTrace("CRASH", "Unhandled exception with no exception record");
		}

		char szDumpPath[MAX_PATH];
		DWORD iDumpError = ERROR_SUCCESS;
		if (writeCrashDump(pExceptionInfo, szDumpPath, sizeof(szDumpPath), iDumpError))
		{
			dllTrace("CRASH", "Minidump written path=%s", szDumpPath);
		}
		else
		{
			dllTrace("CRASH", "Minidump failed error=%lu", iDumpError);
		}

		return EXCEPTION_CONTINUE_SEARCH;
	}
}

bool isDllTraceEnabled()
{
	return g_bDllTraceEnabled;
}

bool isCityTraceEnabled()
{
	return g_bCityTraceEnabled;
}

void dllTrace(const char* pszCategory, const char* pszFormat, ...)
{
	const bool bIsCrashTrace = (pszCategory != NULL && strcmp(pszCategory, "CRASH") == 0);
	if (!bIsCrashTrace && !g_bDllTraceEnabled)
	{
		return;
	}

	char szMessage[2048];
	va_list args;
	va_start(args, pszFormat);
	_vsnprintf(szMessage, sizeof(szMessage) - 1, pszFormat, args);
	va_end(args);
	szMessage[sizeof(szMessage) - 1] = '\0';

	SYSTEMTIME kTime;
	GetLocalTime(&kTime);

	const LONG iSequence = InterlockedIncrement(&g_iDllTraceSequence);
	char szLine[2560];
	_snprintf(
		szLine,
		sizeof(szLine) - 1,
		"%04d-%02d-%02d %02d:%02d:%02d.%03d [%06ld] [pid:%lu tid:%lu] [%s] %s\r\n",
		kTime.wYear,
		kTime.wMonth,
		kTime.wDay,
		kTime.wHour,
		kTime.wMinute,
		kTime.wSecond,
		kTime.wMilliseconds,
		iSequence,
		GetCurrentProcessId(),
		GetCurrentThreadId(),
		(pszCategory != NULL) ? pszCategory : "TRACE",
		szMessage);
	szLine[sizeof(szLine) - 1] = '\0';

	appendDllTraceLine(szLine);
}

//
// operator global new and delete override for gamecore DLL 
//
void *__cdecl operator new(size_t size)
{
	if (gDLL)
	{
		return gDLL->newMem(size, __FILE__, __LINE__);
	}
	return malloc(size);
}

void __cdecl operator delete (void *p)
{
	if (gDLL)
	{
		gDLL->delMem(p, __FILE__, __LINE__);
	}
	else
	{
		free(p);
	}
}

void* operator new[](size_t size)
{
	if (gDLL)
		return gDLL->newMemArray(size, __FILE__, __LINE__);
	return malloc(size);
}

void operator delete[](void* pvMem)
{
	if (gDLL)
	{
		gDLL->delMemArray(pvMem, __FILE__, __LINE__);
	}
	else
	{
		free(pvMem);
	}
}

void *__cdecl operator new(size_t size, char* pcFile, int iLine)
{
	return gDLL->newMem(size, pcFile, iLine);
}

void *__cdecl operator new[](size_t size, char* pcFile, int iLine)
{
	return gDLL->newMem(size, pcFile, iLine);
}

void __cdecl operator delete(void* pvMem, char* pcFile, int iLine)
{
	gDLL->delMem(pvMem, pcFile, iLine);
}

void __cdecl operator delete[](void* pvMem, char* pcFile, int iLine)
{
	gDLL->delMem(pvMem, pcFile, iLine);
}


void* reallocMem(void* a, unsigned int uiBytes, const char* pcFile, int iLine)
{
	return gDLL->reallocMem(a, uiBytes, pcFile, iLine);
}

unsigned int memSize(void* a)
{
	return gDLL->memSize(a);
}

BOOL APIENTRY DllMain(HANDLE hModule, 
					  DWORD  ul_reason_for_call, 
					  LPVOID lpReserved)
{
	switch( ul_reason_for_call ) {
	case DLL_PROCESS_ATTACH:
		{
		// The DLL is being loaded into the virtual address space of the current process as a result of the process starting up 
		OutputDebugString("DLL_PROCESS_ATTACH\n");
		initDllTracePath((HMODULE)hModule);
		initCrashDumpDirectory();
		pruneCrashDumps();
		refreshDllTraceSettings();
		resetDllTraceLog();
		g_pPreviousUnhandledExceptionFilter = SetUnhandledExceptionFilter(CvGameCoreUnhandledExceptionFilter);
		dllTrace("DLL", "PROCESS_ATTACH module=%p", hModule);

		// set timer precision
		MMRESULT iTimeSet = timeBeginPeriod(1);		// set timeGetTime and sleep resolution to 1 ms, otherwise it's 10-16ms
		FAssertMsg(iTimeSet==TIMERR_NOERROR, "failed setting timer resolution to 1 ms");
		}
		break;
	case DLL_THREAD_ATTACH:
		// OutputDebugString("DLL_THREAD_ATTACH\n");
		break;
	case DLL_THREAD_DETACH:
		// OutputDebugString("DLL_THREAD_DETACH\n");
		break;
	case DLL_PROCESS_DETACH:
		OutputDebugString("DLL_PROCESS_DETACH\n");
		dllTrace("DLL", "PROCESS_DETACH");
		if (g_pPreviousUnhandledExceptionFilter != NULL)
		{
			SetUnhandledExceptionFilter(g_pPreviousUnhandledExceptionFilter);
			g_pPreviousUnhandledExceptionFilter = NULL;
		}
		timeEndPeriod(1);
		GC.setDLLIFace(NULL);
		break;
	}
	
	return TRUE;	// success
}

//
// enable dll profiler if necessary, clear history
//
void startProfilingDLL()
{
	if (GC.isDLLProfilerEnabled())
	{
		gDLL->ProfilerBegin();
	}
}

//
// dump profile stats on-screen
//
void stopProfilingDLL()
{
	if (GC.isDLLProfilerEnabled())
	{
		gDLL->ProfilerEnd();
	}
}
