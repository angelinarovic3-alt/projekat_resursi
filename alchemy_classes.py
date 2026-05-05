from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime
from datetime import datetime
from flask_login import UserMixin

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    ime_prezime: Mapped[str] = mapped_column(String(100), nullable=True)
    uloga: Mapped[str] = mapped_column(String(10), default="user")

    
    zaduzeni_statusi: Mapped[list["StatusResursa"]] = relationship("StatusResursa", back_populates="korisnik")


class Resurs(db.Model):
    __tablename__ = "resurs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    naziv: Mapped[str] = mapped_column(String(100), nullable=False)
    tip: Mapped[str] = mapped_column(String(50))
    serijski_broj: Mapped[str] = mapped_column(String(100), unique=True)
    godina_nabavke: Mapped[int] = mapped_column(Integer)


    statusi: Mapped[list["StatusResursa"]] = relationship("StatusResursa", back_populates="resurs")

class Lokacija(db.Model):
    __tablename__ = "lokacija"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    naziv: Mapped[str] = mapped_column(String(100), nullable=False)
    sprat: Mapped[str] = mapped_column(String(50), nullable=True) 
    odgovorno_lice: Mapped[str] = mapped_column(String(100))


    izvestaji: Mapped[list["StatusResursa"]] = relationship("StatusResursa", back_populates="lokacija")


class StatusResursa(db.Model):
    __tablename__ = "status_resursa"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    resurs_id: Mapped[int] = mapped_column(ForeignKey("resurs.id"), nullable=False)
    lokacija_id: Mapped[int] = mapped_column(ForeignKey("lokacija.id"), nullable=False)
    korisnik_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False) # VEZA SA KORISNIKOM!
    
    kolicina: Mapped[int] = mapped_column(Integer, default=1)
    status_kvara: Mapped[str] = mapped_column(String(50)) 
    prioritet: Mapped[str] = mapped_column(String(20))    
    opis_problema: Mapped[str] = mapped_column(String(50), nullable=True)
    datum_prijave: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resurs: Mapped["Resurs"] = relationship("Resurs", back_populates="statusi")
    lokacija: Mapped["Lokacija"] = relationship("Lokacija", back_populates="izvestaji")
    korisnik: Mapped["User"] = relationship("User", back_populates="zaduzeni_statusi")
    
def init_my_database(app):
    with app.app_context():
        db.create_all() 
        print("Baza za Skladište i QA je spremna")