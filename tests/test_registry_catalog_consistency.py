import json
from pathlib import Path

from cardi_bench import BENCHMARK_FAMILIES


def test_every_benchmark_family_has_a_manifest():
    paths = {
        path.name.removesuffix(".v1.json")
        for path in Path("benchmarks/manifests").glob("*.json")
    }
    family_ids = {family.benchmark_id for family in BENCHMARK_FAMILIES}
    missing = family_ids - paths
    # Some families may use a dedicated YAML specification while still needing
    # a JSON locked-manifest implementation in future; today's release requires all.
    assert not missing, f"benchmark families missing manifests: {sorted(missing)}"


def test_json_manifests_have_unique_ids():
    ids = []
    for path in Path("benchmarks/manifests").glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        ids.append(payload["benchmark_id"])
    assert len(ids) == len(set(ids))
