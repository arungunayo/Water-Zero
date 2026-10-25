#!/usr/bin/env python3
"""
extract_hirakud.py

Extracts Hirakud (Odisha) reservoir storage data from CWC weekly reservoir storage
bulletin PDFs into CSV format, with validation, deduplication, and optional merging.
"""

import argparse
import datetime
import logging
import math
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("extract_hirakud")


# Columns for OUTPUT 1
OUTPUT_COLUMNS = [
    "bulletin_date",
    "reading_date",
    "level_m",
    "live_storage_bcm",
    "pct_live_cap_cwc",
    "frl_m",
    "live_capacity_bcm",
    "last_year_level_m",
    "last_year_storage_bcm",
    "last_year_pct",
    "normal_storage_bcm",
    "normal_pct",
    "pct_of_last_year",
    "pct_of_normal",
    "source_file",
    "layout_used",
]

# Columns for OUTPUT 2
MERGE_COLUMNS = [
    "date",
    "lat",
    "lon",
    "storage_bcm",
    "level_m",
    "storage_source",
    "stale_value",
    "pct_full",
]


def parse_date_to_iso(date_str: str) -> Optional[str]:
    """Parse date string (e.g. 16.04.2026, 16-04-2026, 16/04/2026) to ISO YYYY-MM-DD."""
    if not date_str:
        return None
    cleaned = date_str.strip()
    parts = re.split(r"[./-]", cleaned)
    if len(parts) == 3:
        p1, p2, p3 = parts
        try:
            if len(p3) == 4:  # dd.mm.yyyy
                day, month, year = int(p1), int(p2), int(p3)
                return f"{year:04d}-{month:02d}-{day:02d}"
            elif len(p1) == 4:  # yyyy.mm.dd
                year, month, day = int(p1), int(p2), int(p3)
                return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    return None


def extract_bulletin_date_from_text_or_filename(text: str, filename: str) -> Optional[str]:
    """
    Extract bulletin date using pattern 'AS ON dd.mm.yyyy' in title text,
    falling back to dd-mm-yyyy or dd.mm.yyyy in filename.
    """
    # 1. Pattern 'AS ON dd.mm.yyyy' in text (case-insensitive)
    match_text = re.search(
        r"AS\s+ON\b[^\d\n\r]*?(\d{1,2}[./-]\d{1,2}[./-]\d{4})",
        text,
        re.IGNORECASE,
    )
    if match_text:
        iso_date = parse_date_to_iso(match_text.group(1))
        if iso_date:
            return iso_date

    # 2. Fallback in filename: dd.mm.yyyy or dd-mm-yyyy
    match_file = re.search(r"(\d{1,2})[.-](\d{1,2})[.-](\d{4})", filename)
    if match_file:
        d, m, y = match_file.groups()
        try:
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        except ValueError:
            pass

    # Fallback in filename: yyyy-mm-dd or yyyy.mm.dd
    match_file_iso = re.search(r"(\d{4})[.-](\d{1,2})[.-](\d{1,2})", filename)
    if match_file_iso:
        y, m, d = match_file_iso.groups()
        try:
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        except ValueError:
            pass

    return None


def is_data_token(token: str) -> bool:
    """
    Check if a token is a data token (date, float/integer, or missing value).
    Ignores Hindi or garbled text.
    """
    # Date token: e.g. 16.04.2026, 16-04-2026, 2025-03-27
    if re.match(r"^\d{1,2}[./-]\d{1,2}[./-]\d{4}$|^\d{4}[./-]\d{1,2}[./-]\d{1,2}$", token):
        return True
    # Numeric token: e.g. 192.020, 36.83, -1.5, 153
    if re.match(r"^[+-]?\d+(?:\.\d+)?$", token):
        return True
    # Missing value token
    if token.upper() in ("N.A.", "N.A", "NA", "N/A", "-", "--"):
        return True
    return False


def to_float_or_none(val: str) -> Optional[float]:
    """Convert token to float, returning None for missing or unparseable values."""
    if not val or val.upper() in ("N.A.", "N.A", "NA", "N/A", "-", "--"):
        return None
    try:
        return float(val)
    except ValueError:
        return None


