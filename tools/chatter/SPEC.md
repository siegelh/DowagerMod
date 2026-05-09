# Chatter Spool JSON Schemas

The game and sidecar communicate via JSON files under
`%LOCALAPPDATA%\DowagerMod\chatter\spool\`.

All writes are atomic (write to `*.tmp` + `os.rename`).

## Request: `req-<utc>-<seq>.json`

Written by the game (elector machine only). Sidecar reads + deletes.

```json
{
  "schema": 1,
  "request_id": "<uuid>",
  "session_id": "<uuid>",
  "game_turn": 142,
  "elector_player_id": 7,
  "trigger": "DECLARE_WAR",
  "mode": "directed",
  "speaker": {
    "player_id": 13,
    "leader_name": "Victoria",
    "civ_short_name": "England",
    "score": 3120
  },
  "target": {
    "player_id": 4,
    "leader_name": "Lincoln",
    "civ_short_name": "America",
    "score": 980
  },
  "context": {
    "era": "Industrial",
    "city": "Berlin",
    "wonder": "Pyramids",
    "tech": "Iron Working",
    "religion": "Buddhism",
    "corporation": "Standard Ethanol"
  },
  "multi_turn": false,
  "n_lines": 1,
  "issued_at_unix": 1714770000.123,
  "ttl_seconds": 60
}
```

- `mode`: `"directed"` (1-to-1) or `"broadcast"` (proclamation).
- `multi_turn`: if `true`, sidecar generates an N-line script (Approach B).
- `n_lines`: how many lines to generate (1-3).
- `context`: trigger-specific extras. Only relevant fields are populated.

## Response: `resp-<utc>-<seq>.json`

Written by sidecar. Game reads + deletes.

```json
{
  "schema": 1,
  "request_id": "<uuid>",
  "session_id": "<uuid>",
  "elector_player_id": 7,
  "ok": true,
  "lines": [
    {
      "speaker_player_id": 13,
      "speaker_name": "Victoria",
      "text": "Mr. Lincoln, your republic shall find that the Crown's patience is refined, but its displeasure is most industriously dreadful.",
      "delay_ms": 0
    },
    {
      "speaker_player_id": 4,
      "speaker_name": "Lincoln",
      "text": "Madam, your cannon smoke may cloud the air, yet this republic has weathered thicker fogs than Victorian manners ever produced.",
      "delay_ms": 7000
    }
  ],
  "error": null,
  "latency_ms": 1842,
  "input_tokens": 246,
  "output_tokens": 138,
  "completed_at_unix": 1714770001.965
}
```

- `ok`: `true` on success, `false` if the API call failed or was refused.
- `lines`: 1+ entries. Each has speaker info + text + relative delay from
  the previous line in milliseconds.
- `error`: human-readable error string if `ok` is `false`. Game-side
  drops these silently.
- The first line always has `delay_ms: 0`. Subsequent lines have a
  randomized 5000-10000 ms (configurable) delay so the conversation
  paces out in real time.

## Filename convention

`req-<YYYYMMDDTHHMMSS>-<6char-random>.json`
`resp-<YYYYMMDDTHHMMSS>-<6char-random>.json`

The request_id (UUID) inside the file is the canonical join key; the
filename is just for sortability and uniqueness. Sidecar matches request
to response by `request_id`, not by filename.

## Lifecycle

1. Game writes `req-*.json` atomically (`*.tmp` + rename).
2. Sidecar polls spool dir every `spool_poll_interval_seconds`.
3. Sidecar processes each request (calls Foundry).
4. Sidecar writes `resp-*.json` atomically.
5. Sidecar deletes the matching `req-*.json`.
6. Game polls on `onUpdate` / `onBeginPlayerTurn`, finds matching
   `resp-*.json` by `request_id`, queues lines for display, deletes
   the response file.
7. Janitor (sidecar): deletes any `req-*.json` older than
   `request_ttl_seconds` (presumed orphan).
8. Janitor (sidecar): deletes any `resp-*.json` older than
   `response_ttl_seconds` (presumed unconsumed by game).
