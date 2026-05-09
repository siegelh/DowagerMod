from __future__ import annotations
import os, shutil, subprocess, sys, time
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


def build_pristine_hot(pristine, pristine_hot, log_path=None):
    '''Build pristine_hot SYNCHRONOUSLY by robocopy from pristine.

    Blocking. Streams robocopy output to the console so the user sees progress
    in the installer window. Returns dict {ok: bool, error?: str, elapsed?: float}.

    Synchronous because detached subprocess on a UAC-elevated PyInstaller .exe
    is unreliable (child dies when parent exits even with DETACHED_PROCESS).
    Trading "instant install" for "guaranteed-built HOT" -- next install will
    then use the rename fast path.
    '''
    if not pristine.exists():
        return {'ok': False, 'error': 'pristine directory does not exist'}
    if pristine_hot.exists():
        try:
            shutil.rmtree(pristine_hot)
        except Exception as exc:
            return {'ok': False, 'error': 'could not remove stale HOT: ' + str(exc)}

    # /NFL /NDL keeps output readable; /NP suppresses per-file progress %.
    # /MT:16 uses 16 threads (most modern machines handle this fine).
    args = [
        'robocopy', str(pristine), str(pristine_hot),
        '/MIR', '/NFL', '/NDL', '/NP', '/R:1', '/W:1', '/MT:16',
    ]
    t0 = time.time()
    try:
        # Inherit stdout/stderr so robocopy's summary streams live to the console.
        rc = subprocess.call(args)
    except Exception as exc:
        return {'ok': False, 'error': 'robocopy raised: ' + repr(exc)}
    elapsed = time.time() - t0

    # Robocopy exit codes: 0-7 are success-ish (8+ are failures).
    # See https://ss64.com/nt/robocopy-exit.html
    if rc >= 8:
        return {'ok': False, 'error': 'robocopy rc=' + str(rc), 'elapsed': elapsed}
    if not pristine_hot.exists():
        return {'ok': False, 'error': 'HOT did not appear after robocopy', 'elapsed': elapsed}
    return {'ok': True, 'elapsed': elapsed, 'rc': rc}

