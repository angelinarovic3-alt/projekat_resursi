import pytest
import sys
import os
from main import app 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Ne menjamo URI baze jer nećemo praviti nove tabele
    with app.test_client() as client:
        yield client

def test_login_prolaz(client):
    """Provera da li login radi sa podacima koje si stavila u main.py"""
    res = client.post('/login', data={
        'korisnicko_ime': 'admin',  
        'lozinka': 'admin123'       
    }, follow_redirects=True)
    
    assert res.status_code == 200
    # Proveri da li se na stranici nakon logina pojavljuje neka od ovih reči
    assert b"Status" in res.data or b"Inventar" in res.data