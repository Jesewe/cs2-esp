import os
import sys
import struct
from typing import Dict, List, Optional

import requests
import pymem

def read_vec3(mem: pymem.Pymem, address: int) -> Dict[str, float]:
    """
    Reads a 3D vector (three floats) from memory at the specified address.
    """
    return {
        "x": mem.read_float(address),
        "y": mem.read_float(address + 4),
        "z": mem.read_float(address + 8)
    }

def read_string(mem: pymem.Pymem, address: int, max_length: int = 256) -> str:
    """
    Reads a null-terminated string from memory at the specified address.
    """
    data = mem.read_bytes(address, max_length)
    string_data = data.split(b'\x00')[0]
    return string_data.decode('utf-8', errors='replace')

def read_floats(mem: pymem.Pymem, address: int, count: int) -> List[float]:
    """
    Reads an array of `count` floats from memory.
    """
    data = mem.read_bytes(address, count * 4)
    return list(struct.unpack(f'{count}f', data))

def transliterate(text: str) -> str:
    """
    Converts Cyrillic characters in the given text to their Latin equivalents.
    """
    mapping = {
        'А': 'A',  'а': 'a',
        'Б': 'B',  'б': 'b',
        'В': 'V',  'в': 'v',
        'Г': 'G',  'г': 'g',
        'Д': 'D',  'д': 'd',
        'Е': 'E',  'е': 'e',
        'Ё': 'Yo', 'ё': 'yo',
        'Ж': 'Zh', 'ж': 'zh',
        'З': 'Z',  'з': 'z',
        'И': 'I',  'и': 'i',
        'Й': 'I',  'й': 'i',  # "Й" → "I"
        'К': 'K',  'к': 'k',
        'Л': 'L',  'л': 'l',
        'М': 'M',  'м': 'm',
        'Н': 'N',  'н': 'n',
        'О': 'O',  'о': 'o',
        'П': 'P',  'п': 'p',
        'Р': 'R',  'р': 'r',
        'С': 'S',  'с': 's',
        'Т': 'T',  'т': 't',
        'У': 'U',  'у': 'u',
        'Ф': 'F',  'ф': 'f',
        'Х': 'Kh', 'х': 'kh',
        'Ц': 'Ts', 'ц': 'ts',
        'Ч': 'Ch', 'ч': 'ch',
        'Ш': 'Sh', 'ш': 'sh',
        'Щ': 'Shch', 'щ': 'shch',
        'Ъ': '',   'ъ': '',
        'Ы': 'Y',  'ы': 'y',
        'Ь': '',   'ь': '',
        'Э': 'E',  'э': 'e',
        'Ю': 'Yu', 'ю': 'yu',
        'Я': 'Ya', 'я': 'ya'
    }
    return "".join(mapping.get(char, char) for char in text)

def resource_path(relative_path: str) -> str:
    """
    Returns the absolute path to a resource, supporting both development
    and PyInstaller's _MEIPASS environment.
    """
    try:
        if hasattr(sys, '_MEIPASS'):
            # If the application is frozen, use the _MEIPASS path.
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    except Exception as e:
        return f"Failed to get resource path: {e}"

def check_for_updates(current_version: str) -> Dict[str, Optional[str]]:
    """
    Checks for updates by querying the GitHub API for the latest release.
    """
    url = "https://api.github.com/repos/Jesewe/cs2-esp/releases/latest"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        latest_version = data.get("tag_name", "")
        update_available = compare_versions(latest_version, current_version)
        return {
            "update_available": update_available,
            "latest_version": latest_version,
        }
    except Exception as e:
        return {"error": str(e)}

def compare_versions(latest: str, current: str) -> bool:
    """
    Compares two semantic version strings.
    """
    def parse_version(v: str) -> List[int]:
        # Remove a leading 'v' if present and split by '.'
        return [int(x) for x in v.lstrip("v").split(".")]
    
    try:
        return parse_version(latest) > parse_version(current)
    except Exception:
        return False