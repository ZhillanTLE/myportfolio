### Developer's Identity
Name : Zhillan Baniaksa

NPM : 2506637174

Class : PBP KKI

**live:** https://zhillan-baniaksa-myportfolio.pws.cs.ui.ac.id
**current state:** waiting for dbs credentials from ITF, thus not yet updated to the latest changes!

do run Local Setup for grading measures:
### Local Setup
git clone https://github.com/ZhillanTLE/myportfolio.git
cd myportfolio
python -m venv env && source env/bin/activate
pip install -r requirements.txt
python manage.py runserver

### Reflection
1. 
    We use Django’s ModelForm instead of creating HTML forms manually in ordere to build scalable systems when we want to add another form. This also stands along with SRP (Single Responsibility Principle) to separate the logic of HTML, and logic of forms.

    Additionally, It is necessary to add {% csrf token %} Because attackers cannot easily guess or generate the secure token, so their forged requests will be rejected by the server.


2. 
   JSON (JavaScript Object Notation) is preferred over XML (Extensible Markup Language) in modern web development because it is lighter, faster to parse, and **natively** integrates with JavaScript. While XML was once the enterprise standard for data exchange, JSON has become the default choice for modern web applications, Single-Page Applications (SPAs), and RESTful APIs.


3. 
    The view runs QuerySet through serializers.serialize("json", ...), which extracts only the field values from each Project and converts them into JSON string. It will then return it in an HttpResponse with content_type="application/json", because a model instance is a live Python object (methods, database connection, memory address) that cannot be sent over HTTP, whereas JSOn is plain text that any client can parse.

    
A full reflection record in [docs/reflection-weekly.md](docs/reflection-weekly.md) 

#### Reflecting on AI Usage
Used Claude Code to find me why my 'python manage.py check" shows an error on tutorial 01. This was necessary since my eyes couldn't find which references was left out when i changed /myportfolio to /portfolio.

A full prompt record in [docs/ai-log.md](docs/ai-log.md).

I still believe while AI would do my Individual Assignment way faster, that is not the purpose of this course: for me (and everyone else) to learn even alongside AI help.

