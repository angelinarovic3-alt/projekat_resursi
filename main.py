from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from alchemy_classes import Resurs, Lokacija, StatusResursa, db, init_my_database, User
from custom_forms import ResursForm, LokacijaForm, StatusForm, LoginForm
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from custom_forms import AddUserForm, EditUserForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)
app.secret_key = "firma_gis_bezbednost_123"
bootstrap = Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///QAInventory.db"
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'zephyr'
app.config['SECRET_KEY'] = 'tvoja_tajna_sifra_123'

db.init_app(app)
init_my_database(app)

@app.route('/')
@login_required 
def home():

    svi_resursi = db.session.execute(db.select(Resurs)).scalars().all()
    
    upit_stanja = db.select(StatusResursa).join(Resurs).join(Lokacija).order_by(
        StatusResursa.status_kvara.desc(), 
        StatusResursa.prioritet.asc()
    )
    result = db.session.execute(upit_stanja)
    sva_stanja = result.scalars().all()
    
    return render_template("index.html", 
                           stanja=sva_stanja, 
                           resursi=svi_resursi,
                           naslov="Glavni Dashboard")


@app.route('/napravi_admina')
def create_admin():
    postoji = db.session.execute(db.select(User).where(User.username == "admin")).scalar()
    if not postoji:
        hashed_pw = generate_password_hash("admin123", method='pbkdf2:sha256', salt_length=8)
        new_user = User(username="admin", password=hashed_pw, ime_prezime="Glavni Admin", uloga="admin")
        db.session.add(new_user)
        db.session.commit()
        return "Admin kreiran! Korisničko ime: admin, Lozinka: admin123"
    return "Admin već postoji."


@app.route('/admin_panel')
@login_required
def admin_panel():
    if current_user.uloga != 'admin':
        flash("Nemate ovlašćenja za ovu stranicu!", "danger")
        return redirect(url_for('home'))
    
    svi_korisnici = User.query.all()
    return render_template("admin.html", korisnici=svi_korisnici)

@app.route("/administracija", methods=["GET", "POST"]) 
def admin_page():
    all_resources = db.session.execute(db.select(Resurs)).scalars().all()
    all_locations = db.session.execute(db.select(Lokacija)).scalars().all()
    return render_template("administracija.html", resursi=all_resources, lokacije=all_locations)



@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.uloga != 'admin':
        flash("Samo admini mogu dodavati korisnike!", "danger")
        return redirect(url_for('home'))
        
    form = AddUserForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        novi_korisnik = User(
            username=form.username.data,
            password=hashed_pw,
            ime_prezime=form.ime_prezime.data,
            uloga=form.uloga.data
        )
        db.session.add(novi_korisnik)
        db.session.commit()
        flash(f"Korisnik {form.username.data} je uspešno kreiran!", "success")
        return redirect(url_for('admin_panel'))
        
    return render_template("add_user.html", form=form)



@app.route("/dodaj_status", methods=['GET', 'POST'])
def add_status():
    add_form = StatusForm()
    all_resources = db.session.execute(db.select(Resurs)).scalars().all()
    all_locations = db.session.execute(db.select(Lokacija)).scalars().all()
    all_locations = db.session.execute(db.select(Lokacija)).scalars().all()
    add_form.lokacija_dropdown.choices = [(l.id, l.naziv) for l in all_locations]
    
    resursi_iz_baze = db.session.execute(db.select(Resurs)).scalars().all()
    lokacije_iz_baze = db.session.execute(db.select(Lokacija)).scalars().all()
    add_form.resurs_dropdown.choices = [(r.id, f"{r.naziv} ({r.tip})") for r in all_resources]
    add_form.lokacija_dropdown.choices = [(l.id, l.naziv) for l in all_locations]
    
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

