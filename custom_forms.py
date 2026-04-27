from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms import PasswordField


class EditUserForm(FlaskForm):
    username = StringField("Korisničko ime", validators=[DataRequired()])
    ime_prezime = StringField("Ime i Prezime", validators=[DataRequired()])
    uloga = SelectField("Uloga", choices=[('radnik', 'Radnik'), ('admin', 'Admin'),('serviser', 'Serviser'),('direktor', 'Direktor')])
    submit = SubmitField("Sačuvaj izmene")

class AddUserForm(FlaskForm):
    username = StringField("Korisničko ime", validators=[DataRequired()])
    ime_prezime = StringField("Ime i Prezime", validators=[DataRequired()])
    password = PasswordField("Lozinka", validators=[DataRequired()])
    uloga = SelectField("Uloga", choices=[('radnik', 'Radnik'), ('admin', 'Admin'), ('serviser', 'Serviser'),('direktor', 'Direktor')])
    submit = SubmitField("Kreiraj korisnika")

class LoginForm(FlaskForm):
    username = StringField("Korisničko ime", validators=[DataRequired()])
    password = PasswordField("Lozinka", validators=[DataRequired()])
    submit = SubmitField("Prijavi se")

class ResursForm(FlaskForm):
    naziv = StringField("Naziv uređaja/resursa", validators=[DataRequired()])
    tip = SelectField("Tip", choices=[("Hardver", "Hardver"), ("Softver", "Softver"), ("Inventar", "Inventar")], validators=[DataRequired()])
    serijski_broj = StringField("Serijski broj", validators=[Optional()])
    godina_nabavke = IntegerField("Godina nabavke", validators=[DataRequired()])
    submit = SubmitField("Sačuvaj resurs")

class LokacijaForm(FlaskForm):
    naziv = StringField("Naziv lokacije (npr. Kancelarija 1)", validators=[DataRequired()])
    sprat = StringField("Sprat/Sektor", validators=[Optional()])
    odgovorno_lice = StringField("Ime i prezime odgovorne osobe", validators=[DataRequired()])
    submit = SubmitField("Sačuvaj lokaciju")


class StatusForm(FlaskForm):
    resurs_dropdown = SelectField("Odaberi resurs", choices=[], coerce=int, validators=[DataRequired()])
    lokacija_dropdown = SelectField("Odaberi lokaciju", choices=[], coerce=int, validators=[DataRequired()])

    
    korisnik_dropdown = SelectField("Zaduženo lice (Korisnik)", choices=[], coerce=int, validators=[DataRequired()])
    kolicina = IntegerField("Količina na lokaciji", default=1, validators=[DataRequired()])
    submit = SubmitField("Sačuvaj status")
    
    
    status_kvara = SelectField("Trenutni status", choices=[
        ("Ispravno", "Ispravno"), 
        ("U kvaru", "U kvaru"), 
        ("Na servisu", "Na servisu"),
        ("Potrebna zamena", "Potrebna zamena")
    ], validators=[DataRequired()])
    
    prioritet = SelectField("Prioritet rešavanja", choices=[
        ("Nizak", "Nizak"), 
        ("Normalan", "Normalan"), 
        ("Hitno", "Hitno")
    ], default="Normalan")

    opis_problema = TextAreaField("Opis problema/napomena", validators=[Optional()])
    
    submit = SubmitField("Ažuriraj status i QA prijavu")