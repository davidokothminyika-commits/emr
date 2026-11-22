import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def token():
    r = client.post('/api/auth/login', json={'username':'clinician','password':'demo123'})
    assert r.status_code == 200
    return r.json()['token']

def auth_headers():
    return {'Authorization': f"Bearer {token()}"}

def test_login():
    r = client.post('/api/auth/login', json={'username':'clinician','password':'demo123'})
    assert r.status_code == 200

def test_patients():
    r = client.get('/api/patients', headers=auth_headers())
    assert r.status_code == 200
    assert len(r.json()) >= 8

def test_patient_history():
    r = client.get('/api/patients/P-0001/history', headers=auth_headers())
    assert r.status_code == 200
    assert 'diagnoses' in r.json()

def test_labs():
    r = client.get('/api/patients/P-0001/laboratory', headers=auth_headers())
    assert r.status_code == 200
    assert len(r.json()) > 0

def test_summary():
    r = client.post('/api/patients/P-0001/generate-summary', headers=auth_headers())
    assert r.status_code == 200
    content = r.json()['content']
    # stronger: all source ids must exist in full record
    hist = client.get('/api/patients/P-0001/history', headers=auth_headers()).json()
    allids = set()
    for k in ['diagnoses','medications','allergies','labs','encounters']:
        for x in hist[k]:
            allids.add(x['id'])
    for s in content['summary']:
        for sid in s['source_ids']:
            assert sid in allids

def test_timeline():
    r = client.get('/api/patients/P-0001/timeline', headers=auth_headers())
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_alerts():
    r = client.get('/api/alerts', headers=auth_headers())
    assert r.status_code == 200

def test_encounter_draft():
    r = client.post('/api/encounters/draft', json={'patient_id':'P-0001','observations':'test'}, headers=auth_headers())
    assert r.status_code == 200
    nid = r.json()['id']
    r2 = client.post(f'/api/encounters/notes/{nid}/approve', headers=auth_headers())
    assert r2.status_code == 200
    assert r2.json()['status'] == 'approved'

def test_audit():
    r = client.get('/api/audit', headers=auth_headers())
    assert r.status_code == 200
    assert len(r.json()) > 0

def test_rules():
    r = client.get('/api/rules', headers=auth_headers())
    assert r.status_code == 200
    assert any(x['rule_id']=='VL-OVERDUE-01' for x in r.json())