@app.route("/dodaj_resurs", methods=['GET', 'POST'])
def add_resource():
    form = ResursForm()
    if form.validate_on_submit():
        new_res = Resurs(
            naziv=form.naziv.data,
            tip=form.tip.data,
            serijski_broj=form.serijski_broj.data,
            godina_nabavke=form.godina_nabavke.data
        )
        db.session.add(new_res)
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template("add_ad.html", form=form, title="Dodaj novi resurs")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data 
        password = form.password.data

        user = db.session.execute(db.select(User).where(User.username == username)).scalar()
        

        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash(f"Dobrodošli nazad, {user.ime_prezime}!", "success")
                return redirect(url_for('home'))
            else:
                print("DEBUG: Lozinka se ne poklapa.")
                flash("Pogrešno korisničko ime ili lozinka.", "danger")
        else:
            print(f"DEBUG: Korisnik {username} ne postoji.")
            flash("Pogrešno korisničko ime ili lozinka.", "danger")
            
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Uspešno ste se odjavili sa sistema.", "info")
    return redirect(url_for('login'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.uloga != 'admin':
        return redirect(url_for('home'))

    user_to_edit = db.session.get(User, user_id)
    
    form = EditUserForm(obj=user_to_edit)
    
    if form.validate_on_submit():
        user_to_edit.username = form.username.data
        user_to_edit.ime_prezime = form.ime_prezime.data
        user_to_edit.uloga = form.uloga.data
        db.session.commit()
        flash("Podaci uspešno ažurirani!", "success")
        return redirect(url_for('admin_panel')) 
        
    return render_template("edit_user.html", form=form, user=user_to_edit)


@app.route("/dodaj_lokaciju", methods=['GET', 'POST'])
def add_location():
    form = LokacijaForm()
    if form.validate_on_submit():
        new_loc = Lokacija(
            naziv=form.naziv.data,
            sprat=form.sprat.data,
            odgovorno_lice=form.odgovorno_lice.data
        )
        db.session.add(new_loc)
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template("add_ad.html", form=form, title="Dodaj novu lokaciju")

@app.route("/edit_status", methods=['GET', 'POST'])
def edit_status():
    status_id = request.args.get('id')
    status_entry = db.get_or_404(StatusResursa, status_id)
    
    all_resources = db.session.execute(db.select(Resurs)).scalars().all()
    all_locations = db.session.execute(db.select(Lokacija)).scalars().all()
    
    edit_form = StatusForm()
    edit_form.resurs_dropdown.choices = [(r.id, r.naziv) for r in all_resources]
    edit_form.lokacija_dropdown.choices = [(l.id, l.naziv) for l in all_locations]

    if edit_form.validate_on_submit():
        status_entry.resurs_id = edit_form.resurs_dropdown.data
        status_entry.lokacija_id = edit_form.lokacija_dropdown.data
        status_entry.kolicina = edit_form.kolicina.data
        status_entry.status_kvara = edit_form.status_kvara.data
        status_entry.prioritet = edit_form.prioritet.data
        status_entry.opis_problema = edit_form.opis_problema.data
        db.session.commit()
        return redirect(url_for('home'))

    edit_form.resurs_dropdown.data = status_entry.resurs_id
    edit_form.lokacija_dropdown.data = status_entry.lokacija_id
    edit_form.kolicina.data = status_entry.kolicina
    edit_form.status_kvara.data = status_entry.status_kvara
    edit_form.prioritet.data = status_entry.prioritet 
    edit_form.opis_problema.data = status_entry.opis_problema
    
    return render_template("edit_ad.html", form=edit_form, title="Izmeni status/kvar")

@app.route("/delete_resource")
def delete_resource():
    res_id = request.args.get('id')
    res = db.get_or_404(Resurs, res_id)
    db.session.delete(res)
    db.session.commit()
    return redirect(url_for('admin_page'))


@app.route('/setup')
def setup():
    postoji = db.session.execute(db.select(User).where(User.username == "admin")).scalar()
    if not postoji:
        hashed_pw = generate_password_hash("admin123", method='pbkdf2:sha256')
        novi_admin = User(
            username="admin", 
            password=hashed_pw, 
            ime_prezime="Glavni Admin", 
            uloga="admin"
        )
        db.session.add(novi_admin)
        db.session.commit()
        return "USPEH: Admin (admin/admin123) je upisan u bazu! Sad idi na /login."
    return "Admin već postoji u bazi."



if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        
        admin_provera = db.session.execute(db.select(User).where(User.username == "admin")).scalar()
        
        if not admin_provera:
            print("Sistem: Admin ne postoji, kreiram ga...")
            hashed_pw = generate_password_hash("admin123", method='pbkdf2:sha256')
            novi_admin = User(
                username="admin", 
                password=hashed_pw, 
                uloga="admin", 
                ime_prezime="Marko Jovanović"
            )
            db.session.add(novi_admin)
            db.session.commit()
            print("Sistem: Admin (admin/admin123) uspešno dodat u bazu!")
        else:
            print("Sistem: Admin je već prisutan u bazi.")

    app.run(debug=True)