import json
from pathlib import Path

from cardi_bench.evidence import CatalogRecord
from cardi_bench.search import search_catalog


FIXTURE = Path(__file__).parent / "fixtures" / "search_regressions.json"


def test_search_regression_cases():
    cases=json.loads(FIXTURE.read_text(encoding="utf-8"))
    for case in cases:
        records=[CatalogRecord.from_dict(item) for item in case["records"]]
        result=search_catalog(records,case["query"])
        if "expected_record_id" in case:
            assert result["results"], case["query"]
            assert result["results"][0]["record"]["record_id"]==case["expected_record_id"]
        if "expected_status" in case:
            assert result["search_status"]==case["expected_status"]
