**Full-Stack Resource Management Solution with integrated QA Incident Tracking.**

---

## Overview

Ovaj projekat predstavlja hibridnu platformu za upravljanje IT resursima (ITAM) i istovremeno praćenje njihove ispravnosti (Bug Tracking).

Sistem zamenjuje haotičnu komunikaciju mejlovima centralizovanim dashboard-om gde se u svakom trenutku vidi lokacija opreme, njeno stanje i prioritetni kvarovi.

### Ključne funkcionalnosti (Day 1 - Day 4 Progres)
* **Inventory & Tracking:** Centralizovana evidencija IT opreme sa lokacijama.
* **Incident QA:** Registar kvarova direktno povezan sa stavkama iz inventara.
* **User Authentication & Roles:** Login sistem sa različitim nivoima pristupa (Admin, User).
* **Full CRUD Operacije:** Kompletno upravljanje (Kreiranje, Čitanje, Izmena, Brisanje) nad resursima i korisnicima.
* **Audit Trail:** Svaki incident je mapiran na konkretnog korisnika radi praćenja odgovornosti.

## Tehnologije

* **Backend:** Python 3.x, Flask
* **Database & ORM:** SQL (SQLite), SQLAlchemy
* **Frontend:** HTML5, CSS3, JavaScript
* **Development Tools:** Git, GitHub, AI-assisted development

## Plan za budućnost (QA & PM focus)

- [ ] Implementacija automatskih email obaveštenja za admine pri prijavi kvara.
- [ ] Dodavanje automatskih testova (npr. Pytest/Selenium) za login formu.
- [ ] Analitika kvarova po lokacijama/tipovima opreme.

---
*Projekat je razvijen kao deo interne prakse za digitalizaciju procesa male firme.*
