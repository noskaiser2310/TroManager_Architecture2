"""
Robust JSON parser cho LLM responses.

LLM thường trả về JSON không hoàn hảo:
- Wrapped trong markdown fencing (```json ... ```)
- Có text trước/sau JSON
- Truncated (max_tokens quá thấp)
- Single quotes thay vì double quotes
- Có BOM, whitespace thừa

Module này cung cấp `parse_llm_json()` với nhiều fallback strategies.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


# Patterns
# Match opening fence at start of input: ```json or ``` (with optional newline)
_OPENING_FENCE = re.compile(r"^\s*```(?:json|JSON)?\s*\n?", re.IGNORECASE)
# Match closing fence at end of input: ``` (with optional leading newline)
_CLOSING_FENCE = re.compile(r"\n?\s*```\s*$", re.IGNORECASE)
# Match any fence in the middle (for cleanup of stray fences)
_MIDDLE_FENCE = re.compile(r"```(?:json|JSON)?\s*\n?", re.IGNORECASE)
_BOM = "\ufeff"
_INSIGHT_LINE_PATTERN = re.compile(r"^\s*[-*•\d.]+\s*[\)\.]?\s*(.+?)\s*$", re.MULTILINE)


def _clean_text(text: str) -> str:
    """Remove BOM, strip whitespace, unwrap markdown fencing."""
    # Strip BOM
    text = text.lstrip(_BOM)
    # Strip whitespace
    text = text.strip()
    # Unwrap opening fence at start
    text = _OPENING_FENCE.sub("", text, count=1)
    # Strip again in case fence removal left whitespace
    text = text.strip()
    # Unwrap closing fence at end
    text = _CLOSING_FENCE.sub("", text)
    return text.strip()


def _find_json_object(text: str) -> Optional[str]:
    """
    Tìm JSON object đầu tiên trong text bằng brace matching.
    Returns substring, hoặc None nếu không tìm thấy.
    """
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text[start:], start=start):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def _extract_insights_from_text(text: str, max_items: int = 10) -> list[str]:
    """
    Fallback: extract insights từ plain text bằng cách tìm các dòng
    bắt đầu bằng `-`, `*`, `•`, hoặc số thứ tự.
    """
    candidates = _INSIGHT_LINE_PATTERN.findall(text)
    insights = []
    for c in candidates:
        # Strip trailing period/quote
        c = c.strip().rstrip(".'\"").strip()
        if c and 5 <= len(c) <= 500:  # Reasonable insight length cho text fallback
            insights.append(c)
        if len(insights) >= max_items:
            break
    return insights


def _normalize_insight(raw: Any, *, min_length: int = 1) -> Optional[str]:
    """
    Normalize 1 insight thành clean string, hoặc None nếu invalid.
    Accept str, dict (lấy field 'text'/'insight'/'memory' đầu tiên), hoặc list joined.

    Args:
        raw: Raw insight từ JSON.
        min_length: Độ dài tối thiểu (mặc định 1).
            Text fallback dùng min_length=5 để filter noise.
    """
    if isinstance(raw, str):
        s = raw.strip()
    elif isinstance(raw, dict):
        # Thử các field phổ biến
        for key in ("text", "insight", "memory", "content", "description"):
            if key in raw and isinstance(raw[key], str):
                s = raw[key].strip()
                break
        else:
            return None
    elif isinstance(raw, list):
        s = " ".join(str(x) for x in raw if x)
    else:
        return None

    # Validate
    if not s or len(s) < min_length:
        return None
    if len(s) > 500:
        s = s[:497] + "..."
    return s


def parse_llm_json(
    text: str,
    expected_key: str = "insights",
    *,
    fallback_to_text: bool = True,
    max_items: int = 10,
) -> dict:
    """
    Parse LLM response thành dict, robust với malformed JSON.

    Strategies (theo thứ tự):
    1. Clean text (strip BOM, unwrap fencing) → json.loads
    2. Find JSON object substring → json.loads
    3. Try fixing common issues (single quotes → double quotes)
    4. Fallback: extract insights từ plain text (nếu fallback_to_text=True)

    Args:
        text: Raw LLM response text.
        expected_key: Key mong đợi trong JSON (vd "insights").
        fallback_to_text: Nếu True, khi JSON parsing fail, thử extract
            insights từ text thuần.
        max_items: Số insights tối đa trả về.

    Returns:
        Dict dạng {expected_key: [str, ...], "_parse_status": "ok|fallback|empty"}

    Raises:
        ValueError: Nếu không parse được và fallback_to_text=False.
    """
    if not text or not text.strip():
        return {expected_key: [], "_parse_status": "empty"}

    original = text
    cleaned = _clean_text(text)

    # Strategy 1: direct parse
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            insights = [_normalize_insight(x) for x in data.get(expected_key, [])]
            insights = [i for i in insights if i]
            return {
                expected_key: insights[:max_items],
                "_parse_status": "ok" if insights else "empty",
            }
    except json.JSONDecodeError:
        pass

    # Strategy 2: find JSON substring
    json_sub = _find_json_object(cleaned)
    if json_sub:
        try:
            data = json.loads(json_sub)
            if isinstance(data, dict):
                insights = [_normalize_insight(x) for x in data.get(expected_key, [])]
                insights = [i for i in insights if i]
                return {
                    expected_key: insights[:max_items],
                    "_parse_status": "ok" if insights else "empty",
                }
        except json.JSONDecodeError:
            pass

    # Strategy 3: try fixing common issues (single quotes, trailing comma)
    if json_sub:
        fixed = json_sub
        # Single quotes → double quotes (cẩn thận với apostrophe trong text)
        # Chỉ làm nếu không có double quotes
        if '"' not in fixed and "'" in fixed:
            fixed = fixed.replace("'", '"')
        # Trailing commas
        fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
        try:
            data = json.loads(fixed)
            if isinstance(data, dict):
                insights = [_normalize_insight(x) for x in data.get(expected_key, [])]
                insights = [i for i in insights if i]
                return {
                    expected_key: insights[:max_items],
                    "_parse_status": "ok" if insights else "empty",
                }
        except json.JSONDecodeError:
            pass

    # Strategy 4: fallback to text extraction
    if fallback_to_text:
        insights = _extract_insights_from_text(cleaned, max_items=max_items)
        if insights:
            logger.debug(
                f"parse_llm_json: JSON parse failed, extracted {len(insights)} "
                f"insights from text fallback"
            )
            return {expected_key: insights, "_parse_status": "fallback"}

    # All strategies failed
    logger.warning(
        f"parse_llm_json: failed to parse, returning empty. "
        f"Text preview: {original[:200]!r}"
    )
    if not fallback_to_text:
        raise ValueError(
            f"Failed to parse LLM JSON and fallback_to_text=False. "
            f"Text preview: {original[:200]!r}"
        )
    return {expected_key: [], "_parse_status": "empty"}