def normalize_line(line: str) -> str:
    """Normalize line by separating touching dates/numbers produced by character positioning."""
    # Separate date attached to next number (e.g. 10.09.202684.96 -> 10.09.2026 84.96)
    line = re.sub(r"(\d{1,2}[./-]\d{1,2}[./-]\d{4})([+-]?\d)", r"\1 \2", line)
    # Separate two floats touching at decimals (e.g. 191.6204.569 -> 191.620 4.569)
    line = re.sub(r"(\d+\.\d{3,5})([+-]?\d+\.\d+)", r"\1 \2", line)
    return line


def get_methods_text(pdf_path: Path):
    """
    Generator yielding (lines, full_text, method_name) in priority order:
    1. pdfplumber
    2. pymupdf
    3. pdftotext -layout
    """
    # Method 1: pdfplumber
    if pdfplumber is not None:
        try:
            lines: List[str] = []
            full_text_parts: List[str] = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt:
                        full_text_parts.append(txt)
                        for raw_l in txt.splitlines():
                            lines.append(normalize_line(raw_l))
            if any("HIRAKUD" in line.upper() for line in lines):
                yield lines, "\n".join(full_text_parts), "pdfplumber"
        except Exception as e:
            logger.debug("pdfplumber extraction failed on %s: %s", pdf_path.name, e)

    # Method 2: pymupdf
    if pymupdf is not None:
        try:
            lines = []
            full_text_parts = []
            doc = pymupdf.open(str(pdf_path))
            for page in doc:
                txt = page.get_text()
                if txt:
                    full_text_parts.append(txt)
                    for raw_l in txt.splitlines():
                        lines.append(normalize_line(raw_l))
            doc.close()
            if any("HIRAKUD" in line.upper() for line in lines):
                yield lines, "\n".join(full_text_parts), "pymupdf"
        except Exception as e:
            logger.debug("pymupdf extraction failed on %s: %s", pdf_path.name, e)

    # Method 3: pdftotext -layout
    try:
        res = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout:
            txt = res.stdout
            lines = [normalize_line(l) for l in txt.splitlines()]
            if any("HIRAKUD" in line.upper() for line in lines):
                yield lines, txt, "pdftotext"
    except Exception as e:
        logger.debug("pdftotext extraction failed on %s: %s", pdf_path.name, e)



def parse_tokens_for_layout_a(tokens: List[str]) -> Dict[str, Any]:
    """
    Parse Layout A (10 tokens):
    Tokens after name:
    0: frl_m
    1: level_m
    2: live_capacity_bcm
    3: live_storage_bcm
    4: reading_date
    5: pct_this_year (pct_live_cap_cwc)
    6: pct_last_year (last_year_pct)
    7: pct_normal (normal_pct)
    8: irr_cca_th_ha
    9: hydel_mw
    """
    return {
        "layout_used": "A",
        "frl_m": to_float_or_none(tokens[0]),
        "level_m": to_float_or_none(tokens[1]),
        "live_capacity_bcm": to_float_or_none(tokens[2]),
        "live_storage_bcm": to_float_or_none(tokens[3]),
        "reading_date": parse_date_to_iso(tokens[4]),
        "pct_live_cap_cwc": to_float_or_none(tokens[5]),
        "last_year_level_m": None,
        "last_year_storage_bcm": None,
        "last_year_pct": to_float_or_none(tokens[6]),
        "normal_storage_bcm": None,
        "normal_pct": to_float_or_none(tokens[7]),
        "pct_of_last_year": None,
        "pct_of_normal": None,
    }


def parse_tokens_for_layout_b(tokens: List[str]) -> Dict[str, Any]:
    """
    Parse Layout B (15 tokens):
    Tokens after state (Odisha):
    0: irr_cca
    1: hydel_mw
    2: frl_m
    3: live_capacity_bcm
    4: reading_date
    5: level_m
    6: live_storage_bcm
    7: pct_this_year (pct_live_cap_cwc)
    8: last_year_level_m
    9: last_year_storage_bcm
    10: last_year_pct
    11: normal_storage_bcm
    12: normal_pct
    13: pct_of_last_year
    14: pct_of_normal
    """
    return {
        "layout_used": "B",
        "frl_m": to_float_or_none(tokens[2]),
        "live_capacity_bcm": to_float_or_none(tokens[3]),
        "reading_date": parse_date_to_iso(tokens[4]),
        "level_m": to_float_or_none(tokens[5]),
        "live_storage_bcm": to_float_or_none(tokens[6]),
        "pct_live_cap_cwc": to_float_or_none(tokens[7]),
        "last_year_level_m": to_float_or_none(tokens[8]),
        "last_year_storage_bcm": to_float_or_none(tokens[9]),
        "last_year_pct": to_float_or_none(tokens[10]),
        "normal_storage_bcm": to_float_or_none(tokens[11]),
        "normal_pct": to_float_or_none(tokens[12]),
        "pct_of_last_year": to_float_or_none(tokens[13]),
        "pct_of_normal": to_float_or_none(tokens[14]),
    }


