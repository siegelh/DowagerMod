"""Drop a fake chatter request into the spool dir to trigger the running daemon."""
from __future__ import annotations
import argparse, json, sys, time, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--trigger", default="DECLARE_WAR")
    p.add_argument("--speaker", default="Lincoln")
    p.add_argument("--target", default="Victoria")
    p.add_argument("--n-lines", type=int, default=3)
    p.add_argument("--game-turn", type=int, default=120)
    args = p.parse_args()
    from tools.chatter import config as cfg_mod
    from tools.chatter.spool import gen_filename, REQ_PREFIX, atomic_write_json
    cfg = cfg_mod.load_config()
    spool = cfg_mod.spool_dir()
    rid = str(uuid.uuid4())
    request = {
        "schema": 1, "request_id": rid, "session_id": str(uuid.uuid4()),
        "game_turn": args.game_turn, "elector_player_id": 0, "trigger": args.trigger,
        "mode": "directed",
        "speaker": {"player_id": 0, "leader_name": args.speaker, "civ_short_name": "Test", "score": 100, "is_barbarian": False},
        "target":  {"player_id": 1, "leader_name": args.target,  "civ_short_name": "Test", "score": 100, "is_barbarian": False},
        "context": {"era": "Renaissance"},
        "multi_turn": True, "n_lines": args.n_lines,
        "issued_at_unix": time.time(), "ttl_seconds": 60,
    }
    fname = gen_filename(REQ_PREFIX)
    out_path = spool / fname
    atomic_write_json(out_path, request)
    print(f"injected: {out_path.name}")
    print(f"  trigger={args.trigger} speaker={args.speaker} target={args.target}")
    print(f"  daemon should pick this up within 1 second")
    return 0


if __name__ == "__main__":
    sys.exit(main())
