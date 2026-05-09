from __future__ import annotations
import os, shutil, subprocess, sys
from pathlib import Path

def same_drive(a, b):
    try:
        ra = str(a.resolve()); rb = str(b.resolve())
        return ra.split(':',1)[0].lower() == rb.split(':',1)[0].lower()
    except Exception:
        return False


def install_from_pristine_or_hot(live, pristine, pristine_hot, robocopy_fn):
    if pristine_hot.exists() and same_drive(pristine_hot, live):
        print(f'Fast path: renaming {pristine_hot.name} -> {live.name}')
        old_dir = live.with_name(live.name + ' - DELETE_ME')
        if old_dir.exists():
            shutil.rmtree(old_dir, ignore_errors=True)
        if live.exists():
            os.rename(str(live), str(old_dir))
        os.rename(str(pristine_hot), str(live))
        print('  Cleaning up old live dir...')
        try:
            shutil.rmtree(old_dir)
        except Exception as exc:
            print(f'  WARN: could not delete {old_dir}: {exc}')
        return True
    print('Slow path: full robocopy from PRISTINE (no HOT yet).')
    robocopy_fn(pristine, live, mirror=True, label='restore pristine')
    return False


def kickoff_background_hot_rebuild(pristine, pristine_hot):
    '''Spawn detached subprocess to robocopy pristine -> pristine_hot. Non-blocking.'''
    if not pristine.exists():
        return
    if pristine_hot.exists():
        try:
            shutil.rmtree(pristine_hot)
        except Exception:
            return
    args = ['robocopy', str(pristine), str(pristine_hot), '/MIR', '/NP', '/NFL', '/NDL', '/R:1', '/W:1', '/MT:8']
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    try:
        subprocess.Popen(args, creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    except Exception as exc:
        print(f'  WARN: could not spawn background HOT rebuild: {exc}')