def extract_rows_from_lines(
    lines: List[str], filename: str, failed_rows_path: Path
) -> List[Dict[str, Any]]:
    """
    Extract Hirakud rows from lines of text.
    Handles line wrapping by joining subsequent lines when numeric token count is short.
    Writes unrecognized rows to failed_rows_path.
    """
    rows: List[Dict[str, Any]] = []
    i = 0
    num_lines = len(lines)

    while i < num_lines:
        line = lines[i]
        if "HIRAKUD" not in line.upper():
            i += 1
            continue

        accumulated = line.strip()
        consumed = 1
        max_lookahead = 4  # Allow up to 4 continuation lines

        layout: Optional[str] = None
        data_tokens: List[str] = []

        while True:
            # Check for Layout B: Odisha follows HIRAKUD
            match_b = re.search(
                r"\bHIRAKUD\b.*?\b(?:Odisha|Orissa)\b(.*)",
                accumulated,
                re.IGNORECASE | re.DOTALL,
            )
            if match_b:
                layout = "B"
                expected_count = 15
                after_text = match_b.group(1)
            else:
                match_a = re.search(
                    r"\bHIRAKUD\b(.*)",
                    accumulated,
                    re.IGNORECASE | re.DOTALL,
                )
                layout = "A"
                expected_count = 10
                after_text = match_a.group(1) if match_a else ""

            raw_tokens = after_text.split()
            data_tokens = [t for t in raw_tokens if is_data_token(t)]

            if len(data_tokens) == expected_count:
                break
            elif (
                len(data_tokens) < expected_count
                and (i + consumed) < num_lines
                and consumed < max_lookahead
            ):
                next_line = lines[i + consumed].strip()
                # Stop if next line clearly starts another reservoir (e.g. '2 BALIMELA' or '44 RENGALI')
                if re.match(r"^\d{1,3}\s+[A-Z]", next_line):
                    break
                accumulated += " " + next_line
                consumed += 1
            else:
                break

        # Process outcome
        if layout == "B" and len(data_tokens) == 15:
            row_dict = parse_tokens_for_layout_b(data_tokens)
            row_dict["raw_line"] = accumulated
            rows.append(row_dict)
        elif layout == "A" and len(data_tokens) == 10:
            row_dict = parse_tokens_for_layout_a(data_tokens)
            row_dict["raw_line"] = accumulated
            rows.append(row_dict)
        else:
            # Matches neither layout: write raw line to failed_rows.txt without guessing
            logger.warning(
                "Row in %s matched neither Layout A nor Layout B (%d tokens). Appending to %s.",
                filename,
                len(data_tokens),
                failed_rows_path.name,
            )
            with open(failed_rows_path, "a", encoding="utf-8") as f_fail:
                f_fail.write(f"{filename}: {accumulated}\n")

        i += consumed

    return rows


