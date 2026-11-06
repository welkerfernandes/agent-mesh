import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import create_app
from app.models import Models
from app.orchestrator import Budget,verify_references
from app.contracts import Report

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(str(tmp_path/'test.db'))) as c:
        c.headers['X-API-Key']='local-alpha';yield c

def mission(**changes):return {'objective':'Compare operational context for a reference business',**changes}

def test_full_demo_with_typescript_critic(client):
    response=client.post('/api/runs',json=mission())
    assert response.status_code==200,response.text
    result=response.json()
    assert result['status']=='completed' and len(result['evidence'])==3
    assert result['structural_review']['engine']=='typescript'
    assert result['budget']['used']=={'tool':3,'model':3}
    assert all(e['provenance']['mode']=='demo' for e in result['evidence'])
    assert [e['sequence'] for e in result['events']]==list(range(1,len(result['events'])+1))

def test_isolation(client):
    client.post('/api/runs',json=mission())
    assert len(client.get('/api/history').json())==1
    client.headers['X-API-Key']='local-beta'
    assert client.get('/api/history').json()==[]

def test_budget_exhaustion_has_no_snapshot(client):
    response=client.post('/api/runs',json=mission(max_tool_calls=1))
    assert response.status_code==422
    assert client.get('/api/history').json()==[]

def test_model_budget(client):
    assert client.post('/api/runs',json=mission(max_model_calls=1)).status_code==422

def test_budget_thread_safety():
    from concurrent.futures import ThreadPoolExecutor
    budget=Budget(1,1)
    def reserve(_):
        try: budget.reserve('tool');return True
        except HTTPException:return False
    with ThreadPoolExecutor(max_workers=8) as p:assert sum(p.map(reserve,range(20)))==1

def test_invented_citations():
    report=Report(summary='x',claims=[{'text':'x','evidence_ids':['invented']}],limitations=['x'])
    with pytest.raises(HTTPException):verify_references(report,[{'id':'real'}])

def test_model_output_is_schema_validated():
    import httpx
    from app.contracts import Plan
    model=Models(httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'message':{'content':'{"tasks":[{"id":"x","tool":"shell","question":"execute"}]}'}}))))
    with pytest.raises(HTTPException):model.ask('planner',{},Plan,'ollama')
    model.close()

def test_tool_injection_is_rejected():
    from app.contracts import Plan
    from pydantic import ValidationError
    with pytest.raises(ValidationError):Plan(tasks=[{'id':'x','tool':'shell','question':'run arbitrary code'}])

def test_auth(client):
    client.headers['X-API-Key']='bad'
    assert client.post('/api/runs',json=mission()).status_code==401
