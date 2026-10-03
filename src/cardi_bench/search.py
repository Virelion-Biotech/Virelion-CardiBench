"""Deterministic local search over the CardiBench evidence catalog.

The implementation intentionally keeps retrieval lexical and explainable. A
search score orders one query; it is not a calibrated probability and must not
be used as a scientific quality score.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable, Mapping

from .evidence import CatalogRecord

TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)*")
DEFAULT_FIELD_WEIGHTS: dict[str, float] = {"name":6.0,"aliases":3.5,"identifiers":5.0,"sources":1.0,"metadata":0.7}


def tokenize(value: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(value)]


def _fields(record: CatalogRecord) -> dict[str, str]:
    return {"name":record.canonical_name,"aliases":" ".join(record.aliases),"identifiers":" ".join(f"{key} {value}" for key,value in record.identifiers.items()),"sources":" ".join(record.sources),"metadata":" ".join(f"{key} {value}" for key,value in record.metadata.items())}


@dataclass(frozen=True)
class SearchHit:
    record: CatalogRecord
    retrieval_score: float
    matched_tokens: tuple[str, ...]
    missing_tokens: tuple[str, ...]
    matched_fields: tuple[str, ...]
    lexical_coverage: float
    exact_name_match: bool = False
    phrase_name_match: bool = False

    def to_dict(self) -> dict:
        return {"record":self.record.to_dict(),"retrieval_score":self.retrieval_score,"matched_tokens":list(self.matched_tokens),"missing_tokens":list(self.missing_tokens),"matched_fields":list(self.matched_fields),"lexical_coverage":self.lexical_coverage,"exact_name_match":self.exact_name_match,"phrase_name_match":self.phrase_name_match}


def search_catalog(records: Iterable[CatalogRecord], query: str, *, limit: int = 20, field_weights: Mapping[str,float] | None = None) -> dict:
    records=list(records)
    if limit < 1: raise ValueError("limit must be >= 1")
    query_tokens=tuple(dict.fromkeys(tokenize(query)))
    if not query_tokens:
        return {"query":query,"search_status":"no_lexical_candidates","candidate_count":0,"total_matches":0,"full_match_count":0,"partial_match_count":0,"results":[]}
    weights=dict(DEFAULT_FIELD_WEIGHTS)
    if field_weights: weights.update({str(k):float(v) for k,v in field_weights.items()})
    docs=[]; token_df={token:0 for token in query_tokens}
    for record in records:
        raw=_fields(record); token_fields={name:tokenize(value) for name,value in raw.items()}; docs.append((record,token_fields,raw))
        present={token for values in token_fields.values() for token in values}
        for token in query_tokens:
            if token in present: token_df[token]+=1
    n_docs=max(len(docs),1)
    idf={token:math.log(1.0+(n_docs-token_df[token]+0.5)/(token_df[token]+0.5)) for token in query_tokens}
    average_lengths={field:(sum(len(tokens.get(field,())) for _,tokens,_ in docs)/len(docs) if docs else 1.0) for field in weights}
    hits=[]; k1=1.2; b=0.75; normalized_query=" ".join(query_tokens)
    for record,token_fields,raw_fields in docs:
        matched=set(); matched_fields=set(); score=0.0
        for field,weight in weights.items():
            values=token_fields.get(field,[])
            if not values or weight<=0: continue
            length_norm=1.0-b+b*(len(values)/max(average_lengths.get(field,1.0),1.0))
            for token in query_tokens:
                tf=values.count(token)
                if tf<=0: continue
                matched.add(token); matched_fields.add(field); score += weight*idf[token]*((tf*(k1+1.0))/(tf+k1*length_norm))
        if not matched: continue
        name_tokens=tokenize(raw_fields["name"]); exact_name=name_tokens==list(query_tokens); phrase_name=normalized_query in " ".join(name_tokens); query_idf=sum(idf.values()) or 1.0
        score += (2.0*query_idf if exact_name else (1.0*query_idf if phrase_name else 0.0))
        missing=tuple(token for token in query_tokens if token not in matched); coverage=sum(idf[token] for token in matched)/query_idf
        hits.append(SearchHit(record,round(score,8),tuple(token for token in query_tokens if token in matched),missing,tuple(sorted(matched_fields)),round(coverage,8),exact_name,phrase_name))
    hits.sort(key=lambda hit:(-hit.retrieval_score,-hit.lexical_coverage,hit.record.canonical_name.lower(),hit.record.record_id))
    full_count=sum(not hit.missing_tokens for hit in hits)
    status="no_lexical_candidates" if not hits else ("full_matches_found" if full_count else "partial_candidates_only")
    return {"query":query,"search_status":status,"candidate_count":len(hits),"total_matches":len(hits),"full_match_count":full_count,"partial_match_count":len(hits)-full_count,"results":[hit.to_dict() for hit in hits[:limit]]}
