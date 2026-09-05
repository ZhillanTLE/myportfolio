### Developer's Identity
Name : Zhillan Baniaksa

NPM : 2506637174

Class : PBP KKI

**live:** https://zhillan-baniaksa-myportfolio.pws.cs.ui.ac.id

### Local Setup
```bash
git clone https://github.com/ZhillanTLE/myportfolio.git
cd myportfolio
python -m venv env && source env/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Reflection
1. 
    Each 'article' having its own nested 'header'(.role-header) holding the title/org/dates, which separates what identifies this role and what i did in it turned out to be more useful than its meaning. .role-header is the flex container pushing the dates to the right, so the semantic boundary and the layout boundary happened to be the same box.

    The heading hierarchy says 'h1' name -> 'h2' Experience -> 'h3' per role. Because each role is its own article

    My CSS got simpler to name. I could write .role + .role for spacing between jobs instead of adding a wrapper div for a .last class

    However, i did not sure 'aside'. I looked at it and couldn't find anything on the page that qualified.

2. 
    My honest answer is that I haven't hit the responsive challenges yet, because i didn't write the responsive layer as it already existed.


3. 
    Most definitely changing into a less-poster looking frontend. With three roles, dumping everything on one page is fine. However if i want to input ten, that page becomes a boring wall.

#### Reflecting on AI Usage
Used Claude Code to find me why my 'python manage.py check" shows an error on tutorial 01. This was necessary since my eyes couldn't find which references was left out when i changed /myportfolio to /portfolio.

A full prompt record in [docs/ai-log.md](docs/ai-log.md).

I still believe while AI would do my Individual Assignment way faster, that is not the purpose of this course: for me (and everyone else) to learn even alongside AI help.

