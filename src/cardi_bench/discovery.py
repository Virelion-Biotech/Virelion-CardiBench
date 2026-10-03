"""Bounded public-source discovery for candidate cardiac benchmark evidence.

Discovery is intentionally a candidate layer: a hit is not dataset admission,
benchmark readiness, biological validity, or clinical generalizability.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date,datetime,timedelta,timezone
import json,os,re
from typing import Any,Callable,Iterable,Mapping
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from .evidence import SourceObservation

SOURCE_NAMES=("pubmed","geo","bioproject","sra","crossref","zenodo","github","openalex","europepmc","clinicaltrials","biorxiv","medrxiv")
DEFAULT_SOURCE_QUERIES={
"pubmed":"(cardiac OR heart OR cardiomyocyte) AND (benchmark OR machine learning OR dataset)",
"geo":"(heart OR cardiac OR cardiomyocyte) AND (RNA-seq OR single cell OR transcriptome)",
"bioproject":"(heart OR cardiac OR cardiomyocyte) AND (RNA-seq OR transcriptome OR sequencing)",
"sra":"(heart OR cardiac OR cardiomyocyte) AND (RNA-seq OR transcriptome OR sequencing)",
"crossref":"cardiac machine learning benchmark dataset","zenodo":"cardiac benchmark dataset machine learning",
"github":"cardiac benchmark machine learning","openalex":"cardiac machine learning benchmark dataset",
"europepmc":"cardiac machine learning benchmark dataset","clinicaltrials":"cardiac OR heart",
"biorxiv":"cardiac benchmark dataset machine learning","medrxiv":"cardiac benchmark dataset machine learning"}
JsonFetcher=Callable[[str,Mapping[str,Any]|None,float],dict[str,Any]]

def _now_iso(): return datetime.now(timezone.utc).isoformat()
def _default_fetch_json(url:str,params:Mapping[str,Any]|None=None,timeout:float=30.0)->dict[str,Any]:
    if params:url += ("&" if "?" in url else "?")+urlencode({k:v for k,v in params.items() if v is not None})
    req=Request(url,headers={"User-Agent":"CardiBench/0.10 (+https://github.com/Virelion-Biotech/Virelion-CardiBench)","Accept":"application/json"})
    token=os.getenv("CARDIBENCH_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
    if "api.github.com" in url and token:req.add_header("Authorization",f"Bearer {token}")
    with urlopen(req,timeout=timeout) as resp:return json.loads(resp.read().decode("utf-8"))
def _date(v): return str(v)[:10] if v else None
def _tokens(v): return set(re.findall(r"[a-z0-9]+",str(v).lower()))
def _token_filter(text:str,query:str)->bool:
    q={t for t in _tokens(query) if len(t)>2 and t not in {"and","or","not","the","for"}}
    if not q:return True
    return bool(q & _tokens(text))
def _pubmed_doi(row:Mapping[str,Any])->str|None:
    for item in row.get("articleids") or []:
        if isinstance(item,Mapping) and str(item.get("idtype") or "").lower()=="doi":
            value=str(item.get("value") or "").strip()
            if value:return value.lower()
    return None
def _regex_identifier(text:str,pattern:str)->str|None:
    match=re.search(pattern,text,re.I)
    return match.group(0).upper() if match else None
def _xml_tag(text:str,tag:str)->str|None:
    match=re.search(fr"<{tag}[^>]*>(.*?)</{tag}>",text,re.I|re.S)
    return re.sub(r"<[^>]+>"," ",match.group(1)).strip() if match else None
def _primary_geo_pmid(row:Mapping[str,Any])->str|None:
    raw=row.get("pubmedids") or row.get("PubMedIds") or row.get("pubmed_ids")
    if isinstance(raw,(list,tuple)):
        for value in raw:
            digits="".join(ch for ch in str(value) if ch.isdigit())
            if digits:return digits
    elif raw:
        match=re.search(r"\d+",str(raw))
        if match:return match.group(0)
    return None

@dataclass(frozen=True)
class SourceRun:
    source:str; ok:bool; count:int; message:str=""
    def to_dict(self): return {"source":self.source,"ok":self.ok,"count":self.count,"message":self.message}
@dataclass(frozen=True)
class DiscoveryBatch:
    query:str|None; generated_at:str; observations:tuple[SourceObservation,...]; source_runs:tuple[SourceRun,...]
    @property
    def healthy_sources(self)->int: return sum(1 for run in self.source_runs if run.ok)
    def to_dict(self): return {"schema_version":"1.0","query":self.query,"generated_at":self.generated_at,"observations":[i.to_dict() for i in self.observations],"source_runs":[i.to_dict() for i in self.source_runs]}
    @classmethod
    def from_dict(cls,v): return cls(v.get("query"),str(v.get("generated_at") or _now_iso()),tuple(SourceObservation.from_dict(i) for i in v.get("observations",[])),tuple(SourceRun(**i) for i in v.get("source_runs",[])))

def _ncbi(db:str,query:str,limit:int,fetch:JsonFetcher):
    params={"db":db,"term":query,"retmode":"json","retmax":limit,"sort":"pub date"}
    if os.getenv("NCBI_API_KEY"):params["api_key"]=os.getenv("NCBI_API_KEY")
    ids=fetch("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",params,30).get("esearchresult",{}).get("idlist",[])
    if not ids:return []
    sparams={"db":db,"id":",".join(ids),"retmode":"json"}
    if os.getenv("NCBI_API_KEY"):sparams["api_key"]=os.getenv("NCBI_API_KEY")
    return ids,fetch("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",sparams,30).get("result",{})
def discover_pubmed(q,limit,fetch=_default_fetch_json):
    raw=_ncbi("pubmed",q,limit,fetch)
    if not raw:return []
    ids,res=raw; out=[]
    for pid in ids:
        row=res.get(str(pid),{}); title=str(row.get("title") or "").strip(); doi=_pubmed_doi(row)
        identifiers={"pmid":str(pid)}
        if doi:identifiers["doi"]=doi
        if title:out.append(SourceObservation(source="pubmed",source_record_id=str(pid),title=title,kind="publication",url=f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",published_at=_date(row.get("pubdate")),identifiers=identifiers,metadata={"journal":row.get("fulljournalname") or row.get("source")}))
    return out
def discover_geo(q,limit,fetch=_default_fetch_json):
    raw=_ncbi("gds",q,limit,fetch)
    if not raw:return []
    ids,res=raw; out=[]
    for uid in ids:
        row=res.get(str(uid),{}); acc=str(row.get("accession") or "").strip().upper(); title=str(row.get("title") or acc).strip(); pmid=_primary_geo_pmid(row)
        identifiers={"geo":acc,"accession":acc}
        if pmid:identifiers["pmid"]=pmid
        if acc and title:out.append(SourceObservation(source="geo",source_record_id=acc,title=title,kind="dataset",url=f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={acc}",published_at=_date(row.get("PDAT") or row.get("pdat")),identifiers=identifiers,metadata={"summary":row.get("summary"),"gds_type":row.get("gdstype"),"pubmed_ids":row.get("pubmedids") or row.get("PubMedIds") or row.get("pubmed_ids") or []}))
    return out
def discover_bioproject(q,limit,fetch=_default_fetch_json):
    raw=_ncbi("bioproject",q,limit,fetch)
    if not raw:return []
    ids,res=raw; out=[]
    for uid in ids:
        row=res.get(str(uid),{}); blob=json.dumps(row,ensure_ascii=False)
        acc=str(row.get("project_acc") or row.get("project_accn") or row.get("accession") or "").strip().upper() or _regex_identifier(blob,r"\bPRJ[A-Z]{2}\d+\b")
        title=str(row.get("project_title") or row.get("title") or row.get("project_name") or acc or f"BioProject {uid}").strip()
        identifiers={"bioproject":acc} if acc else {"bioproject_uid":str(uid)}
        out.append(SourceObservation(source="bioproject",source_record_id=acc or str(uid),title=title,kind="dataset",url=f"https://www.ncbi.nlm.nih.gov/bioproject/{acc or uid}",identifiers=identifiers,metadata={"uid":str(uid),"organism":row.get("organism_name") or row.get("organism")}))
    return out
def discover_sra(q,limit,fetch=_default_fetch_json):
    raw=_ncbi("sra",q,limit,fetch)
    if not raw:return []
    ids,res=raw; out=[]
    for uid in ids:
        row=res.get(str(uid),{}); blob=" ".join(str(v) for v in row.values())
        accession=str(row.get("study_acc") or row.get("accession") or "").strip().upper() or _regex_identifier(blob,r"\bSR[APRX]\d+\b")
        bioproject=_regex_identifier(blob,r"\bPRJ[A-Z]{2}\d+\b")
        title=str(row.get("title") or _xml_tag(str(row.get("expxml") or ""),"Title") or accession or f"SRA {uid}").strip()
        identifiers={}
        if accession:identifiers["sra"]=accession
        else:identifiers["sra_uid"]=str(uid)
        if bioproject:identifiers["bioproject"]=bioproject
        out.append(SourceObservation(source="sra",source_record_id=accession or str(uid),title=title,kind="dataset",url=f"https://www.ncbi.nlm.nih.gov/sra/{accession or uid}",identifiers=identifiers,metadata={"uid":str(uid)}))
    return out
def discover_europepmc(q,limit,fetch=_default_fetch_json):
    rows=fetch("https://www.ebi.ac.uk/europepmc/webservices/rest/search",{"query":q+" sort_date:y","format":"json","resultType":"core","pageSize":limit},30).get("resultList",{}).get("result",[]); out=[]
    for row in rows:
        title=str(row.get("title") or "").strip(); source_id=str(row.get("id") or row.get("pmid") or row.get("pmcid") or row.get("doi") or title).strip()
        if not title:continue
        identifiers={}
        if row.get("doi"):identifiers["doi"]=str(row["doi"])
        if row.get("pmid"):identifiers["pmid"]=str(row["pmid"])
        if row.get("pmcid"):identifiers["pmcid"]=str(row["pmcid"])
        out.append(SourceObservation(source="europepmc",source_record_id=source_id,title=title,kind="publication",url=f"https://europepmc.org/article/{row.get('source') or 'MED'}/{source_id}",published_at=_date(row.get("firstPublicationDate") or row.get("firstIndexDate") or row.get("pubYear")),identifiers=identifiers,metadata={"journal":row.get("journalTitle"),"cited_by_count":row.get("citedByCount")}))
    return out
def discover_clinicaltrials(q,limit,fetch=_default_fetch_json):
    studies=fetch("https://clinicaltrials.gov/api/v2/studies",{"query.term":q,"pageSize":limit,"format":"json"},30).get("studies",[]); out=[]
    for study in studies:
        protocol=study.get("protocolSection") or {}; ident=protocol.get("identificationModule") or {}; status=protocol.get("statusModule") or {}; conditions=protocol.get("conditionsModule") or {}; design=protocol.get("designModule") or {}
        nct=str(ident.get("nctId") or "").strip().upper(); title=str(ident.get("briefTitle") or ident.get("officialTitle") or nct).strip()
        if not nct or not title:continue
        start=(status.get("startDateStruct") or {}).get("date")
        out.append(SourceObservation(source="clinicaltrials",source_record_id=nct,title=title,kind="other",url=f"https://clinicaltrials.gov/study/{nct}",published_at=_date(start),identifiers={"nct":nct},metadata={"conditions":conditions.get("conditions") or [],"phases":design.get("phases") or [],"overall_status":status.get("overallStatus")}))
    return out
def discover_crossref(q,limit,fetch=_default_fetch_json):
    items=fetch("https://api.crossref.org/works",{"query.bibliographic":q,"rows":limit,"select":"DOI,title,URL,published,container-title,type"},30).get("message",{}).get("items",[]); out=[]
    for row in items:
        title=((row.get("title") or [""])[0]).strip(); doi=str(row.get("DOI") or "").lower()
        if title:out.append(SourceObservation(source="crossref",source_record_id=doi or str(row.get("URL") or title),title=title,kind="publication",url=row.get("URL"),identifiers={"doi":doi} if doi else {},metadata={"type":row.get("type"),"container_title":row.get("container-title")}))
    return out
def discover_zenodo(q,limit,fetch=_default_fetch_json):
    hits=fetch("https://zenodo.org/api/records",{"q":q,"size":limit,"sort":"newest"},30).get("hits",{}).get("hits",[]); out=[]
    for row in hits:
        md=row.get("metadata") or {}; title=str(md.get("title") or "").strip(); rid=str(row.get("id") or ""); doi=str(md.get("doi") or "").lower(); rtype=str((md.get("resource_type") or {}).get("type") or "")
        if title:out.append(SourceObservation(source="zenodo",source_record_id=rid,title=title,kind="dataset" if "dataset" in rtype else "other",url=(row.get("links") or {}).get("html"),published_at=_date(md.get("publication_date")),identifiers={"doi":doi} if doi else {},metadata={"resource_type":rtype,"keywords":md.get("keywords",[])}))
    return out
def discover_github(q,limit,fetch=_default_fetch_json):
    items=fetch("https://api.github.com/search/repositories",{"q":q,"per_page":limit,"sort":"updated","order":"desc"},30).get("items",[]); out=[]
    for row in items:
        name=str(row.get("full_name") or "").strip()
        if name:out.append(SourceObservation(source="github",source_record_id=name,title=name,kind="repository",url=row.get("html_url"),published_at=_date(row.get("created_at")),identifiers={"github":name.lower()},text=str(row.get("description") or ""),metadata={"description":row.get("description"),"language":row.get("language"),"stars":row.get("stargazers_count")}))
    return out
def discover_openalex(q,limit,fetch=_default_fetch_json):
    params={"search":q,"per-page":limit,"sort":"publication_date:desc"}
    if os.getenv("OPENALEX_EMAIL"):params["mailto"]=os.getenv("OPENALEX_EMAIL")
    items=fetch("https://api.openalex.org/works",params,30).get("results",[]); out=[]
    for row in items:
        title=str(row.get("display_name") or row.get("title") or "").strip(); wid=str(row.get("id") or "").rsplit("/",1)[-1]; ids=row.get("ids") or {}; doi=str(ids.get("doi") or "").removeprefix("https://doi.org/")
        if title:out.append(SourceObservation(source="openalex",source_record_id=wid or title,title=title,kind="publication",url=row.get("id"),published_at=_date(row.get("publication_date")),identifiers={"doi":doi} if doi else {},metadata={"type":row.get("type"),"cited_by_count":row.get("cited_by_count")}))
    return out
def discover_preprints(server,q,limit,lookback_days,fetch=_default_fetch_json):
    end=date.today(); start=end-timedelta(days=max(1,lookback_days)); rows=fetch(f"https://api.biorxiv.org/details/{server}/{start.isoformat()}/{end.isoformat()}/0",None,30).get("collection",[]); out=[]
    for row in rows:
        title=str(row.get("title") or "").strip(); abstract=str(row.get("abstract") or "")
        if not title or not _token_filter(title+" "+abstract,q):continue
        doi=str(row.get("doi") or "").lower(); version=str(row.get("version") or "1"); out.append(SourceObservation(source=server,source_record_id=f"{doi or title}:{version}",title=title,kind="publication",url=f"https://doi.org/{doi}" if doi else None,published_at=_date(row.get("date")),identifiers={"doi":doi} if doi else {},text=abstract,metadata={"category":row.get("category"),"version":version}))
        if len(out)>=limit:break
    return out

def run_discovery(*,query:str|None=None,sources:Iterable[str]|None=None,limit:int=25,lookback_days:int=30,fetch_json:JsonFetcher=_default_fetch_json)->DiscoveryBatch:
    if not 1<=limit<=100:raise ValueError("limit must be between 1 and 100")
    requested=tuple(dict.fromkeys(str(s).lower() for s in (sources or SOURCE_NAMES))); unknown=sorted(set(requested)-set(SOURCE_NAMES))
    if unknown:raise ValueError(f"Unknown discovery sources: {unknown}")
    observations=[]; runs=[]
    for source in requested:
        q=query or DEFAULT_SOURCE_QUERIES[source]
        try:
            if source=="pubmed":found=discover_pubmed(q,limit,fetch_json)
            elif source=="geo":found=discover_geo(q,limit,fetch_json)
            elif source=="bioproject":found=discover_bioproject(q,limit,fetch_json)
            elif source=="sra":found=discover_sra(q,limit,fetch_json)
            elif source=="europepmc":found=discover_europepmc(q,limit,fetch_json)
            elif source=="clinicaltrials":found=discover_clinicaltrials(q,limit,fetch_json)
            elif source=="crossref":found=discover_crossref(q,limit,fetch_json)
            elif source=="zenodo":found=discover_zenodo(q,limit,fetch_json)
            elif source=="github":found=discover_github(q,limit,fetch_json)
            elif source=="openalex":found=discover_openalex(q,limit,fetch_json)
            else:found=discover_preprints(source,q,limit,lookback_days,fetch_json)
            observations.extend(found); runs.append(SourceRun(source,True,len(found)))
        except Exception as exc:runs.append(SourceRun(source,False,0,f"{type(exc).__name__}: {exc}"))
    unique={i.observation_id:i for i in observations}
    return DiscoveryBatch(query,_now_iso(),tuple(sorted(unique.values(),key=lambda i:i.observation_id)),tuple(runs))
