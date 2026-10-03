from cardi_bench import BenchmarkResultObservation,CardiBenchAPI,CatalogRecord,SourceObservation,append_result,load_result_history,resolve_observations,run_discovery,search_catalog

def test_identity_is_conservative_across_types():
    a=SourceObservation(source='geo',source_record_id='GSE1',title='Atlas',kind='dataset',identifiers={'doi':'10.1/x'})
    b=SourceObservation(source='zenodo',source_record_id='1',title='Atlas data',kind='dataset',identifiers={'doi':'10.1/x'})
    p=SourceObservation(source='pubmed',source_record_id='2',title='Atlas paper',kind='publication',identifiers={'doi':'10.1/x'})
    c=resolve_observations([a,b,p]); assert len(c.records)==2; assert len(c.links)==1

def test_search_explains_partial_candidates():
    rows=[CatalogRecord(record_id='a',canonical_name='Myocardial infarction single-cell benchmark',record_type='benchmark'),CatalogRecord(record_id='b',canonical_name='Cardiac mechanics dataset',record_type='dataset')]
    assert search_catalog(rows,'myocardial infarction benchmark')['full_match_count']==1
    assert search_catalog(rows,'cardiac mechanics benchmark')['partial_match_count']>=1

def test_result_history_idempotent(tmp_path):
    r=BenchmarkResultObservation('b','1','m','1','test',{'auroc':.8},20,'a'*64,protocol_id='task')
    path=tmp_path/'results.json'; assert append_result(path,r); assert not append_result(path,r); assert len(load_result_history(path))==1

def test_discovery_crossref_fixture():
    def fetch(url,params,timeout): return {'message':{'items':[{'DOI':'10.1000/test','title':['Cardiac benchmark dataset'],'URL':'https://doi.org/10.1000/test','type':'journal-article'}]}}
    batch=run_discovery(sources=['crossref'],limit=3,fetch_json=fetch); assert batch.healthy_sources==1; assert batch.observations[0].identifiers['doi']=='10.1000/test'

def test_hearttwin_api_surfaces():
    api=CardiBenchAPI(); search=api.invoke('benchmark.search',{'query':'cardiac benchmark','records':[{'record_id':'x','canonical_name':'Cardiac benchmark','record_type':'benchmark','aliases':[],'identifiers':{},'observation_ids':[],'sources':['manual'],'evidence_state':'verified','metadata':{}}]}); assert search['full_match_count']==1
    out=api.invoke('benchmark.result.record',{'benchmark_id':'b','benchmark_version':'1','benchmark_sha256':'b'*64,'model_id':'m','model_version':'1','split':'test','metrics':[{'name':'auroc','value':.9,'n':10}],'sample_count':10,'task_id':'task'}); assert out['result']['metrics']=={'auroc':.9}


def test_identity_resolution_is_transitive_within_artifact_kind():
    a=SourceObservation(source="geo",source_record_id="GSE1",title="A",kind="dataset",identifiers={"geo":"GSE1"})
    b=SourceObservation(source="zenodo",source_record_id="1",title="B",kind="dataset",identifiers={"geo":"GSE1","doi":"10.1000/x"})
    c=SourceObservation(source="other",source_record_id="2",title="C",kind="dataset",identifiers={"doi":"10.1000/x"})
    resolved=resolve_observations([a,b,c])
    assert len(resolved.records)==1
    assert resolved.records[0].metadata["observation_count"]==3

def test_result_comparability_includes_evaluator_source():
    base=dict(benchmark_id="b",benchmark_version="1",model_id="m",model_version="1",split="test",metrics={"auroc":0.8},sample_count=10,benchmark_provenance_sha256="c"*64,protocol_id="task")
    a=BenchmarkResultObservation(source="CardiEval/0.4",**base)
    b=BenchmarkResultObservation(source="CardiEval/0.5",**base)
    assert a.comparability_key!=b.comparability_key


def test_admission_bridge_payload_is_transport_shaped():
    from cardi_bench import assess_admission, bridge_admission_payload
    rows=[
        {"sample_id":"s1","group_id":"g1","study_id":"st","label":"reference"},
        {"sample_id":"s2","group_id":"g2","study_id":"st","label":"myocardial_injury"},
        {"sample_id":"s3","group_id":"g3","study_id":"st","label":"reference"},
        {"sample_id":"s4","group_id":"g4","study_id":"st","label":"myocardial_injury"},
        {"sample_id":"s5","group_id":"g5","study_id":"st","label":"reference"},
        {"sample_id":"s6","group_id":"g6","study_id":"st","label":"myocardial_injury"},
    ]
    report=assess_admission(rows,benchmark_id="candidate",test_values=["g1","g2"],validation_values=["g3","g4"])
    payload=bridge_admission_payload(report,benchmark_id="candidate",benchmark_version="1.0",trace={"source":"CardiBench"})
    assert payload["status"]=="ready_for_review"
    assert payload["ready_for_review"] is True
    assert payload["trace"]["source"]=="CardiBench"
