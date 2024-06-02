import ctypes
import paths
import platform
import os
import subprocess

from cryptography.fernet import Fernet

current_os = platform.system()


def encrypt():
    with open(paths.KEY, 'wb') as filekey:
        key = Fernet.generate_key()
        filekey.write(key)
    if os.path.exists(paths.KEY and paths.USER_JSON):
        with open(paths.KEY, 'rb') as filekey:
            key = filekey.read()
        fern = Fernet(key)
        with open(paths.USER_JSON, 'rb') as file:
            original = file.read()
        encrypted = fern.encrypt(original)
        with open(paths.USER_JSON, 'wb') as file:
            file.write(encrypted)
    if current_os == 'Windows':
        ctypes.windll.kernel32.SetFileAttributesW(paths.KEY, 0x80)
    elif current_os == 'Darwin':
        subprocess.run(['chflags', 'nohidden', paths.KEY])


def decrypt():
    if os.path.exists(paths.KEY and paths.USER_JSON):
        with open(paths.KEY, 'rb') as filekey:
            key = filekey.read()
        fern = Fernet(key)
        with open(paths.USER_JSON, 'rb') as file:
            original = file.read()
        decrypted = fern.decrypt(original)
        with open(paths.USER_JSON, 'wb') as file:
            file.write(decrypted)
    if current_os == 'Windows':
        ctypes.windll.kernel32.SetFileAttributesW(paths.KEY, 0x80)
    elif current_os == 'Darwin':
        subprocess.run(['chflags', 'hidden', paths.KEY])
