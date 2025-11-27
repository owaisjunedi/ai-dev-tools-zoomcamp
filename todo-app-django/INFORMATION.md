# Project Architecture & Learning Guide 📘

> **For Future Reference:** This document explains the inner workings of the Retro Todo App. If you come back to this project in 6 months and forget how Django works, read this.

## 1. What is this Project?

This is a **Task Management System** (Todo App) built using **Django**, a high-level Python web framework. It goes beyond a basic "Hello World" app by including real-world features like database management, form handling, dynamic filtering, search functionality, priority levels, tagging system, and a stunning retro aesthetic.

---

## 2. The Database: Under the Hood 🗄️

One of the most intimidating parts of web development is the database. Here is exactly how it works in this project.

### What Database are we using?
We use **SQLite**.
* **Physical File**: `db.sqlite3` in the project root.
* **Why?**: It is serverless and creates a simple file on your disk. You don't need to install MySQL or PostgreSQL servers to run this app. It is the default for Django and perfect for development.

### How is the Database Created? (`Migrations`)
You never write SQL code (like `CREATE TABLE ...`) manually. Django does it for you.
1.  **Models (`models.py`)**: You define your data structure as Python classes.
2.  **`makemigrations`**: You run this command to tell Django, "I changed my Python model, please create a script to update the database." Django creates a file in `migrations/` (e.g., `0001_initial.py`).
3.  **`migrate`**: You run this command to actually execute those scripts. Django translates the Python instructions into SQL and modifies the `db.sqlite3` file.

### How is Data Stored? (Data Types)
In `todo/models.py`, we defined specific fields that map to database column types:

* **`CharField`** (`title`, `priority`, `tags`): Stores short text strings. In the database, this is `VARCHAR`.
* **`TextField`** (`description`): Stores unlimited length text. In the database, this is `TEXT`.
* **`DateTimeField`** (`created_at`, `due_date`): Stores exact date and time. In the database, this is `DATETIME`.
* **`BooleanField`** (`is_resolved`): Stores `True` (1) or `False` (0). In the database, this is `BOOL`.

### How do we Fetch Data? (The ORM)
Django uses an **Object-Relational Mapper (ORM)**. This lets us talk to the database using Python methods instead of SQL queries.

* **Fetching All**: `Todo.objects.all()` -> `SELECT * FROM todo_todo;`
* **Filtering**: `Todo.objects.filter(is_resolved=False)` -> `SELECT * FROM todo_todo WHERE is_resolved = 0;`
* **Saving**: `todo.save()` -> `INSERT INTO ...` or `UPDATE ...`
* **Deleting**: `todo.delete()` -> `DELETE FROM ...`

---

## 3. The Life of a Request (Application Flow) 🔄



Understanding how a user action turns into a web page is critical. Here are the three main "flows" in this application.

### Flow A: Viewing the Todo List (Standard GET Request)
1.  **User Action**: Enters `http://127.0.0.1:8000/` in browser.
2.  **`urls.py`**: Matches the empty string `''` pattern and points to `TodoListView`.
3.  **`views.py` (Controller)**:
    * `TodoListView` wakes up.
    * Runs `get_queryset()`: Fetches todos from DB, applies filters (search/tags), and annotates them for custom sorting.
    * Runs `get_context_data()`: Packs the todos + extra data (like the list of all tags) into a "Context" dictionary.
4.  **`templates/todo/todo_list.html` (View)**:
    * Receives the Context.
    * Uses `{% extends 'base.html' %}` to load the CSS/JS shell.
    * Loops through todos using `{% for todo in todos %}` to generate the HTML cards/rows.
5.  **Browser**: Receives the final HTML and displays the page.

### Flow B: Creating a Task (The "Magic" Priority Logic)
1.  **User Action**: Fills out the form and clicks "Save".
2.  **`views.py`**: `TodoCreateView` validates the form data. If valid, it calls `form.save()`.
3.  **`models.py` (The Interception)**:
    * The data **does not** go straight to the database!
    * Our custom `save()` method intercepts it.
    * **Logic**: It calculates `due_date - now`. If the difference is < 1 day, it forces `self.priority = 'critical'`.
    * **Final Step**: It calls `super().save()`, which finally writes the SQL `INSERT` to `db.sqlite3`.
4.  **Redirect**: The view sends the user back to the list page, where they see their new task (now colored red/orange based on the calculated priority).

### Flow C: The Calendar Modal (AJAX/Fetch Flow)
This is advanced because it doesn't reload the page.
1.  **User Action**: Clicks a task in the Calendar view.
2.  **JavaScript (`todo_calendar.html`)**:
    * Catches the click.
    * Fires a `fetch('/1/update/')` request.
    * **Crucial Detail**: Adds a header `X-Requested-With: XMLHttpRequest`.
3.  **`views.py`**:
    * `TodoUpdateView` receives the request.
    * It checks `get_template_names()`.
    * **Logic**: "Is this an AJAX request?" -> **YES**.
    * Instead of sending the full page (with navbar/footer), it sends **only** `todo_form_partial.html`.
4.  **Browser (JS)**:
    * Receives the HTML snippet (just the `<form>...</form>`).
    * Injects it into the Bootstrap Modal `<div class="modal-body">`.
    * Shows the modal to the user.

---

## 4. The "Why" and "How" of Custom Logic

