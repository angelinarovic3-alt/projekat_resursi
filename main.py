from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_bootstrap import Bootstrap5
from alchemy_classes import Resurs, Lokacija, StatusResursa, db, init_my_database, User
from custom_forms import ResursForm, LokacijaForm, StatusForm, LoginForm
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
import io
from openpyxl import Workbook

app = Flask(__name__)
app.secret_key = "firma_gis_bezbednost_123"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///QAInventory.db"
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'zephyr'

# Inicijalizacija
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
bootstrap = Bootstrap5(app)
db.init_app(app)
init_my_database(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# --- HOME ---
@app.route('/')
@login_required 
def home():
    svi_resursi = db.session.execute(db.select(Resurs)).scalars().all()
    upit_stanja = db.select(StatusResursa).join(Resurs).join(Lokacija).order_by(
        StatusResursa.status_kvara.desc(), 
        StatusResursa.prioritet.asc()
    )
    sva_stanja = db.session.execute(upit_stanja).scalars().all()
    return render_template("index.html", stanja=sva_stanja, resursi=svi_resursi, naslov="Glavni Dashboard")

@app.route('/admin_panel')
@login_required
def admin_panel():
    # STRIKTNA PROVERA: Samo korisnik sa ulogom 'admin' prolazi dalje
    if current_user.uloga != 'admin':
        flash("Greška: Nemate administrativna ovlašćenja za pristup korisnicima!", "danger")
        return redirect(url_for('home'))
    
    # Izvlačimo sve korisnike iz baze
    svi_korisnici = User.query.all()
    
    # KLJUČNO: Šaljemo ih pod oba imena da bi tvoj HTML (koji god da koristiš) radio
    return render_template("admin.html", korisnici=svi_korisnici, users=svi_korisnici)

# --- INVENTAR I LOKACIJE (Tvoja originalna Administracija) ---
@app.route("/administracija", methods=["GET", "POST"]) 
@login_required
def admin_page():
    all_resources = db.session.execute(db.select(Resurs)).scalars().all()
    all_locations = db.session.execute(db.select(Lokacija)).scalars().all()
    return render_template("administracija.html", resursi=all_resources, lokacije=all_locations)

# --- RAD SA STATUSIMA ---
@app.route("/dodaj_status", methods=['GET', 'POST'])
@login_required
def add_status():
    add_form = StatusForm()
    resursi = Resurs.query.all()
    lokacije = Lokacija.query.all()
    add_form.resurs_dropdown.choices = [(r.id, f"{r.naziv} ({r.tip})") for r in resursi]
    add_form.lokacija_dropdown.choices = [(l.id, l.naziv) for l in lokacije]
    
    if add_form.validate_on_submit():
        new_status = StatusResursa(
            resurs_id=add_form.resurs_dropdown.data,
            lokacija_id=add_form.lokacija_dropdown.data,
            kolicina=add_form.kolicina.data,
            status_kvara=add_form.status_kvara.data,
            prioritet=add_form.prioritet.data,
            opis_problema=add_form.opis_problema.data
        )
        db.session.add(new_status)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_ad.html", form=add_form, title="Prijavi novo stanje")

@app.route("/delete_status/<int:status_id>")
@login_required
def delete_status(status_id):
    zapis = db.get_or_404(StatusResursa, status_id)
    db.session.delete(zapis)
    db.session.commit()
    return redirect(url_for('home'))

# --- EXCEL EXPORT (Novo!) ---
@app.route("/export_excel")
@login_required
def export_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Izvestaj"
    ws.append(["Resurs", "Lokacija", "Status", "Prioritet", "Opis"])
    for s in StatusResursa.query.all():
        ws.append([s.resurs.naziv, s.lokacija.naziv, s.status_kvara, s.prioritet, s.opis_problema or "/"])
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return send_file(buffer, download_name="IT_Izvestaj.xlsx", as_attachment=True)

# --- OSTALE RUTE (Resursi, Lokacije, Login) ---
@app.route("/dodaj_resurs", methods=['GET', 'POST'])
@login_required
def add_resource():
    form = ResursForm()
    if form.validate_on_submit():
        db.session.add(Resurs(naziv=form.naziv.data, tip=form.tip.data, serijski_broj=form.serijski_broj.data, godina_nabavke=form.godina_nabavke.data))
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template("add_ad.html", form=form, title="Dodaj novi resurs")

@app.route("/delete_resource")
@login_required
def delete_resource():
    res_id = request.args.get('id')
    res = db.get_or_404(Resurs, res_id)
    db.session.delete(res)
    db.session.commit()
    return redirect(url_for('admin_page'))

@app.route("/dodaj_lokaciju", methods=['GET', 'POST'])
@login_required
def add_location():
    form = LokacijaForm()
    if form.validate_on_submit():
        db.session.add(Lokacija(naziv=form.naziv.data, sprat=form.sprat.data, odgovorno_lice=form.odgovorno_lice.data))
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template("add_ad.html", form=form, title="Dodaj novu lokaciju")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.username == form.username.data)).scalar()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash("Pogrešno ime ili lozinka", "danger")
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- IZMENA KORISNIKA ---
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.uloga != 'admin':
        return redirect(url_for('home'))
        
    korisnik = db.get_or_404(User, user_id)
    # Koristimo AddUserForm ali bez obavezne lozinke ako se ne menja
    form = User(obj=korisnik) 
    
    if form.validate_on_submit():
        korisnik.username = form.username.data
        korisnik.ime_prezime = form.ime_prezime.data
        korisnik.uloga = form.uloga.data
        if form.password.data: # Ako je uneta nova lozinka, hešuj je
            korisnik.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        db.session.commit()
        flash(f"Korisnik {korisnik.username} uspešno ažuriran.", "success")
        return redirect(url_for('admin_panel'))
        
    return render_template("add_ad.html", form=form, title="Izmeni korisnika")

# --- BRISANJE KORISNIKA ---
@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.uloga != 'admin' or current_user.id == user_id:
        flash("Ne možete obrisati sebe ili nemate prava!", "danger")
        return redirect(url_for('admin_panel'))
        
    korisnik = db.get_or_404(User, user_id)
    db.session.delete(korisnik)
    db.session.commit()
    flash("Korisnik obrisan.", "info")
    return redirect(url_for('admin_panel'))

# --- DODAVANJE KORISNIKA (da se slaže sa tvojim dugmetom) ---
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.uloga != 'admin':
        return redirect(url_for('home'))
    from custom_forms import AddUserForm # Proveri da li se ovako zove u custom_forms.py
    form = AddUserForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        novi = User(username=form.username.data, password=hashed_pw, 
                    ime_prezime=form.ime_prezime.data, uloga=form.uloga.data)
        db.session.add(novi)
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template("add_ad.html", form=form, title="Dodaj novog zaposlenog")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not db.session.execute(db.select(User).where(User.username == "admin")).scalar():
            db.session.add(User(username="admin", password=generate_password_hash("admin123", method='pbkdf2:sha256'), uloga="admin", ime_prezime="Administrator"))
            db.session.commit()
    app.run(debug=True)