def process_single_pdf(
    pdf_path: Path, failed_rows_path: Path
) -> Tuple[Optional[Dict[str, Any]], bool]:
    """
    Process a single bulletin PDF.
    Returns (chosen_row, had_failure).
    """
    filename = pdf_path.name
    methods_tried = 0
    chosen_row = None
    bulletin_date = None

    for lines, full_text, method in get_methods_text(pdf_path):
        methods_tried += 1
        b_date = extract_bulletin_date_from_text_or_filename(full_text, filename)
        if b_date and not bulletin_date:
            bulletin_date = b_date

        extracted_rows = extract_rows_from_lines(lines, filename, failed_rows_path)
        if not extracted_rows:
            continue

        layout_b_rows = [r for r in extracted_rows if r["layout_used"] == "B"]
        layout_a_rows = [r for r in extracted_rows if r["layout_used"] == "A"]

        if layout_b_rows and layout_a_rows:
            row_b = layout_b_rows[0]
            row_a = layout_a_rows[0]
            lev_a, lev_b = row_a.get("level_m"), row_b.get("level_m")
            stg_a, stg_b = row_a.get("live_storage_bcm"), row_b.get("live_storage_bcm")
            lev_diff = abs(lev_a - lev_b) if (lev_a is not None and lev_b is not None) else 0.0
            stg_diff = abs(stg_a - stg_b) if (stg_a is not None and stg_b is not None) else 0.0

            if lev_diff > 0.01 or stg_diff > 0.005:
                logger.warning(
                    "[%s] Layout A and B disagree on level/storage: "
                    "Layout A (level=%s, storage=%s) vs Layout B (level=%s, storage=%s)",
                    filename,
                    lev_a,
                    stg_a,
                    lev_b,
                    stg_b,
                )
            chosen_row = dict(row_b)
            break
        elif layout_b_rows:
            chosen_row = dict(layout_b_rows[0])
            break
        elif layout_a_rows:
            chosen_row = dict(layout_a_rows[0])
            break

    if methods_tried == 0:
        logger.error("No Hirakud row found in PDF %s with any extraction method.", filename)
        with open(failed_rows_path, "a", encoding="utf-8") as f_fail:
            f_fail.write(f"{filename}: NO HIRAKUD TEXT FOUND\n")
        return None, True

    if chosen_row is None:
        logger.error("Failed to parse any valid Hirakud rows from %s", filename)
        return None, True

    if not bulletin_date:
        bulletin_date = extract_bulletin_date_from_text_or_filename("", filename)
    if not bulletin_date:
        logger.error("Could not determine bulletin date for %s", filename)
        with open(failed_rows_path, "a", encoding="utf-8") as f_fail:
            f_fail.write(f"{filename}: COULD NOT EXTRACT BULLETIN DATE\n")
        return None, True

    chosen_row["bulletin_date"] = bulletin_date
    chosen_row["source_file"] = filename
    return chosen_row, False



def deduplicate_and_sort_bulletins(
    rows: List[Dict[str, Any]]
) -> Tuple[pd.DataFrame, int]:
    """
    Sort by bulletin_date. Drop exact duplicates and warn if two PDFs give different values
    for the same date.
    Returns (cleaned_df, duplicate_dates_count).
    """
    if not rows:
        return pd.DataFrame(columns=OUTPUT_COLUMNS), 0

    df = pd.DataFrame(rows)
    # Ensure all output columns exist
    for col in OUTPUT_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = df[OUTPUT_COLUMNS]
    df["bulletin_date"] = df["bulletin_date"].astype(str)
    df = df.sort_values("bulletin_date").reset_index(drop=True)

    duplicate_dates_count = 0
    grouped = df.groupby("bulletin_date")
    unique_rows: List[Dict[str, Any]] = []

    for b_date, group in grouped:
        if len(group) == 1:
            unique_rows.append(group.iloc[0].to_dict())
        else:
            duplicate_dates_count += len(group) - 1
            # Check if values differ across duplicates (ignoring source_file and layout_used)
            cols_to_compare = [
                c
                for c in OUTPUT_COLUMNS
                if c not in ("source_file", "layout_used", "bulletin_date")
            ]
            first_vals = group.iloc[0][cols_to_compare].to_dict()
            has_conflict = False

            for idx in range(1, len(group)):
                other_vals = group.iloc[idx][cols_to_compare].to_dict()
                for k in cols_to_compare:
                    v1 = first_vals[k]
                    v2 = other_vals[k]
                    if pd.isna(v1) and pd.isna(v2):
                        continue
                    if v1 != v2:
                        has_conflict = True
                        break

            if has_conflict:
                files = list(group["source_file"])
                logger.warning(
                    "Conflict detected for bulletin_date %s across files %s. Preferring first entry.",
                    b_date,
                    files,
                )
            else:
                logger.info(
                    "Dropped exact duplicate(s) for bulletin_date %s across %s.",
                    b_date,
                    list(group["source_file"]),
                )

            # Prefer row with Layout B if present, else first
            b_matches = group[group["layout_used"] == "B"]
            if not b_matches.empty:
                unique_rows.append(b_matches.iloc[0].to_dict())
            else:
                unique_rows.append(group.iloc[0].to_dict())

    res_df = pd.DataFrame(unique_rows)[OUTPUT_COLUMNS]
    res_df = res_df.sort_values("bulletin_date").reset_index(drop=True)
    return res_df, duplicate_dates_count


