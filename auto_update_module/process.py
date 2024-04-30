import ctypes
from ctypes import wintypes


kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD)
    ]

def run_exe(exe_name):
    start_info = ctypes.create_string_buffer(68)
    start_info.dwFlags = 0x00000080  # STARTF_FORCEOFFFEEDBACK
    
    process_info = PROCESS_INFORMATION()
    
    if not kernel32.CreateProcessW(None, ctypes.c_wchar_p(exe_name), None, None, False, 0, None, None, ctypes.byref(start_info), ctypes.byref(process_info)):
        return False
    
    user32.WaitForInputIdle(process_info.hProcess, 0xFFFFFFFF)
    kernel32.CloseHandle(process_info.hThread)
    kernel32.CloseHandle(process_info.hProcess)