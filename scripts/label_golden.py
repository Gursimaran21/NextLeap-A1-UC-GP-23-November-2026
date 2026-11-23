"""Interactive golden-set labeling helper.

Walks through data/golden_set.csv and asks for HUMAN labels.
Never fabricates labels; only saves what you enter.

Usage:
    python -m scripts.label_golden          # label rows with blank/TODO labels
    python -m scripts.label_golden --all    # relabel every row
    python -m scripts.label_golden --limit 5

After labeling:
    python -m src.eval
    python -m scripts.qa_check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402


def _theme_codes() -> list[str]:
    return [t["code"] for t in config.THEMES]


def _theme_legend() -> str:
    lines = []
    for t in config.THEMES:
        lines.append(f"  {t['code']}  — {t['meaning']}")
    return "\n".join(lines)


def _is_unlabelled(value: object) -> bool:
    s = str(value).strip()
    return s == "" or s.lower() in {"todo", "to_fill", "nan", "none"}


def _prompt_theme(current: str) -> str:
    codes = _theme_codes()
    while True:
        raw = input(f"Primary theme [{current or 'blank'}]: ").strip()
        if raw == "" and not _is_unlabelled(current):
            return current
        if raw == "":
            print("  A theme is required (or type 'skip' / 'quit').")
            continue
        if raw.upper() in codes:
            return raw.upper()
        # allow short form like T1
        matches = [c for c in codes if c.split("_")[0] == raw.upper()]
        if len(matches) == 1:
            return matches[0]
        print(f"  Invalid theme. Use one of: {', '.join(codes)}")


def _prompt_return_signal(current: str) -> str:
    signals = list(config.RETURN_SIGNALS)
    while True:
        raw = input(f"Return signal ({'/'.join(signals)}) [{current or 'blank'}]: ").strip().lower()
        if raw == "" and not _is_unlabelled(current):
            return current
        if raw in signals:
            return raw
        print(f"  Invalid return signal. Use one of: {', '.join(signals)}")


def _save(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manually label the golden set (no fabrication).")
    parser.add_argument("--all", action="store_true", help="relabel every row, not only blank/TODO rows")
    parser.add_argument("--limit", type=int, default=0, help="max rows to label this session")
    args = parser.parse_args()

    path = config.GOLDEN
    if not path.exists():
        print(f"Missing {path}. Run `python -m src.eval` to generate the template first.")
        sys.exit(1)

    df = pd.read_csv(path)
    required = {"item_id", "text", "human_primary_theme", "human_return_signal", "human_note"}
    missing = required - set(df.columns)
    if missing:
        print(f"Golden CSV missing columns: {sorted(missing)}")
        sys.exit(1)

    # normalize columns to string for editing
    for col in ("human_primary_theme", "human_return_signal", "human_note"):
        df[col] = df[col].fillna("").astype(str)

    targets = []
    for idx, row in df.iterrows():
        needs_theme = _is_unlabelled(row["human_primary_theme"])
        needs_signal = _is_unlabelled(row["human_return_signal"])
        if args.all or needs_theme or needs_signal:
            targets.append(idx)

    if args.limit > 0:
        targets = targets[: args.limit]

    total_rows = len(df)
    labelled_now = int((~df["human_primary_theme"].map(_is_unlabelled)).sum())
    print("=" * 72)
    print("Golden-set manual labeling (your labels only; nothing is auto-filled)")
    print(f"File: {path}")
    print(f"Rows: {total_rows} | currently labelled: {labelled_now} | to label now: {len(targets)}")
    print("=" * 72)
    print("\nTheme legend:")
    print(_theme_legend())
    print(f"\nReturn signals: {', '.join(config.RETURN_SIGNALS)}")
    print("\nCommands while labeling: skip = leave row unchanged, quit = stop and save progress")
    print("-" * 72)

    done = 0
    skipped = 0
    try:
        for n, idx in enumerate(targets, start=1):
            row = df.loc[idx]
            item_id = str(row["item_id"])
            text = str(row["text"])
            cur_theme = row["human_primary_theme"] if not _is_unlabelled(row["human_primary_theme"]) else ""
            cur_signal = row["human_return_signal"] if not _is_unlabelled(row["human_return_signal"]) else ""
            cur_note = row["human_note"] if not _is_unlabelled(row["human_note"]) else ""

            print(f"\n[{n}/{len(targets)}] {item_id}")
            print(f"Text: {text}")
            print("Themes: " + ", ".join(_theme_codes()))

            while True:
                action = input("Label this row? [Enter=yes / skip / quit]: ").strip().lower()
                if action in {"", "y", "yes", "label"}:
                    break
                if action in {"skip", "s"}:
                    skipped += 1
                    break
                if action in {"quit", "q", "exit"}:
                    raise KeyboardInterrupt
                print("  Type Enter to label, 'skip', or 'quit'.")
            else:
                continue

            if action in {"skip", "s"}:
                continue

            theme = _prompt_theme(cur_theme)
            if theme.lower() in {"skip", "s"}:
                skipped += 1
                continue
            if theme.lower() in {"quit", "q"}:
                raise KeyboardInterrupt

            signal = _prompt_return_signal(cur_signal)
            if signal.lower() in {"skip", "s"}:
                skipped += 1
                continue
            if signal.lower() in {"quit", "q"}:
                raise KeyboardInterrupt

            note_raw = input(f"Optional note [{cur_note or 'blank'}]: ").strip()
            if note_raw.lower() in {"quit", "q"}:
                raise KeyboardInterrupt
            note = note_raw if note_raw != "" else cur_note

            df.at[idx, "human_primary_theme"] = theme
            df.at[idx, "human_return_signal"] = signal
            df.at[idx, "human_note"] = note
            _save(df, path)
            done += 1
            print(f"  Saved {item_id}: {theme} / {signal}")
    except (KeyboardInterrupt, EOFError):
        print("\nStopped. Progress saved.")

    labelled_total = int((~df["human_primary_theme"].map(_is_unlabelled)).sum())
    print("-" * 72)
    print(f"Session: labelled={done}, skipped={skipped}")
    print(f"Golden set now: {labelled_total}/{total_rows} labelled")
    print("Next: python -m src.eval && python -m scripts.qa_check")


if __name__ == "__main__":
    main()