def merge_and_extend_clean_file(
    existing_clean_path: Path,
    bulletins_df: pd.DataFrame,
    merge_out_path: Path,
) -> pd.DataFrame:
    """
    Extend existing cleaned file with bulletin rows.
    Never modify the original file.
    """
    if not existing_clean_path.exists():
        raise FileNotFoundError(f"Existing clean file not found: {existing_clean_path}")

    existing_df = pd.read_csv(existing_clean_path)
    if existing_df.empty:
        raise ValueError(f"Existing clean file {existing_clean_path} is empty")

    lat = float(existing_df["lat"].iloc[0])
    lon = float(existing_df["lon"].iloc[0])
    last_date = str(existing_df["date"].max())

    # Calculate IMPLIED_CAPACITY as median of storage_bcm / pct_full * 100
    valid_mask = (existing_df["pct_full"] > 0) & (existing_df["storage_bcm"] > 0)
    implied_caps = (existing_df.loc[valid_mask, "storage_bcm"] / existing_df.loc[valid_mask, "pct_full"]) * 100
    implied_capacity = float(implied_caps.median())
    logger.info("Implied capacity calculated from existing file: %.5f BCM", implied_capacity)

    # Sort bulletins to evaluate stale_value chronologically
    sorted_bulletins = bulletins_df.sort_values("bulletin_date").copy().reset_index(drop=True)

    new_rows: List[Dict[str, Any]] = []
    prev_level_m = None
    prev_storage_bcm = None

    for idx, row in sorted_bulletins.iterrows():
        b_date = str(row["bulletin_date"])
        r_date = str(row["reading_date"]) if pd.notna(row["reading_date"]) else b_date
        level_m = float(row["level_m"]) if pd.notna(row["level_m"]) else None
        storage_bcm = float(row["live_storage_bcm"]) if pd.notna(row["live_storage_bcm"]) else None

        # Determine stale_value: True if reading_date < bulletin_date or identical to previous bulletin's
        is_stale = False
        if r_date < b_date:
            is_stale = True
        elif prev_level_m is not None and prev_storage_bcm is not None:
            if level_m == prev_level_m and storage_bcm == prev_storage_bcm:
                is_stale = True

        prev_level_m = level_m
        prev_storage_bcm = storage_bcm

        # Append only dates strictly AFTER last date in existing file
        if b_date > last_date:
            pct_full = (
                round((storage_bcm / implied_capacity) * 100.0, 2)
                if storage_bcm is not None
                else None
            )
            new_rows.append(
                {
                    "date": b_date,
                    "lat": lat,
                    "lon": lon,
                    "storage_bcm": storage_bcm,
                    "level_m": level_m,
                    "storage_source": "cwc_bulletin",
                    "stale_value": is_stale,
                    "pct_full": pct_full,
                }
            )

    new_df = pd.DataFrame(new_rows, columns=MERGE_COLUMNS)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values("date").reset_index(drop=True)

    # Assert unique dates
    assert combined_df["date"].is_unique, "Dates in extended file must be strictly unique"

    # Save to merge_out_path
    merge_out_path.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(merge_out_path, index=False)
    logger.info(
        "Successfully wrote extended clean dataset to %s (%d rows added, %d total rows)",
        merge_out_path,
        len(new_rows),
        len(combined_df),
    )
    return combined_df


