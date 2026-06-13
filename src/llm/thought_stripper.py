"""
Thought Stripper - Loại bỏ <thought>...</thought> blocks từ response của thinking models.

Một số model (vd: gemma-4-26b-a4b-it, gemini-2.0-thinking) trả về response
có dạng:
    <thought>
    * Step 1: ...
    * Step 2: ...
    </thought>
    Actual answer here.

Module này strip phần thinking để user chỉ thấy phần answer thật.

Cấu hình qua:
- ENABLE_THOUGHT_STRIP: bật/tắt (default: True)
- Hoặc per-model: extra.strip_thought = True/False trong llm_config.yaml
"""

from __future__ import annotations
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# Pattern để match <thought>...</thought> hoặc <think>...</think> blocks
_THOUGHT_PATTERN = re.compile(
    r"<(?:thought|think)\b[^>]*>.*?</(?:thought|think)\s*>",
    re.DOTALL | re.IGNORECASE,
)

# Pattern cho trường hợp truncated
_THOUGHT_OPEN_PATTERN = re.compile(
    r"<(?:thought|think)\b[^>]*>.*\Z",
    re.DOTALL | re.IGNORECASE,
)


def strip_thought_blocks(
    content: str,
    enabled: bool = True,
) -> str:
    """
    Loại bỏ tất cả <thought>...</thought> blocks từ content.

    Args:
        content: Raw response từ LLM
        enabled: Nếu False, return content nguyên bản

    Returns:
        Content đã được strip thought blocks
    """
    if not enabled or not content:
        return content

    original_length = len(content)

    # 1. Strip complete <thought>...</thought> blocks
    stripped = _THOUGHT_PATTERN.sub("", content)

    # 2. Nếu còn <thought> mở mà không đóng (truncated response),
    #    strip từ <thought> đến hết
    lower_stripped = stripped.lower()
    if "<thought" in lower_stripped or "<think" in lower_stripped:
        stripped = _THOUGHT_OPEN_PATTERN.sub("", stripped)

    # 3. Cleanup: xóa leading/trailing whitespace, multiple newlines
    stripped = stripped.strip()
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)

    if len(stripped) != original_length:
        removed = original_length - len(stripped)
        logger.debug(
            f"Stripped {removed} chars of thought block "
            f"({original_length} -> {len(stripped)} chars)"
        )

    return stripped


def has_thought_block(content: str) -> bool:
    """Check xem content có thought block không."""
    if not content:
        return False
    return bool(re.search(r"<(?:thought|think)\b", content, re.IGNORECASE))


def extract_thought_and_answer(content: str) -> tuple[Optional[str], str]:
    """
    Tách riêng thought và answer từ content.

    Returns:
        (thought, answer) tuple. Nếu không có thought, trả (None, content).
    """
    if not has_thought_block(content):
        return (None, content)

    thought_match = _THOUGHT_PATTERN.search(content)
    if thought_match:
        thought = thought_match.group(0)
        # Remove thought tags để lấy phần còn lại
        answer = _THOUGHT_PATTERN.sub("", content).strip()
        # Cleanup
        answer = re.sub(r"\n{3,}", "\n\n", answer)
        return (thought, answer)

    # Thought mở nhưng không đóng - coi như không có answer riêng
    return (content, "")


# ============ Tests ============

if __name__ == "__main__":
    # Quick smoke test
    test_cases = [
        # Case 1: With complete thought block
        (
            "<thought>\n* Step 1: Analyze\n* Step 2: Compute\n</thought>\n\nCau tra loi la 42.",
            "Cau tra loi la 42.",
        ),
        # Case 2: No thought block
        (
            "Cau tra loi truc tiep khong co thought.",
            "Cau tra loi truc tiep khong co thought.",
        ),
        # Case 3: Multiple thought blocks
        (
            "<thought>Plan 1</thought>Answer 1<thought>Plan 2</thought>Answer 2",
            "Answer 1Answer 2",
        ),
        # Case 4: Truncated thought (no closing tag) - treat as incomplete
        (
            "<thought>Dang suy nghi...\n\nMot phan cau tra loi",
            "",
        ),
        # Case 5: With attributes
        (
            '<thought type="reasoning">Some thought</thought>\nKet qua cuoi.',
            "Ket qua cuoi.",
        ),
        # Case 6: Case insensitive
        (
            "<Thought>Mixed case</Thought>\nFinal answer.",
            "Final answer.",
        ),
        # Case 7: Empty
        ("", ""),
        # Case 8: Only thought
        (
            "<thought>Only thinking, no answer</thought>",
            "",
        ),
    ]

    print("Testing thought stripper:")
    all_pass = True
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = strip_thought_blocks(input_text)
        status = "[OK]" if result == expected else "[FAIL]"
        if result != expected:
            all_pass = False
        print(f"  {status} Test {i}: {repr(input_text[:60])}")
        if result != expected:
            print(f"        Expected: {repr(expected)}")
            print(f"        Got:      {repr(result)}")
        else:
            print(f"        -> {repr(result[:60])}")

    print(f"\n{'[PASS]' if all_pass else '[FAIL]'} {sum(1 for _ in test_cases)} tests")
