### Developer's Identity
Name : Zhillan Baniaksa

NPM : 2506637174

Class : PBP KKI

**live:** https://zhillan-baniaksa-myportfolio.pws.cs.ui.ac.id

### Local Setup
git clone https://github.com/ZhillanTLE/myportfolio.git
cd myportfolio
python -m venv env && source env/bin/activate
pip install -r requirements.txt
python manage.py runserver

### Reflection
1. 
    User clicks/types my myportfolio URL (e.g.,https://zhillan-baniaksa-myportfolio.pws.cs.ui.ac.id) which sends a request to the Django app.

    Project (urls.py) receives the request and checks the project-level config. It matches the /portfolio/ path and forwards it to the specific app handling that route using include() function.

    Application (ursl.py) application level URL dispatcher matches that specific pattern and directs the request to the designated view on views.py

    The View: view functions (classes) acts as the logic controller. It receives the request and recognizes that it would need data to fulfill, thus calling the Model to fetch the data.

    The Model: representing database schema as Python class. It translates view's request into SQL query. It fetches the relevant portfolio items from the database and returns them to the view as QuerySet.

    The Template: The view packages the QuerySet into a context dictionary and sends it into the HTML template. Django template engine processes the file using template tags (e.g., % for item in items %) to inject the database info into the HTML structure.

    Browser  Display: Takes fully rendered HTML document and returns it as an HTTP response to user's browser.

2. 
   It would be easier to scalable when the list inside is expanding as data stored in a model is highly flexible, may be filtered, ordered, paginated, or even searched using Django's ORM. Thus making future development easier and more organised. 


3. 
    'makemigrations' scans models.py files for any changes (additions, deletions, modifications) and generates a new migration file.

    'migrate' reads the migration files created by makemigrations and applies them to the actual database to update its table and columns. It also records what it applied in django_migrations table, so re-running doesnt re-apply anything.
    

#### Reflecting on AI Usage
Used Claude Code to find me why my 'python manage.py check" shows an error on tutorial 01. This was necessary since my eyes couldn't find which references was left out when i changed /myportfolio to /portfolio.

A full prompt record in [docs/ai-log.md](docs/ai-log.md).

I still believe while AI would do my Individual Assignment way faster, that is not the purpose of this course: for me (and everyone else) to learn even alongside AI help.

