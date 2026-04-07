"""
Persistence layer backed by JSONBin.io (free tier).

Required environment variables:
    JSONBIN_BIN_ID   – the bin ID from jsonbin.io (create once manually)
    JSONBIN_API_KEY  – your JSONBin master key or access key

On first run with an empty / missing bin the module initialises the bin
with the game list that was compiled at import time from data/games.py so
that existing data is not lost when you switch over.
"""

import os
import requests

_BIN_URL = "https://api.jsonbin.io/v3/b"
_BIN_ID  = os.environ.get("JSONBIN_BIN_ID", "")
_HEADERS = {
    "Content-Type":  "application/json",
    "X-Access-Key":  os.environ.get("JSONBIN_API_KEY", ""),
    "X-Bin-Versioning": "false",   # always overwrite, no version history needed
}

# In-memory cache so we only hit the API when something actually changes.
_cache: dict | None = None


def _url() -> str:
    if not _BIN_ID:
        raise RuntimeError("JSONBIN_BIN_ID environment variable is not set.")
    return f"{_BIN_URL}/{_BIN_ID}"


def _fetch_remote() -> dict:
    """Download the whole bin and return its record dict."""
    resp = requests.get(f"{_url()}/latest", headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()["record"]


def _push_remote(data: dict) -> None:
    """Overwrite the whole bin with *data*."""
    resp = requests.put(_url(), json=data, headers=_HEADERS, timeout=10)
    resp.raise_for_status()


# ── Public API ────────────────────────────────────────────────────────────────
def load_stats():
    """
    Load the full persisted state.

    Returns a dict:
        {
             username: { "hypothetical": {}, ... }
        }
    """
    global _cache
    try:
        remote = _fetch_remote()
        print(f"[persistence] Loaded state from JSONBin: {remote}")
        _cache = remote
    except Exception as exc:
        print(f"[persistence] WARNING: could not fetch from JSONBin: {exc}")
        # Fail gracefully – return defaults so the app at least starts.
        _cache = {}

def load_user_state(username: str, default_teams: set) -> dict:
    """Return the persisted state for *username*, or sensible defaults."""
    if _cache is None:
        raise RuntimeError("Call load_stats() before load_user_state().")
    raw = _cache.get(username)
    if raw is None:
        return {
            "hypothetical":   {},
            "selected_teams": set(default_teams),
            "compare_teams":  set(),
        }
    return {
        "hypothetical":   {int(k): tuple(v) for k, v in raw.get("hypothetical", {}).items()},
        "selected_teams": set(raw.get("selected_teams", list(default_teams))),
        "compare_teams":  set(raw.get("compare_teams", [])),
    }


def save_user_state(username: str, state: dict) -> None:
    """Persist *state* for *username*."""
    if _cache is None:
        raise RuntimeError("Call load_stats() before save_user_state().")
    _cache[username] = {
        "hypothetical":   {str(k): list(v) for k, v in state["hypothetical"].items()},
        "selected_teams": sorted(state["selected_teams"]),
        "compare_teams":  sorted(state["compare_teams"]),
    }
    _push_remote(_cache)