### The Automated Priority Logic (`models.py`)
**The Goal:** Instead of forcing the user to arbitrarily decide if a task is "High" or "Medium" priority, we let the deadline dictate importance.

**The Implementation:**
We overrode the standard Django `save()` method on the `Todo` model.
1.  **Intercept Save**: Before writing to the database, the `save` method runs.
2.  **Calculate Delta**: We calculate `time_remaining = due_date - timezone.now()`.
3.  **Assign Priority**:
    * `< 1 day`: **Critical**
    * `< 3 days`: **High**
    * `< 7 days`: **Medium**
    * `Else`: **Low**
4.  **Super Save**: Finally, we call `super().save()` to actually write to the DB.

*Why this matters:* This is a classic example of **"Business Logic in the Model"**. It ensures that no matter *how* a todo is created (Admin panel, API, or Frontend form), the priority rules are always applied.

### The Retro Theme Architecture (`base.html`)
**The Goal:** Switch between a "Windows 95" look and a "Hacker Terminal" look instantly without reloading the page.

**The Implementation:**
We used **CSS Variables (Custom Properties)** defined under `:root[data-theme="light"]` and `:root[data-theme="dark"]`.

* **The Beveled 3D Effect**: To get that 90s button look, we didn't use standard shadows. We used border tricks:
    ```css
    /* Light Mode Borders */
    --border-light: #ffffff;  /* Top/Left = Light hitting the edge */
    --border-dark: #888888;   /* Bottom/Right = Shadow */
    
    /* The Button CSS */
    border-top: 2px solid var(--border-light);
    border-left: 2px solid var(--border-light);
    border-bottom: 2px solid var(--border-dark);
    border-right: 2px solid var(--border-dark);
    ```
* **Placeholder Text Fix**: In Dark mode, black placeholder text on a black background is invisible. We explicitly targeted `::placeholder` in CSS to set its color to `var(--text-secondary)`.

---

## 5. Django Components Deep Dive

### Views & QuerySets (`views.py`)
We used **Class-Based Views (CBVs)**.
* **Sorting Priorities**: Since 'Critical', 'High', etc., are strings, alphabetical sorting won't work (Critical > High > Low > Medium... is wrong).
    * *Solution*: We annotate the queryset using `Case` and `When` (SQL `CASE WHEN` statements) to assign numeric values (Critical=1, High=2...) and sort by that number.
* **The Calendar View**:
    * Django doesn't have a built-in calendar. We used Python's `calendar` library to generate a matrix of days (e.g., `[[0,0,1,2...], [3,4,5...]]`).
    * We fetch *all* todos for the month and group them into a Python dictionary: `{ day_number: [todo1, todo2] }`.
    * **Custom Template Filter**: In the HTML, we can't do `dict[key]`. We wrote a custom filter `get_item` (`templatetags/todo_extras.py`) to allow `{{ todos_by_date|get_item:day }}`.

### Templates (`templates/`)
* **Inheritance**: `base.html` holds the CSS, JS, and Navbar. Every other page uses `{% extends 'todo/base.html' %}` and injects content into `{% block content %}`.
* **AJAX Modal**: In `todo_calendar.html`, we don't reload the page to edit.
    1.  JS fetches the form HTML from `TodoUpdateView`.
    2.  `TodoUpdateView` detects `request.headers.get('x-requested-with') == 'XMLHttpRequest'` and returns a *partial* template (`todo_form_partial.html`) without the navbar/footer.
    3.  JS injects this HTML into the Bootstrap Modal.

---

## 6. Common Pitfalls & Solutions (For the Learner)

If you try to build this again, you will likely hit these errors (we did!):

1.  **Template Syntax Error: "Invalid block tag"**
    * *Cause*: Splitting tags across lines.
    * *Wrong*: `{% if condition \n %}`
    * *Right*: `{% if condition %}` (Must be on one line).

2.  **Template Syntax Error: "Could not parse remainder"**
    * *Cause*: Missing spaces in comparison operators.
    * *Wrong*: `{% if value=="x" %}`
    * *Right*: `{% if value == "x" %}` (Django is picky about spaces!).

3.  **JavaScript Scope Issues**
    * *Problem*: `onclick` functions not working.
    * *Cause*: Placing `{% block extra_scripts %}` *inside* an existing `<script>` tag in the parent template creates nested script tags (invalid HTML).
    * *Fix*: Always place block hooks *outside* `<script>` tags in `base.html`.

4.  **Calendar Distortion**
    * *Problem*: Long todos stretch the table cells, breaking the grid.
    * *Fix*: Use `table-layout: fixed` in CSS, set specific widths (`width: 14.28%` for 7 days), and use `overflow-y: auto` on the cell content container.

---

## 7. Glossary of Terms

-   **MVT**: Model-View-Template (Django's version of MVC).
-   **ORM**: Object-Relational Mapper (Allows writing Python `Todo.objects.all()` instead of SQL `SELECT * FROM todo`).
-   **Migration**: A file that tells the database how to change its structure (e.g., "Add a priority column").
-   **Context Processor**: Functions that run for *every* request to add data to templates (used for standard things like `user` or `messages`).

## 8. Future Challenges for You

Ready to level up? Try implementing these:
1.  **User Accounts**: Use `django.contrib.auth` so users only see *their own* todos.
2.  **Drag & Drop**: Use a JS library like `SortableJS` to drag todos between status columns.
3.  **Recurring Tasks**: Modify the model to handle "Repeat every Monday".

Happy coding! 🎬✨