def print_validation_report(
    pdfs_processed: int,
    rows_parsed: int,
    failures: int,
    duplicate_dates: int,
    bulletins_df: pd.DataFrame,
    existing_clean_path: Optional[Path] = None,
) -> None:
    """Print the required 4-part validation report."""
    print("\n" + "=" * 65)
    print("                HIRAKUD BULLETIN VALIDATION REPORT")
    print("=" * 65)

    # 1. Counts
    print("\n1. COUNTS")
    print(f"   - PDFs processed   : {pdfs_processed}")
    print(f"   - Rows parsed      : {rows_parsed}")
    print(f"   - Failures         : {failures}")
    print(f"   - Duplicate dates  : {duplicate_dates}")

    # 2. Missing weeks (every Thursday between first and last bulletin)
    print("\n2. MISSING WEEKS (Thursdays)")
    if bulletins_df.empty or len(bulletins_df["bulletin_date"].dropna()) == 0:
        print("   - No bulletin data available to check missing weeks.")
    else:
        dates = pd.to_datetime(bulletins_df["bulletin_date"]).sort_values()
        min_date = dates.min()
        max_date = dates.max()

        # Find first Thursday on or after min_date
        # In Python weekday(): Monday=0, Thursday=3
        days_ahead = (3 - min_date.weekday() + 7) % 7
        curr_thursday = min_date + datetime.timedelta(days=days_ahead)

        missing_thursdays: List[str] = []
        parsed_dates_set = set(bulletins_df["bulletin_date"].dropna())

        while curr_thursday <= max_date:
            thurs_str = curr_thursday.strftime("%Y-%m-%d")
            if thurs_str not in parsed_dates_set:
                missing_thursdays.append(thurs_str)
            curr_thursday += datetime.timedelta(days=7)

        if missing_thursdays:
            print(f"   - First bulletin: {min_date.strftime('%Y-%m-%d')}, Last bulletin: {max_date.strftime('%Y-%m-%d')}")
            print(f"   - Missing {len(missing_thursdays)} Thursdays:")
            for m_date in missing_thursdays:
                print(f"       * {m_date}")
        else:
            print(f"   - None! All Thursdays between {min_date.strftime('%Y-%m-%d')} and {max_date.strftime('%Y-%m-%d')} are present.")

    # 3. Plausibility checks
    print("\n3. PLAUSIBILITY CHECKS")
    plausibility_flags: List[str] = []
    for _, row in bulletins_df.iterrows():
        b_date = row["bulletin_date"]
        lev = row["level_m"]
        stg = row["live_storage_bcm"]
        cap = row["live_capacity_bcm"]
        pct = row["pct_live_cap_cwc"]

        if pd.notna(lev) and (lev < 170.0 or lev > 195.0):
            plausibility_flags.append(f"{b_date}: level_m={lev} outside [170, 195]")
        if pd.notna(stg) and pd.notna(cap) and cap > 0 and (stg > cap * 1.05):
            plausibility_flags.append(f"{b_date}: live_storage_bcm={stg} > 1.05 * capacity={cap}")
        if pd.notna(pct) and (pct < 0.0 or pct > 105.0):
            plausibility_flags.append(f"{b_date}: pct_live_cap_cwc={pct} outside [0, 105]")

    if plausibility_flags:
        print(f"   - Flagged {len(plausibility_flags)} plausibility issues:")
        for flag in plausibility_flags:
            print(f"       * {flag}")
    else:
        print("   - All values passed plausibility checks (level_m in 170-195, storage <= 1.05*cap, pct in 0-105).")

    # 4. Overlap check with existing clean file
    print("\n4. OVERLAP CHECK (Dates overlapping with existing clean file: 8 May to 10 Jul 2025)")
    if existing_clean_path and existing_clean_path.exists() and not bulletins_df.empty:
        existing_df = pd.read_csv(existing_clean_path)
        existing_overlap = existing_df[(existing_df["date"] >= "2025-05-08") & (existing_df["date"] <= "2025-07-10")]
        merged = pd.merge(
            bulletins_df,
            existing_overlap,
            left_on="bulletin_date",
            right_on="date",
            suffixes=("_bulletin", "_clean"),
        )
        if not merged.empty:
            diff_level = (merged["level_m_bulletin"] - merged["level_m_clean"]).abs()
            diff_storage = (merged["live_storage_bcm"] - merged["storage_bcm"]).abs()
            max_diff_level = diff_level.max()
            max_diff_storage = diff_storage.max()
            print(f"   - Overlapping rows compared : {len(merged)}")
            print(f"   - Max absolute difference in level_m    : {max_diff_level:.4f} m")
            print(f"   - Max absolute difference in storage_bcm: {max_diff_storage:.5f} BCM")
        else:
            print("   - No overlapping dates found between bulletins and clean file (2025-05-08 to 2025-07-10).")
    else:
        print("   - Existing clean file not available or bulletin data empty; skipping overlap check.")

    print("=" * 65 + "\n")


