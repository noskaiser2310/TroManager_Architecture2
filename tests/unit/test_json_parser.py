"""Tests cho parse_llm_json."""
import pytest

from src.core.json_parser import parse_llm_json


class TestParseLLMJson:
    """Test các scenarios parse LLM response."""

    def test_clean_json(self):
        """JSON thuần, không có wrapper."""
        text = '{"insights": ["insight 1", "insight 2"]}'
        result = parse_llm_json(text)
        assert result["insights"] == ["insight 1", "insight 2"]
        assert result["_parse_status"] == "ok"

    def test_markdown_fenced_json(self):
        """JSON wrapped trong ```json ... ```."""
        text = '```json\n{"insights": ["a", "b"]}\n```'
        result = parse_llm_json(text)
        assert result["insights"] == ["a", "b"]
        assert result["_parse_status"] == "ok"

    def test_markdown_fenced_no_lang(self):
        """JSON wrapped trong ``` ... ``` (không có json)."""
        text = '```\n{"insights": ["x"]}\n```'
        result = parse_llm_json(text)
        assert result["insights"] == ["x"]
        assert result["_parse_status"] == "ok"

    def test_bom_prefix(self):
        """JSON có BOM character ở đầu."""
        text = '\ufeff{"insights": ["bom insight"]}'
        result = parse_llm_json(text)
        assert result["insights"] == ["bom insight"]
        assert result["_parse_status"] == "ok"

    def test_text_around_json(self):
        """JSON có text thừa trước/sau."""
        text = 'Đây là kết quả:\n{"insights": ["good"]}\nCảm ơn!'
        result = parse_llm_json(text)
        assert result["insights"] == ["good"]
        assert result["_parse_status"] == "ok"

    def test_nested_json(self):
        """JSON với nested arrays trong insights."""
        text = '{"insights": [["a", "b"], "c"]}'
        result = parse_llm_json(text)
        # List joined: ["a b", "c"]
        assert "a b" in result["insights"]
        assert "c" in result["insights"]

    def test_dict_insight_with_text_field(self):
        """Insights là dicts với field 'text'."""
        text = '{"insights": [{"text": "dict insight 1"}, {"text": "dict insight 2"}]}'
        result = parse_llm_json(text)
        assert result["insights"] == ["dict insight 1", "dict insight 2"]

    def test_dict_insight_with_memory_field(self):
        """Insights là dicts với field 'memory'."""
        text = '{"insights": [{"memory": "memory insight"}]}'
        result = parse_llm_json(text)
        assert result["insights"] == ["memory insight"]

    def test_empty_insights(self):
        """JSON hợp lệ nhưng insights rỗng."""
        text = '{"insights": []}'
        result = parse_llm_json(text)
        assert result["insights"] == []
        assert result["_parse_status"] == "empty"

    def test_missing_insights_key(self):
        """JSON không có key 'insights'."""
        text = '{"other_key": ["a", "b"]}'
        result = parse_llm_json(text)
        assert result["insights"] == []
        assert result["_parse_status"] == "empty"

    def test_truncated_json(self):
        """JSON bị truncate (thiếu closing brace)."""
        text = '{"insights": ["a", "b"'
        result = parse_llm_json(text, fallback_to_text=True)
        # Không parse được JSON, nhưng fallback có thể cũng không extract được
        # vì text chỉ có JSON, không có bullet points
        assert result["_parse_status"] in ("empty", "fallback")

    def test_fallback_to_bullet_list(self):
        """JSON broken, fallback extract từ bullet list."""
        text = "Đây là phân tích:\n- Thường thanh toán trễ 3-5 ngày\n- Hay hỏi về phòng trống\n- Thích nhận Zalo"
        result = parse_llm_json(text, fallback_to_text=True)
        assert result["_parse_status"] == "fallback"
        assert len(result["insights"]) == 3
        assert "Thường thanh toán trễ 3-5 ngày" in result["insights"]

    def test_fallback_to_numbered_list(self):
        """JSON broken, fallback từ numbered list (1. 2. 3.)."""
        text = "1. Thường xuyên hỏi giá phòng\n2. Ít gọi điện\n3. Thích chat Zalo"
        result = parse_llm_json(text, fallback_to_text=True)
        assert result["_parse_status"] == "fallback"
        assert len(result["insights"]) >= 1

    def test_fallback_to_star_list(self):
        """JSON broken, fallback từ star bullets."""
        text = "* Insight A\n* Insight B\n* Insight C"
        result = parse_llm_json(text, fallback_to_text=True)
        assert result["_parse_status"] == "fallback"
        assert "Insight A" in result["insights"]
        assert "Insight B" in result["insights"]

    def test_fallback_disabled_raises(self):
        """Khi fallback_to_text=False và JSON fail, raise ValueError."""
        text = "not json at all"
        with pytest.raises(ValueError, match="Failed to parse LLM JSON"):
            parse_llm_json(text, fallback_to_text=False)

    def test_fallback_disabled_empty_insights(self):
        """JSON hợp lệ nhưng rỗng → không raise, trả empty."""
        text = '{"insights": []}'
        result = parse_llm_json(text, fallback_to_text=False)
        assert result["insights"] == []

    def test_max_items_limit(self):
        """max_items giới hạn số insights trả về."""
        text = '{"insights": ["a", "b", "c", "d", "e"]}'
        result = parse_llm_json(text, max_items=2)
        assert result["insights"] == ["a", "b"]

    def test_empty_string(self):
        """Empty string → empty result, không raise."""
        result = parse_llm_json("")
        assert result["insights"] == []
        assert result["_parse_status"] == "empty"

    def test_whitespace_only(self):
        """Whitespace only → empty result."""
        result = parse_llm_json("   \n\t  ")
        assert result["insights"] == []

    def test_normalize_truncates_long_insights(self):
        """Insights quá dài (>500 chars) bị truncate."""
        long_text = "x" * 1000
        text = f'{{"insights": ["{long_text}"]}}'
        result = parse_llm_json(text)
        assert len(result["insights"][0]) <= 500
        assert result["insights"][0].endswith("...")

    def test_normalize_drops_too_short(self):
        """JSON insights: chỉ drop empty string (min_length=1)."""
        text = '{"insights": ["ab", "good insight", ""]}'
        result = parse_llm_json(text)
        # Empty bị drop, "ab" và "good insight" đều giữ
        assert "ab" in result["insights"]
        assert "good insight" in result["insights"]
        assert "" not in result["insights"]

    def test_single_quote_fix(self):
        """JSON với single quotes (Python-style) được fix."""
        text = "{'insights': ['insight 1', 'insight 2']}"
        result = parse_llm_json(text)
        assert "insight 1" in result["insights"]
        assert "insight 2" in result["insights"]

    def test_trailing_comma_fix(self):
        """JSON với trailing comma được fix."""
        text = '{"insights": ["a", "b", ],}'
        result = parse_llm_json(text)
        assert "a" in result["insights"]
        assert "b" in result["insights"]

    def test_realistic_llm_response(self):
        """Mô phỏng response thực tế từ LLM."""
        text = '''```json
{
  "insights": [
    "Khách thường thanh toán trễ 2-3 ngày so với hạn",
    "Ưa chuộng liên lạc qua Zalo hơn gọi điện",
    "Có xu hướng hỏi thông tin phòng trống vào cuối tháng",
    "Đánh giá tích cực về tốc độ phản hồi của quản lý"
  ]
}
```'''
        result = parse_llm_json(text)
        assert result["_parse_status"] == "ok"
        assert len(result["insights"]) == 4
        assert "Khách thường thanh toán trễ" in result["insights"][0]

    def test_custom_expected_key(self):
        """Đổi expected_key."""
        text = '{"memories": ["mem 1", "mem 2"]}'
        result = parse_llm_json(text, expected_key="memories")
        assert result["memories"] == ["mem 1", "mem 2"]
