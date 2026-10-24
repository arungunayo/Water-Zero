"""Evidence extraction and conservative validation for WaterZero."""
from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any
from urllib.parse import urlparse


DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"),
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    re.compile(r"\b(\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})\b", re.I),
    re.compile(r"\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4})\b", re.I),
]
DATE_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%B %d %Y", "%b %d %Y")


def _first(obj: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = obj.get(key)
        if value not in (None, ""):
            return value
    return default


def _as_results(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if not isinstance(raw, dict):
        return []
    for key in ("results", "data", "items", "documents"):
        value = raw.get(key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
        if isinstance(value, dict):
            nested = _as_results(value)
            if nested:
                return nested
    # Some fetch responses use a single object with URL/text fields.
    if any(k in raw for k in ("url", "final_url", "text", "markdown", "content")):
        return [raw]
    return []


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def _is_official(url: str) -> bool:
    host = _host(url)
    return host.endswith((".gov.in", ".nic.in", ".gov", ".gov.uk", ".gov.au")) or host in {
        "imd.gov.in", "mausam.imd.gov.in", "cwc.gov.in", "jalshakti-dowr.gov.in"
    }


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, (int, float)):
        try:
            # Avoid treating year-like values as Unix timestamps.
            if value > 1_000_000_000:
                return datetime.fromtimestamp(value, tz=timezone.utc).date()
        except (ValueError, OSError, OverflowError):
            return None
    text = str(value).strip()
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        candidate = match.group(1).replace(",", "")
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(candidate, fmt).date()
            except ValueError:
                pass
        # Handle two-digit years in slash/dash dates.
        for fmt in ("%d/%m/%y", "%d-%m-%y", "%m/%d/%y"):
            try:
                return datetime.strptime(candidate, fmt).date()
            except ValueError:
                pass
    return None


def _find_date_in_text(text: str) -> date | None:
    # Prefer dates close to publication/date/issued/updated labels.
    labelled = re.search(
        r"(?:published|publication date|issued|issue date|updated|last updated|dated)\s*[:\-]?\s*"
        r"([^\n.;]{4,40})",
        text, re.I,
    )
    if labelled:
        parsed = _parse_date(labelled.group(1))
        if parsed:
            return parsed
    for pattern in DATE_PATTERNS:
        match = pattern.search(text[:12000])
        if match:
            parsed = _parse_date(match.group(1))
            if parsed:
                return parsed
    return None


def _source_kind(url: str, title: str, snippet: str) -> str:
    text = f"{url} {title} {snippet}".lower()
    if any(x in text for x in ("drought", "rainfall deficit", "rainfall departure")):
        return "drought_advisory"
    if any(x in text for x in ("forecast", "rainfall warning", "heavy rain", "catchment warning")):
        return "rainfall_or_catchment_warning"
    if any(x in text for x in ("water supply", "water-supply", "supply restriction", "rationing", "municipal")):
        return "municipal_water_restriction"
    if any(x in text for x in ("reservoir", "storage", "live storage", "cwc")):
        return "reservoir_storage_bulletin"
    return "other_official_or_web_source"


def normalize_search(raw: dict[str, Any], *, reservoir: str, state: str, query_type: str) -> list[dict[str, Any]]:
    items = _as_results(raw)
    evidence = []
    for item in items:
        url = _first(item, "url", "link", "source_url", "final_url")
        if not isinstance(url, str) or not url.startswith(("https://", "http://")):
            continue
        title = str(_first(item, "title", "name", default="Untitled source"))
        snippet = str(_first(item, "snippet", "description", "text", "content", default=""))
        published = _first(item, "published_date", "published_at", "publication_date", "date", "published")
        published_date = _parse_date(published)
        official = _is_official(url)
        evidence.append({
            "reservoir": reservoir,
            "state": state,
            "query_type": query_type,
            "title": title[:300],
            "claim": snippet[:2000],
            "source_url": url,
            "source_domain": _host(url),
            "is_official_domain": official,
            "evidence_type": _source_kind(url, title, snippet),
            "publication_date": published_date.isoformat() if published_date else None,
            "observation_period": None,
            "reported_observation": None,
            "warning_period": None,
            "location": None,
            "stance": "unknown",
            "verification_status": "search_result_not_yet_fetched",
            "staleness": "unknown",
            "conflict_group": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        })
    return evidence


def _extract_location(text: str, state: str, reservoir: str) -> str | None:
    # Conservative: report user-provided geography only if it appears in the fetched text.
    for candidate in (reservoir, state):
        if candidate and re.search(re.escape(candidate), text, re.I):
            return candidate
    match = re.search(r"\b(?:district|catchment|basin|tehsil|block)\s+(?:of\s+)?([A-Z][A-Za-z .'-]{2,60})", text)
    return match.group(0).strip() if match else None


def _extract_period(text: str, label: str) -> str | None:
    patterns = [
        rf"({label}[^\n.;]{{0,100}})",
        r"\b(?:from|between)\s+\d{1,2}\s+[A-Za-z]+\s+(?:to|and)\s+\d{1,2}\s+[A-Za-z]+\s+\d{4}\b",
        r"\bnext\s+\d{1,2}\s+days?\b",
        r"\b(?:valid|warning period)\s*(?:from|:)?[^\n.;]{0,100}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return re.sub(r"\s+", " ", match.group(1) if match.lastindex else match.group(0)).strip()[:220]
    return None


def _extract_observation(text: str) -> str | None:
    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines() if x.strip()]
    keywords = re.compile(
        r"(storage|reservoir level|live storage|rainfall|deficit|departure|drought|water supply|restriction|"
        r"release|inflow|outflow|warning|alert|shortage|mm rainfall|capacity)", re.I
    )
    candidates = [line for line in lines if keywords.search(line) and len(line) > 20]
    if not candidates:
        return None
    # Prefer lines containing quantitative observations or explicit advisories.
    candidates.sort(key=lambda s: (not bool(re.search(r"\d|deficit|drought|restriction|warning|shortage", s, re.I)), len(s)))
    return candidates[0][:500]


def enrich_fetched(evidence: list[dict[str, Any]], raw: dict[str, Any], *, state: str, reservoir: str,
                   stale_after_days: int = 90) -> list[dict[str, Any]]:
    fetched_items = _as_results(raw)
    by_url = {}
    for item in fetched_items:
        url = _first(item, "url", "final_url", "source_url", "requested_url")
        if url:
            by_url[str(url)] = item

    today = date.today()
    for ev in evidence:
        fetched = by_url.get(ev["source_url"])
        if fetched is None and len(fetched_items) == 1:
            fetched = fetched_items[0]
        if not fetched:
            ev["verification_status"] = "fetch_failed_or_missing"
            continue

        content = _first(fetched, "text", "markdown", "content", "body", "html", default="")
        if isinstance(content, (dict, list)):
            content = str(content)
        content = str(content)
        title = _first(fetched, "title")
        if title:
            ev["title"] = str(title)[:300]
        final_url = _first(fetched, "final_url", "url")
        if isinstance(final_url, str) and final_url.startswith(("https://", "http://")):
            ev["final_url"] = final_url
        ev["fetched_content_excerpt"] = content[:5000]
        ev["publication_date"] = (
            _parse_date(_first(fetched, "published_date", "publication_date", "date", "published"))
            or _parse_date(ev.get("publication_date"))
            or _find_date_in_text(content)
        )
        ev["publication_date"] = ev["publication_date"].isoformat() if ev["publication_date"] else None
        ev["location"] = _extract_location(content, state, reservoir)
        ev["reported_observation"] = _extract_observation(content)
        ev["observation_period"] = _extract_period(content, r"(?:observation period|period covered|data period)")
        ev["warning_period"] = _extract_period(content, r"(?:warning period|validity|valid till|forecast period|warning valid)")
        ev["staleness"] = "unknown"
        pub_date = _parse_date(ev["publication_date"])
        if pub_date:
            age = (today - pub_date).days
            ev["age_days"] = age
            if age < 0:
                ev["staleness"] = "future_or_date_parse_issue"
            elif age > stale_after_days:
                ev["staleness"] = "stale"
            else:
                ev["staleness"] = "current_by_configured_threshold"
        if not content.strip():
            ev["verification_status"] = "fetched_but_empty"
        elif not ev["publication_date"]:
            ev["verification_status"] = "fetched_date_not_found"
        elif not ev["location"]:
            ev["verification_status"] = "fetched_location_not_confirmed"
        else:
            ev["verification_status"] = "fetched_needs_human_claim_validation"
    return evidence


def detect_conflicts(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flag contradictory water/rainfall signals from different source claims."""
    risk_re = re.compile(r"\b(drought|deficit|below normal|below-normal|shortage|low storage|declining storage|restriction|insufficient rainfall|below average)\b", re.I)
    reassuring_re = re.compile(r"\b(normal rainfall|above normal|above-normal|surplus rainfall|adequate storage|storage increased|no restriction|no shortage)\b", re.I)
    risk_items = []
    reassuring_items = []
    for item in evidence:
        text = " ".join(str(item.get(k) or "") for k in ("claim", "reported_observation", "fetched_content_excerpt"))
        if risk_re.search(text):
            item["stance"] = "potentially_supports_risk"
            risk_items.append(item)
        if reassuring_re.search(text):
            item["stance"] = "potentially_contradicts_risk" if item["stance"] == "unknown" else "mixed_signal"
            reassuring_items.append(item)
    if risk_items and reassuring_items:
        group = "water_signal_conflict_1"
        for item in risk_items + reassuring_items:
            item["conflict_group"] = group
            item["verification_status"] = "conflicting_signals_review_required"
    return evidence
