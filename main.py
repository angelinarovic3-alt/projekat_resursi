from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_bootstrap import Bootstrap5
from alchemy_classes import Resurs, Lokacija, StatusResursa, db, init_my_database, User
from custom_forms import ResursForm, LokacijaForm, StatusForm, LoginForm, AddUserForm
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
import io
from openpyxl import Workbook
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = "firma_gis_bezbednost_123"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///QAInventory.db"
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'lux'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
bootstrap = Bootstrap5(app)
db.init_app(app)
init_my_database(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/')
@login_required 
def home():
    svi_resursi = Resurs.query.all()
    aktivni_kvarovi = StatusResursa.query.filter(StatusResursa.status_kvara != 'Ispravno').all()

    search_query = request.args.get('search', '')

    upit_stanja = db.select(StatusResursa).join(Resurs).join(Lokacija)

    if search_query:
        upit_stanja = upit_stanja.where(
            (Resurs.naziv.ilike(f'%{search_query}%')) | 
            (StatusResursa.status_kvara.ilike(f'%{search_query}%')) |
            (Lokacija.naziv.ilike(f'%{search_query}%'))
        )
    
    upit_stanja = upit_stanja.order_by(
        StatusResursa.status_kvara.desc(), 
        StatusResursa.prioritet.asc()
    )
    
    sva_stanja = db.session.execute(upit_stanja).scalars().all()
    

    return render_template("index.html", 
                           stanja=sva_stanja, 
                           resursi=svi_resursi, 
                           statusi=aktivni_kvarovi,
                           naslov="Glavni Dashboard")

@app.route('/admin_panel')
@login_required
def admin_panel():
    
    if current_user.uloga != 'admin':
        flash("Greška: Nemate administrativna ovlašćenja za pristup korisnicima!", "danger")
        return redirect(url_for('home'))
    
    svi_korisnici = User.query.all()
    

    return render_template("admin.html", korisnici=svi_korisnici, users=svi_korisnici)


@app.route("/administracija", methods=["GET", "POST"]) 
@login_required
def admin_page():
    all_resources = db.session.execute(db.select(Resurs)).scalars().all()
    all_locations = db.session.execute(db.select(Lokacija)).scalars().all()
    return render_template("administracija.html", resursi=all_resources, lokacije=all_locations)


@app.route("/dodaj_status", methods=['GET', 'POST'])
@login_required
def add_status():
    add_form = StatusForm()
    
    korisnici_iz_baze = User.query.all()
    resursi_iz_baze = Resurs.query.all()
    lokacije_iz_baze = Lokacija.query.all()

    add_form.korisnik_dropdown.choices = [(k.id, k.ime_prezime) for k in korisnici_iz_baze]
    add_form.resurs_dropdown.choices = [(r.id, f"{r.naziv} ({r.tip})") for r in resursi_iz_baze]
    add_form.lokacija_dropdown.choices = [(l.id, l.naziv) for l in lokacije_iz_baze]
    
    if add_form.validate_on_submit():
        
        new_status = StatusResursa(
            resurs_id=add_form.resurs_dropdown.data,
            lokacija_id=add_form.lokacija_dropdown.data,
            korisnik_id=add_form.korisnik_dropdown.data, 
            kolicina=add_form.kolicina.data,
            status_kvara=add_form.status_kvara.data,
            prioritet=add_form.prioritet.data,
            opis_problema=add_form.opis_problema.data
        )
        db.session.add(new_status)
        db.session.commit()
        flash("Status uspešno dodat!", "success") 
        return redirect(url_for('home'))
    
    return render_template("add_ad.html", form=add_form, title="Prijavi novo stanje")
@app.route("/delete_status/<int:status_id>")
@login_required
def delete_status(status_id):
    zapis = db.get_or_404(StatusResursa, status_id)
    db.session.delete(zapis) 
    db.session.commit()
    return redirect(url_for('home'))


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


@app.route("/dodaj_resurs", methods=['GET', 'POST'])
@login_required
def add_resource():
    form = ResursForm()
    
    if form.validate_on_submit():
        db.session.add(Resurs(naziv=form.naziv.data, tip=form.tip.data, serijski_broj=form.serijski_broj.data, godina_nabavke=form.godina_nabavke.data))
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template("add_ad.html", form=form, title="Dodaj novi resurs")

@app.route('/izmeni-stanje/<int:stanje_id>', methods=['GET', 'POST'])
@login_required
def izmeni_stanje(stanje_id):

    stanje = StatusResursa.query.get_or_404(stanje_id)
    
    
    svi_resursi = Resurs.query.all()
    sve_lokacije = Lokacija.query.all()
    svi_korisnici = User.query.all()

    if request.method == 'POST':
        
        stanje.resurs_id = request.form.get('resurs_id')
        stanje.lokacija_id = request.form.get('lokacija_id')
        stanje.user_id = request.form.get('user_id')
        stanje.status_kvara = request.form.get('status_kvara')
        stanje.prioritet = request.form.get('prioritet')
        stanje.opis_stanja = request.form.get('opis_stanja')

        
        db.session.commit()
        return redirect(url_for('home'))


    return render_template('izmeni_stanje.html', 
                           stanje=stanje, 
                           resursi=svi_resursi, 
                           lokacije=sve_lokacije, 
                           korisnici=svi_korisnici)



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
    lok_id = request.args.get('id')
    if lok_id:

        lokacija = db.get_or_404(Lokacija, lok_id)
        form = LokacijaForm(obj=lokacija)
    else:

        lokacija = None
        form = LokacijaForm()

    if form.validate_on_submit():
        if lokacija:
            
            lokacija.naziv = form.naziv.data
            lokacija.sprat = form.sprat.data
            lokacija.odgovorno_lice = form.odgovorno_lice.data
        else:
    
            nova_lokacija = Lokacija(
                naziv=form.naziv.data, 
                sprat=form.sprat.data, 
                odgovorno_lice=form.odgovorno_lice.data
            )

            db.session.add(nova_lokacija)
            
        db.session.commit()
        return redirect(url_for('admin_page'))
        
    return render_template("add_ad.html", form=form, title="Upravljanje lokacijom")
    
@app.route("/delete_location")
@login_required
def delete_location():

    lok_id = request.args.get('id')
    
    lokacija = db.get_or_404(Lokacija, lok_id)
    
    db.session.delete(lokacija)
    db.session.commit()
    
    return redirect(url_for('admin_page'))


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


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    korisnik = db.get_or_404(User, user_id)
    
    form = AddUserForm(obj=korisnik) 
    
    if form.validate_on_submit():
        korisnik.username = form.username.data
        korisnik.ime_prezime = form.ime_prezime.data
        korisnik.uloga = form.uloga.data
        
        if form.password.data:
            korisnik.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            
        db.session.commit()
        return redirect(url_for('admin_panel'))
        
    return render_template("add_ad.html", form=form, title="Izmeni korisnika")

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


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.uloga != 'admin':
        return redirect(url_for('home'))
    from custom_forms import AddUserForm #
    form = AddUserForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        novi = User(username=form.username.data, password=hashed_pw, 
                    ime_prezime=form.ime_prezime.data, uloga=form.uloga.data)
        db.session.add(novi)
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template("add_ad.html", form=form, title="Dodaj novog zaposlenog")


def izracunaj_rizik_resursa(resurs_id):
    broj_kvarova = db.session.query(StatusResursa).filter_by(resurs_id=resurs_id).count()
    
    if broj_kvarova > 5:
        return "KRITIČNO"
    elif broj_kvarova > 2:
        return "PROBLEM"
    return "STABILNO"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not db.session.execute(db.select(User).where(User.username == "admin")).scalar():
            db.session.add(User(username="admin", password=generate_password_hash("admin123", method='pbkdf2:sha256'), uloga="admin", ime_prezime="Administrator"))
            db.session.commit()
    app.run(debug=True)