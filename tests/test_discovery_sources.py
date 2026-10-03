from cardi_bench.discovery import (
    discover_bioproject,
    discover_clinicaltrials,
    discover_crossref,
    discover_europepmc,
    discover_geo,
    discover_github,
    discover_openalex,
    discover_preprints,
    discover_pubmed,
    discover_sra,
    discover_zenodo,
    run_discovery,
)


def test_pubmed_fixture():
    def fetch(url, params, timeout):
        if "esearch.fcgi" in url:
            return {"esearchresult": {"idlist": ["123"]}}
        return {"result": {"123": {"title": "Cardiac ML benchmark", "pubdate": "2026 Jan", "fulljournalname": "Heart AI", "articleids": [{"idtype": "doi", "value": "10.1000/PUBMED"}]}}}
    rows=discover_pubmed("cardiac benchmark",5,fetch)
    assert rows[0].identifiers["pmid"]=="123"
    assert rows[0].identifiers["doi"]=="10.1000/pubmed"
    assert rows[0].kind=="publication"


def test_geo_fixture():
    def fetch(url, params, timeout):
        if "esearch.fcgi" in url:
            return {"esearchresult": {"idlist": ["1"]}}
        return {"result": {"1": {"accession": "GSE123", "title": "Cardiac single-cell atlas", "pdat": "2026-01-01", "pubmedids": ["456"]}}}
    rows=discover_geo("cardiac single cell",5,fetch)
    assert rows[0].identifiers["geo"]=="GSE123"
    assert rows[0].identifiers["pmid"]=="456"
    assert rows[0].kind=="dataset"


def test_crossref_fixture():
    def fetch(url, params, timeout):
        return {"message":{"items":[{"DOI":"10.1000/test","title":["Cardiac benchmark"],"URL":"https://doi.org/10.1000/test","type":"journal-article"}]}}
    rows=discover_crossref("cardiac benchmark",5,fetch)
    assert rows[0].identifiers["doi"]=="10.1000/test"


def test_zenodo_fixture():
    def fetch(url, params, timeout):
        return {"hits":{"hits":[{"id":7,"metadata":{"title":"Cardiac benchmark data","doi":"10.5281/zenodo.7","publication_date":"2026-01-02","resource_type":{"type":"dataset"}},"links":{"html":"https://zenodo.org/records/7"}}]}}
    rows=discover_zenodo("cardiac benchmark",5,fetch)
    assert rows[0].kind=="dataset"
    assert rows[0].identifiers["doi"]=="10.5281/zenodo.7"


def test_github_fixture():
    def fetch(url, params, timeout):
        return {"items":[{"full_name":"org/cardiac-benchmark","html_url":"https://github.com/org/cardiac-benchmark","created_at":"2026-01-01T00:00:00Z","description":"cardiac benchmark","language":"Python","stargazers_count":3}]}
    rows=discover_github("cardiac benchmark",5,fetch)
    assert rows[0].identifiers["github"]=="org/cardiac-benchmark"
    assert rows[0].kind=="repository"


def test_openalex_fixture():
    def fetch(url, params, timeout):
        return {"results":[{"id":"https://openalex.org/W1","display_name":"Cardiac benchmark study","publication_date":"2026-01-01","ids":{"doi":"https://doi.org/10.1000/openalex"},"type":"article","cited_by_count":2}]}
    rows=discover_openalex("cardiac benchmark",5,fetch)
    assert rows[0].identifiers["doi"]=="10.1000/openalex"


def test_preprint_fixture_for_biorxiv_and_medrxiv():
    def fetch(url, params, timeout):
        return {"collection":[{"title":"Cardiac machine learning benchmark","abstract":"A cardiac benchmark dataset.","doi":"10.1101/2026.01.01.1","version":"1","date":"2026-01-01","category":"bioinformatics"}]}
    bio=discover_preprints("biorxiv","cardiac benchmark",5,30,fetch)
    med=discover_preprints("medrxiv","cardiac benchmark",5,30,fetch)
    assert bio[0].source=="biorxiv"
    assert med[0].source=="medrxiv"


def test_discovery_failure_is_isolated_per_source():
    def fetch(url, params, timeout):
        if "api.crossref.org" in url:
            return {"message":{"items":[{"DOI":"10.1000/test","title":["Cardiac benchmark"],"URL":"https://doi.org/10.1000/test","type":"journal-article"}]}}
        raise RuntimeError("source unavailable")
    batch=run_discovery(sources=["crossref","github"],limit=5,fetch_json=fetch)
    assert batch.healthy_sources==1
    assert [run.ok for run in batch.source_runs]==[True,False]
    assert batch.observations


def test_bioproject_fixture():
    def fetch(url, params, timeout):
        if "esearch.fcgi" in url:return {"esearchresult":{"idlist":["9"]}}
        return {"result":{"9":{"project_acc":"PRJNA123","project_title":"Cardiac RNA-seq project","organism_name":"Mus musculus"}}}
    rows=discover_bioproject("cardiac RNA-seq",5,fetch)
    assert rows[0].identifiers["bioproject"]=="PRJNA123"


def test_sra_fixture():
    def fetch(url, params, timeout):
        if "esearch.fcgi" in url:return {"esearchresult":{"idlist":["10"]}}
        return {"result":{"10":{"study_acc":"SRP123","title":"Cardiac SRA study","extra":"PRJNA123"}}}
    rows=discover_sra("cardiac RNA-seq",5,fetch)
    assert rows[0].identifiers["sra"]=="SRP123"
    assert rows[0].identifiers["bioproject"]=="PRJNA123"


def test_europepmc_fixture():
    def fetch(url, params, timeout):
        return {"resultList":{"result":[{"id":"123","source":"MED","title":"Cardiac benchmark study","pmid":"123","pmcid":"PMC123","doi":"10.1000/EPMC","firstPublicationDate":"2026-01-01"}]}}
    rows=discover_europepmc("cardiac benchmark",5,fetch)
    assert rows[0].identifiers["doi"]=="10.1000/epmc"
    assert rows[0].identifiers["pmid"]=="123"
    assert rows[0].identifiers["pmcid"]=="PMC123"


def test_clinicaltrials_fixture():
    def fetch(url, params, timeout):
        return {"studies":[{"protocolSection":{"identificationModule":{"nctId":"NCT12345678","briefTitle":"Cardiac trial"},"statusModule":{"overallStatus":"RECRUITING","startDateStruct":{"date":"2026-01"}},"conditionsModule":{"conditions":["Heart Failure"]},"designModule":{"phases":["PHASE2"]}}}]}
    rows=discover_clinicaltrials("cardiac",5,fetch)
    assert rows[0].identifiers["nct"]=="NCT12345678"
    assert rows[0].metadata["overall_status"]=="RECRUITING"


def test_ncbi_fetcher_contract_keeps_source_failures_isolated():
    # The network fetcher owns retry/rate-limit behavior; run_discovery must still
    # preserve per-source health rather than fail the whole batch.
    calls=[]
    def fetch(url,params,timeout):
        calls.append((url,dict(params or {})))
        if params and params.get("db")=="geo":raise RuntimeError("rate limited")
        if "esearch.fcgi" in url:return {"esearchresult":{"idlist":[]}}
        return {}
    batch=run_discovery(sources=["geo","bioproject"],limit=1,fetch_json=fetch)
    assert [run.ok for run in batch.source_runs]==[False,True]