class TestHirakudExtraction(unittest.TestCase):
    """Unit tests for Hirakud table row parsing and extraction."""

    def test_sample_lines_16_04_2026(self):
        line_a = "1 HIRAKUD 192.020 186.710 5.378 1.981 16.04.2026 36.83 37.00 40.91 153.000 307.000"
        line_b = "43 HIRAKUD Odisha 153.000 307.000 192.020 5.378 16.04.2026 186.710 1.981 36.83 186.730 1.990 37.00 2.200 40.91 99.54 90.03"

        failed_rows_path = Path("/tmp/failed_rows_test.txt")
        if failed_rows_path.exists():
            failed_rows_path.unlink()

        # Parse Layout A
        rows_a = extract_rows_from_lines([line_a], "test_a.pdf", failed_rows_path)
        self.assertEqual(len(rows_a), 1)
        r_a = rows_a[0]
        self.assertEqual(r_a["layout_used"], "A")
        self.assertAlmostEqual(r_a["level_m"], 186.71, places=2)
        self.assertAlmostEqual(r_a["live_storage_bcm"], 1.981, places=3)
        self.assertEqual(r_a["reading_date"], "2026-04-16")
        self.assertAlmostEqual(r_a["pct_live_cap_cwc"], 36.83, places=2)
        self.assertAlmostEqual(r_a["frl_m"], 192.02, places=2)
        self.assertAlmostEqual(r_a["live_capacity_bcm"], 5.378, places=3)
        self.assertAlmostEqual(r_a["last_year_pct"], 37.00, places=2)
        self.assertAlmostEqual(r_a["normal_pct"], 40.91, places=2)
        self.assertIsNone(r_a["last_year_level_m"])

        # Parse Layout B
        rows_b = extract_rows_from_lines([line_b], "test_b.pdf", failed_rows_path)
        self.assertEqual(len(rows_b), 1)
        r_b = rows_b[0]
        self.assertEqual(r_b["layout_used"], "B")
        self.assertAlmostEqual(r_b["level_m"], 186.71, places=2)
        self.assertAlmostEqual(r_b["live_storage_bcm"], 1.981, places=3)
        self.assertEqual(r_b["reading_date"], "2026-04-16")
        self.assertAlmostEqual(r_b["pct_live_cap_cwc"], 36.83, places=2)
        self.assertAlmostEqual(r_b["frl_m"], 192.02, places=2)
        self.assertAlmostEqual(r_b["live_capacity_bcm"], 5.378, places=3)
        self.assertAlmostEqual(r_b["last_year_level_m"], 186.73, places=2)
        self.assertAlmostEqual(r_b["last_year_storage_bcm"], 1.990, places=3)
        self.assertAlmostEqual(r_b["last_year_pct"], 37.00, places=2)
        self.assertAlmostEqual(r_b["normal_storage_bcm"], 2.200, places=3)
        self.assertAlmostEqual(r_b["normal_pct"], 40.91, places=2)
        self.assertAlmostEqual(r_b["pct_of_last_year"], 99.54, places=2)
        self.assertAlmostEqual(r_b["pct_of_normal"], 90.03, places=2)

        # Cleanup
        if failed_rows_path.exists():
            failed_rows_path.unlink()

    def test_wrapped_layout_b(self):
        lines = [
            "43 HIRAKUD",
            "Odisha 153.000 307.000 192.020 5.378 16.04.2026",
            "186.710 1.981 36.83 186.730 1.990 37.00 2.200 40.91 99.54 90.03",
        ]
        failed_rows_path = Path("/tmp/failed_rows_wrapped.txt")
        if failed_rows_path.exists():
            failed_rows_path.unlink()

        rows = extract_rows_from_lines(lines, "test_wrapped.pdf", failed_rows_path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["layout_used"], "B")
        self.assertAlmostEqual(rows[0]["level_m"], 186.71, places=2)
        self.assertAlmostEqual(rows[0]["pct_of_normal"], 90.03, places=2)

        if failed_rows_path.exists():
            failed_rows_path.unlink()

    def test_failed_row_logging(self):
        malformed = ["1 HIRAKUD 192.020 186.710"]  # only 2 numeric tokens
        failed_rows_path = Path("/tmp/failed_rows_test_malformed.txt")
        if failed_rows_path.exists():
            failed_rows_path.unlink()

        rows = extract_rows_from_lines(malformed, "bad.pdf", failed_rows_path)
        self.assertEqual(len(rows), 0)
        self.assertTrue(failed_rows_path.exists())
        content = failed_rows_path.read_text()
        self.assertIn("bad.pdf", content)
        self.assertIn("192.020", content)

        if failed_rows_path.exists():
            failed_rows_path.unlink()


