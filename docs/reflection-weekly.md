## Past reflections

### Assignment 1's Reflection

1. 
    Each 'article' having its own nested 'header'(.role-header) holding the title/org/dates, which separates what identifies this role and what i did in it turned out to be more useful than its meaning. .role-header is the flex container pushing the dates to the right, so the semantic boundary and the layout boundary happened to be the same box.

    The heading hierarchy says 'h1' name -> 'h2' Experience -> 'h3' per role. Because each role is its own article

    My CSS got simpler to name. I could write .role + .role for spacing between jobs instead of adding a wrapper div for a .last class

    However, i did not sure 'aside'. I looked at it and couldn't find anything on the page that qualified.

2. 
    My honest answer is that I haven't hit the responsive challenges yet, because i didn't write the responsive layer as it already existed.


3. 
    Most definitely changing into a less-poster looking frontend. With three roles, dumping everything on one page is fine. However if i want to input ten, that page becomes a boring wall.

### Assignment 2's Reflection

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

### Assignment 3's Reflection

1. 
    We use Django’s ModelForm instead of creating HTML forms manually in ordere to build scalable systems when we want to add another form. This also stands along with SRP (Single Responsibility Principle) to separate the logic of HTML, and logic of forms.

    Additionally, It is necessary to add {% csrf token %} Because attackers cannot easily guess or generate the secure token, so their forged requests will be rejected by the server.


2. 
   JSON (JavaScript Object Notation) is preferred over XML (Extensible Markup Language) in modern web development because it is lighter, faster to parse, and **natively** integrates with JavaScript. While XML was once the enterprise standard for data exchange, JSON has become the default choice for modern web applications, Single-Page Applications (SPAs), and RESTful APIs.


3. 
    The view runs QuerySet through serializers.serialize("json", ...), which extracts only the field values from each Project and converts them into JSON string. It will then return it in an HttpResponse with content_type="application/json", because a model instance is a live Python object (methods, database connection, memory address) that cannot be sent over HTTP, whereas JSOn is plain text that any client can parse.
