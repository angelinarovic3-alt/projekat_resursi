import pytest
from main import app  # Izbacili smo 'db' i 'Korisnik' jer ti ne trebaju za ovaj test

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Ne menjamo URI baze jer nećemo praviti nove tabele
    with app.test_client() as client:
        yield client

def test_login_prolaz(client):
    """Provera da li login radi sa podacima koje si stavila u main.py"""
    # Ovde upiši ono korisničko ime i lozinku koje stvarno kucaš kad se loguješ
    res = client.post('/login', data={
        'korisnicko_ime': 'admin',  # PROMENI OVO NA TVOJE
        'lozinka': 'admin123'       # PROMENI OVO NA TVOJE
    }, follow_redirects=True)
    
    assert res.status_code == 200
    # Proveri da li se na stranici nakon logina pojavljuje neka od ovih reči
    assert b"Status" in res.data or b"Inventar" in res.data