def main():
    parser = argparse.ArgumentParser(
        description="Extract Hirakud reservoir data from CWC weekly storage bulletin PDFs."
    )
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default="data/bulletins",
        help="Path to folder containing CWC bulletin PDFs (default: data/bulletins)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="data/processed/hirakud_bulletins.csv",
        help="Path for OUTPUT 1 CSV (default: data/processed/hirakud_bulletins.csv)",
    )
    parser.add_argument(
        "--existing",
        type=str,
        default="data/processed/hirakud_clean.csv",
        help="Path to existing cleaned CSV (default: data/processed/hirakud_clean.csv)",
    )
    parser.add_argument(
        "--merge-out",
        type=str,
        default=None,
        help="Optional path for OUTPUT 2 extended CSV (never modifies existing file)",
    )
    parser.add_argument(
        "--failed-rows",
        type=str,
        default="failed_rows.txt",
        help="Path for logging unparseable/failed rows (default: failed_rows.txt)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run unit tests and exit",
    )

    args = parser.parse_args()

    if args.test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestHirakudExtraction)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

    pdf_dir = Path(args.pdf_dir)
    out_path = Path(args.out)
    existing_path = Path(args.existing) if args.existing else None
    merge_out_path = Path(args.merge_out) if args.merge_out else None
    failed_rows_path = Path(args.failed_rows)

    # Ensure output directories exist
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if merge_out_path:
        merge_out_path.parent.mkdir(parents=True, exist_ok=True)

    # Reset failed_rows_path for idempotency
    if failed_rows_path.exists():
        failed_rows_path.unlink()

    if not pdf_dir.exists():
        logger.warning("PDF directory %s does not exist.", pdf_dir)
        pdf_files: List[Path] = []
    else:
        pdf_files = sorted(
            [p for p in pdf_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
        )

    logger.info("Found %d PDF file(s) in %s", len(pdf_files), pdf_dir)

    all_rows: List[Dict[str, Any]] = []
    total_failures = 0

    for pdf_file in pdf_files:
        row, had_failure = process_single_pdf(pdf_file, failed_rows_path)
        if had_failure or row is None:
            total_failures += 1
        else:
            all_rows.append(row)

    # Deduplicate and sort
    bulletins_df, duplicate_dates_count = deduplicate_and_sort_bulletins(all_rows)

    # Save OUTPUT 1
    bulletins_df.to_csv(out_path, index=False)
    logger.info(
        "Saved %d bulletin row(s) to %s (failures: %d, duplicates: %d)",
        len(bulletins_df),
        out_path,
        total_failures,
        duplicate_dates_count,
    )

    # Process OUTPUT 2 if requested
    if merge_out_path:
        if existing_path and existing_path.exists():
            merge_and_extend_clean_file(existing_path, bulletins_df, merge_out_path)
        else:
            logger.warning(
                "Cannot perform merge-out: existing clean file %s not found.",
                existing_path,
            )

    # Print Validation Report
    print_validation_report(
        pdfs_processed=len(pdf_files),
        rows_parsed=len(all_rows),
        failures=total_failures,
        duplicate_dates=duplicate_dates_count,
        bulletins_df=bulletins_df,
        existing_clean_path=existing_path,
    )

    # Exit code: non-zero if any file failed
    if total_failures > 0:
        logger.error("Completed with %d failure(s).", total_failures)
        sys.exit(1)
    else:
        logger.info("Extraction completed successfully with 0 failures.")
        sys.exit(0)


if __name__ == "__main__":
    main()
