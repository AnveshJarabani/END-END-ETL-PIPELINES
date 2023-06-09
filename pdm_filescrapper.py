import ctypes
from ctypes import wintypes

# Constants
MAX_PATH = 260
FILE_ATTRIBUTE_DIRECTORY = 0x10
FILE_ATTRIBUTE_NORMAL = 0x80

# Structures
class WIN32_FIND_DATAW(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", wintypes.DWORD),
        ("ftCreationTime", wintypes.FILETIME),
        ("ftLastAccessTime", wintypes.FILETIME),
        ("ftLastWriteTime", wintypes.FILETIME),
        ("nFileSizeHigh", wintypes.DWORD),
        ("nFileSizeLow", wintypes.DWORD),
        ("dwReserved0", wintypes.DWORD),
        ("dwReserved1", wintypes.DWORD),
        ("cFileName", wintypes.WCHAR * MAX_PATH),
        ("cAlternateFileName", wintypes.WCHAR * 14)
    ]

# Functions
FindFirstFileW = ctypes.windll.kernel32.FindFirstFileW
FindNextFileW = ctypes.windll.kernel32.FindNextFileW
FindClose = ctypes.windll.kernel32.FindClose

FindFirstFileW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(WIN32_FIND_DATAW)]
FindNextFileW.argtypes = [wintypes.HANDLE, ctypes.POINTER(WIN32_FIND_DATAW)]
FindClose.argtypes = [wintypes.HANDLE]

# Get current directory
current_dir = ctypes.create_unicode_buffer(MAX_PATH)
ctypes.windll.kernel32.GetCurrentDirectoryW(MAX_PATH, current_dir)

# Find files in the current directory
search_path = current_dir.value + "\\*"
find_data = WIN32_FIND_DATAW()
handle = FindFirstFileW(search_path, ctypes.byref(find_data))

if handle != -1:
    while True:
        # Check if it's a file (not a directory)
        if not (find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY):
            file_name = find_data.cFileName
            print(file_name)
        
        # Move to the next file
        if not FindNextFileW(handle, ctypes.byref(find_data)):
            break

    # Close the search handle
    FindClose(handle)
