#!/usr/bin/env python3
"""Generate one reproducible CardiEval software-reference result.

This is a software integration/calibration fixture only. It is intentionally
synthetic and must never be presented as biological, preclinical, or clinical
model performance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from cardieval import (
    BenchmarkManifest,
    BenchmarkTask,
    PredictionRecord,
    canonical_json_hash,
    evaluate_submission,
)
from cardi_bench import CardiBenchAPI


LABELS = {
    "ref-001": 0, "ref-002": 1, "ref-003": 1, "ref-004": 0,
    "ref-005": 0, "ref-006": 1, "ref-007": 0, "ref-008": 1,
    "ref-009": 1, "ref-010": 0, "ref-011": 1, "ref-012": 0,
    "ref-013": 0, "ref-014": 1, "ref-015": 1, "ref-016": 0,
    "ref-017": 1, "ref-018": 0, "ref-019": 0, "ref-020": 1,
}


def _canonical_sha(value: object) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _score(sample_id: str) -> float:
    # Label-independent deterministic pseudo-score used only to exercise the
    # complete evaluator path.
    raw=int(hashlib.sha256(("cardibench-reference:"+sample_id).encode()).hexdigest()[:8],16)
    return raw / 0xFFFFFFFF


def generate(result_store: Path, report_path: Path) -> dict:
    sample_ids=list(LABELS)
    fixture={
        "benchmark_id":"cardibench-software-reference",
        "version":"1.0.0",
        "sample_ids":sample_ids,
        "authoritative_labels":LABELS,
        "validation_class":"software_reference",
    }
    manifest=BenchmarkManifest(
        benchmark_id=fixture["benchmark_id"],
        version=fixture["version"],
        task="binary_classification",
        split="test",
        sample_ids=sample_ids,
        dataset_sha256=_canonical_sha(fixture),
        label_schema={"0":"reference","1":"target"},
        metadata={
            "validation_class":"software_reference",
            "scientific_use":"prohibited",
            "purpose":"exercise CardiBench-CardiEval result provenance",
        },
        authoritative_labels=LABELS,
    )
    task=BenchmarkTask(
        benchmark_id=manifest.benchmark_id,
        version=manifest.version,
        task_id="cardibench-software-reference-v1",
        task_type="binary_classification",
        allowed_metrics=[
            "accuracy","balanced_accuracy","macro_f1","auroc","auprc",
            "brier","ece","sensitivity","specificity",
        ],
        primary_metric="balanced_accuracy",
        primary_direction="higher_is_better",
        splits=["test"],
        requires_authoritative_labels=True,
        description="Synthetic software-reference task; not a scientific benchmark.",
    )
    predictions=[]
    for sample_id in sample_ids:
        score=_score(sample_id)
        predictions.append(PredictionRecord(sample_id=sample_id,y_pred=int(score>=0.5),score=score))
    report=evaluate_submission(
        manifest,
        predictions,
        model_id="hash-prior-software-baseline",
        subgroup_min_n=10,
        task_contract=task,
    )
    if report.ground_truth_source!="benchmark_manifest":
        raise RuntimeError("reference result must use evaluator-controlled labels")
    report_json=report.model_dump(mode="json")
    fingerprint=canonical_json_hash(report_json)
    artifact={
        "schema_version":"1.0",
        "validation_class":"software_reference",
        "scientific_use":"prohibited",
        "statement":"Synthetic software integration fixture; not biological, preclinical, or clinical performance.",
        "model_definition":"SHA-256(sample_id) deterministic score; labels are never used to generate predictions.",
        "evaluation_fingerprint":fingerprint,
        "report":report_json,
    }
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(artifact,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")

    payload={
        "benchmark_id":report.benchmark_id,
        "benchmark_version":report.benchmark_version,
        "benchmark_sha256":report.benchmark_sha256,
        "model_id":report.model_id,
        "model_version":"1.0.0",
        "split":report.split,
        "metrics":[metric.model_dump(mode="json") for metric in report.metrics],
        "sample_count":len(sample_ids),
        "task_id":task.task_id,
        "evaluator_version":report.evaluator_version,
        "artifact_uri":"repo://data/intelligence/reference-evaluation.json",
        "notes":"SOFTWARE REFERENCE ONLY — synthetic labels and label-independent baseline; not biological or clinical performance.",
    }
    result=CardiBenchAPI().record_result({**payload,"result_store":str(result_store)})
    return {
        "evaluation_fingerprint":fingerprint,
        "evaluator_version":report.evaluator_version,
        "ground_truth_source":report.ground_truth_source,
        "result":result,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--result-store",type=Path,default=Path("data/intelligence/results.json"))
    parser.add_argument("--report",type=Path,default=Path("data/intelligence/reference-evaluation.json"))
    args=parser.parse_args()
    print(json.dumps(generate(args.result_store,args.report),indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
