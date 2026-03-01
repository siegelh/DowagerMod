#include "CvGameCoreDLL.h"

#include "CvGameCoreDLLUndefNew.h"

#include <new>

#include "CvGlobals.h"
#include "FProfiler.h"
#include "CvDLLInterfaceIFaceBase.h"
#include <stdarg.h>

namespace
{
	char g_szDllTracePath[MAX_PATH] = "";
	volatile LONG g_iDllTraceSequence = 0;
	LPTOP_LEVEL_EXCEPTION_FILTER g_pPreviousUnhandledExceptionFilter = NULL;

	void initDllTracePath(HMODULE hModule)
	{
		DWORD iLength = GetModuleFileNameA((HMODULE)hModule, g_szDllTracePath, MAX_PATH);
		if (iLength == 0 || iLength >= MAX_PATH)
		{
			lstrcpyA(g_szDllTracePath, "CvGameCoreDLL_trace.log");
			return;
		}

		char* pszFileName = strrchr(g_szDllTracePath, '\\');
		if (pszFileName != NULL)
		{
			*(pszFileName + 1) = '\0';
			lstrcatA(g_szDllTracePath, "CvGameCoreDLL_trace.log");
		}
		else
		{
			lstrcpyA(g_szDllTracePath, "CvGameCoreDLL_trace.log");
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

		return EXCEPTION_CONTINUE_SEARCH;
	}
}

void dllTrace(const char* pszCategory, const char* pszFormat, ...)
{
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
