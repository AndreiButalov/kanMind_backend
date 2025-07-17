# 🧠 KanMind – Kollaboratives Task-Management-System

KanMind ist eine intuitive, API-basierte Kanban-Board-Anwendung, mit der Teams Aufgaben planen, organisieren und kommentieren können. Das Backend basiert auf **Django** und **Django REST Framework**.

## 🚀 Features

- ✅ Benutzer-Authentifizierung via Token
- 👥 Boards mit mehreren Mitgliedern
- 📌 Aufgaben mit:
  - Titel, Beschreibung, Status, Priorität
  - Reviewer und Assignee (Mehrfach-Zuweisung möglich)
  - Fälligkeitstermin (Due Date)
  - Kommentare
- 💬 Kommentar-System mit Autor-Zuweisung
- 🔒 Rechteverwaltung:
  - Nur authentifizierte Nutzer (außer Gast) dürfen schreiben
- 📊 Board-Statistiken:
  - Anzahl der Mitglieder, Aufgaben, offene Aufgaben und Hoch-Prioritäts-Tickets

---

## 🧱 Tech-Stack

| Technologie        | Beschreibung                       |
|--------------------|------------------------------------|
| Django             | Python Web-Framework               |
| Django REST Framework | API-Erstellung & Serialisierung |
| Token Auth         | Benutzer-Authentifizierung         |
| SQLite / PostgreSQL| Datenbank                         |

---

## 📦 API Endpunkte (Auswahl)

### 🔐 Authentifizierung
- `/api/token/` – Token erhalten
- `/api/token/refresh/` – Token aktualisieren

### 🧠 Aufgaben
- `GET /tasks/` – Alle Aufgaben
- `POST /tasks/` – Neue Aufgabe
- `PATCH /tasks/<id>/` – Teilweise Aktualisierung
- `GET /assigned_tasks/` – Aufgaben, bei denen der Nutzer Assignee ist
- `GET /reviewer_tasks/` – Aufgaben, bei denen der Nutzer Reviewer ist

### 🗂️ Boards
- `GET /boards/` – Alle Boards
- `POST /boards/` – Neues Board erstellen
- `GET /boards/<id>/` – Board-Details
- `PATCH /boards/<id>/` – Board aktualisieren

### 💬 Kommentare
- `GET /tasks/<task_id>/comments/` – Kommentare zu einer Aufgabe
- `POST /tasks/<task_id>/comments/` – Kommentar hinzufügen
- `DELETE /comments/<id>/` – Kommentar löschen

---

## 🛡️ Rechte & Rollen

- Nur authentifizierte Benutzer dürfen Änderungen vornehmen.
- Benutzer mit dem Namen `Gast Gast` dürfen **nur lesend** auf Inhalte zugreifen.

---

## ⚙️ Setup-Anleitung

1. **Projekt klonen**
  ```bash
  git clone https://github.com/AndreiButalov/kanMind_backend.git
  python -m venv env
  "env/Scripts/activate"
  pip install -r requirements.txt
  python manage.py makemigrations
  python manage.py migrate
  python manage.py runserver
