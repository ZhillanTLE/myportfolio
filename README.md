### Developer's Identity
Name : Zhillan Baniaksa

NPM : 2506637174

Class : PBP KKI

**live:** https://zhillan-baniaksa-myportfolio.pws.cs.ui.ac.id

**updated**: 04/10/2026

do run Local Setup for grading measures:
### Local Setup
```
git clone https://github.com/ZhillanTLE/myportfolio.git
cd myportfolio
python -m venv env && source env/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Reflection 5
1. Debouncing lets the website load for rapid user actions. User makes network requests to a server to fetch or send data without reloading the page. Without debouncing, rapid user actions can cause major performance and cost issues.
2. Pause code execution until the network request finishes and returns its data.
3. XSS generally occurs when an application takes user input (like a comment or search query) and displays it back on the page without properly cleaning or escaping the code which would allow attackers to steal session cookies, hijack user accounts, log keystrokes, or redirect users to malicious sites.

A full reflection record in [docs/reflection-weekly.md](docs/reflection-weekly.md) 

#### Reflecting on AI Usage
Used Claude Code to find me why my 'python manage.py check" shows an error on tutorial 01. This was necessary since my eyes couldn't find which references was left out when i changed /myportfolio to /portfolio.

A full prompt record in [docs/ai-log.md](docs/ai-log.md).

I still believe while AI would do my Individual Assignment way faster, that is not the purpose of this course: for me (and everyone else) to learn even alongside AI help.

