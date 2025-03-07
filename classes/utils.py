import os
import sys
import struct
import logging
from packaging import version
from typing import Dict, List, Optional

import requests
import pymem

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def read_vec3(mem: pymem.Pymem, address: int) -> Dict[str, float]:
    """
    Reads a 3D vector (three floats) from memory at the specified address.
    """
    try:
        return {
            "x": mem.read_float(address),
            "y": mem.read_float(address + 4),
            "z": mem.read_float(address + 8)
        }
    except Exception as e:
        logging.error("Failed to read vec3 at address %s: %s", hex(address), e)
        return {"x": 0.0, "y": 0.0, "z": 0.0}

def read_string(mem: pymem.Pymem, address: int, max_length: int = 256) -> str:
    """
    Reads a null-terminated string from memory at the specified address.
    """
    try:
        data = mem.read_bytes(address, max_length)
        string_data = data.split(b'\x00')[0]
        return string_data.decode('utf-8', errors='replace')
    except Exception as e:
        logging.error("Failed to read string at address %s: %s", hex(address), e)
        return ""

def read_floats(mem: pymem.Pymem, address: int, count: int) -> List[float]:
    """
    Reads an array of `count` floats from memory.
    """
    try:
        data = mem.read_bytes(address, count * 4)
        return list(struct.unpack(f'{count}f', data))
    except Exception as e:
        logging.error("Failed to read %d floats at address %s: %s", count, hex(address), e)
        return []

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
        'Й': 'I',  'й': 'i',
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
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    absolute_path = os.path.join(base_path, relative_path)
    if not os.path.exists(absolute_path):
        logging.warning("Resource not found at path: %s", absolute_path)
    return absolute_path

def check_for_updates(current_version):
    """
    Checks the GitHub repository for the latest version of the software.
    Compares the current version with the latest version and returns the update URL if an update is available.
    """
    try:
        # Fetch the latest release data from the GitHub API
        response = requests.get("https://api.github.com/repos/Jesewe/cs2-esp/releases/latest")
        response.raise_for_status()

        # Parse the JSON response and extract the latest version and release URL
        latest_release = response.json()
        latest_version = latest_release["tag_name"]
        update_url = latest_release["html_url"]

        if version.parse(latest_version) > version.parse(current_version):
            # Log that a new update is available
            logging.info(f"New version available: {latest_version}.")
            return update_url
        else:
            # Log that no updates are available
            logging.info("No new updates available.")
            return None
    except requests.exceptions.RequestException as e:
        # Log the request exception details if any errors occur during the process
        logging.error(f"Update check failed: {e}")
        return None
    except Exception as e:
        # Log any other exceptions that may occur
        logging.error(f"An unexpected error occurred during update check: {e}")
        return None