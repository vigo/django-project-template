![Django](https://img.shields.io/badge/django-1.11.4-green.svg)
![Version](https://img.shields.io/badge/version-0.1.2-yellow.svg)

# Django Project Starter Template

My custom project starter for Django! I’ll try to support every upcoming
Django releases as much as I can!

## Requirements

- Latest Python 3.6+ runtime environment.
- `pip`, `virtualenv`, `virtualenvwrapper`
- If you like to run Rake Tasks, you need `Ruby` too but not required.

## Installation

Please use `virtualenvwrapper` and create your environment and activate it.

```bash
# example
$ mkvirtualenv my_projects_env
# or make it active:
$ workon my_projects_env
```

You need to declare **2 environment** variables. I always put my project
specific environment variables under `virtualenvwrapper`’s `postactivate`
file. Open your `~/.virtualenvs/my_projects_env/bin/postactivate` and add
these lines:

```bash
export DJANGO_ENV="development"
export DJANGO_SECRET="YOUR-SECRET-HERE" # will fix it in a second.
```

then;

```bash
# for django 1.11.4
$ curl -L https://github.com/vigo/django-project-template/archive/django-1.11.4.zip > template.zip
$ unzip template.zip
$ mv django-project-template-django-1.11.4 my_project && rm template.zip
$ cd my_project/
$ cp config/settings/development.example.py config/settings/development.py
# development.py is not under revison control
$ pip install -r requirements/development.pip
$ git init # now you can start your own repo!
```

or, you can use installer script:

```bash
$ bash <(curl -fsSL https://raw.githubusercontent.com/vigo/django-project-template/master/install.sh)
$ cd YOUR_PROJECT/
$ pip install -r requirements/development.pip
$ git init # now you can start your own repo!
```

This template comes with custom User model. Please take a look at it. If you
need to add/change fields, please do so. If you change anything, please run `makemigrations`
to keep track of your db. Then continue to work:

```bash
$ python manage.py migrate
$ python manage.py createsuperuser
# enter: Email, First Name, Last Name and password
$ python manage.py runserver_plus # or
$ rake
```

Now, please generate your secret via:

```bash
$ python manage.py generate_secret_key
```

and fix your `~/.virtualenvs/my_projects_env/bin/postactivate`

---

## Features

- Custom `User` Model
- Custom `BaseModel`
- Custom `BaseModelWithSoftDelete`
- Custom manager for `BaseModel` and `BaseModelWithSoftDelete`
- More useful Django Application structure!
- Settings abstraction: Development / Production / Heroku / Test
- Requirement abstraction depending on your environment!
- Custom logger and log formatters
- App and Model creator management commands
- Custom Locale middleware
- Debug Mixins for your HTML templates
- Handy utils: `console`, `console.dir()`, `numerify`, `urlify`, `save_file`
- File widget for Django Admin: `AdminImageFileWidget`

---

## Quick Start

Let’s create `blog` application. We’ll have two models. `Post` and `Category`.
First, create application:

```bash
$ python manage.py baseapp_create_app blog
"blog" application created.


    - Do not forget to add your `blog` to `INSTALLED_APPS` under `config/settings/base.py`:

    INSTALLED_APPS += [
        'blog',
    ]

    - Do not forget to fix your `config/settings/urls.py`:

    urlpatterns = [
        # ...
        # this is just an example!
        url(r'^__blog__/', include('blog.urls', namespace='blog')),
        # ..
    ]


```

Fix your `config/settings/base.py`, add this newly created app to your `INSTALLED_APPS`:

```python
# config/settings/base.py
:
:
AUTH_USER_MODEL = 'baseapp.User'

INSTALLED_APPS += [
    'blog',
]

```

Now, if you fix your `config/settings/urls.py` you’ll be able to see demo
pages for your app:

```python
# config/settings/urls.py
:
:
urlpatterns = [
    # ...
    url(r'^__blog__/', include('blog.urls', namespace='blog')),
    # ..
]
```

Now run server and call `http://127.0.0.1:8000/__blog__/`:

```bash
$ python manage.py runserver
```

You’ll see `Hello from Blog` page and If you check `blog/views.py` you’ll see
and example usage of `HtmlDebugMixin` and `console` util. 

```python
from django.views.generic.base import TemplateView

from baseapp.mixins import HtmlDebugMixin
from baseapp.utils import console


console.configure(
    source='blog/views.py',
)


class BlogView(HtmlDebugMixin, TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        self.hdbg('Hello from hdbg')
        kwargs = super().get_context_data(**kwargs)
        console.dir(self.request.user)
        return kwargs

```

Let’s look at our `blog` application structure:

    applications/blog/
    ├── admin
    │   └── __init__.py
    ├── migrations
    │   └── __init__.py
    ├── models
    │   └── __init__.py
    ├── apps.py
    ├── urls.py
    └── views.py

Now lets add `Post` model with **soft-delete** feature!

```bash
$ python manage.py baseapp_create_model blog Post softdelete
models/post.py created.
admin/post.py created.
Post model added to models/__init__.py
Post model added to admin/__init__.py


    `Post` related files created successfully:

    - `blog/models/post.py`
    - `blog/admin/post.py`

    Please check your models before running `makemigrations` ok?

```

This creates `blog/models/post.py` and `blog/admin/post.py` files:

```python
# blog/models/post.py

from django.utils.translation import ugettext_lazy as _
from django.db import models

from baseapp.models import BaseModelWithSoftDelete


__all__ = [
    'Post',
]


class Post(BaseModelWithSoftDelete):
    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )

    class Meta:
        app_label = 'blog'
        verbose_name = _('Post')
        verbose_name_plural = _('Post')
    
    def __str__(self):
        return self.title


```

and `Category` model:

```bash
$ python manage.py baseapp_create_model blog Category softdelete
models/category.py created.
admin/category.py created.
Category model added to models/__init__.py
Category model added to admin/__init__.py


    `Category` related files created successfully:

    - `blog/models/category.py`
    - `blog/admin/category.py`

    Please check your models before running `makemigrations` ok?

```

Now It’s time to fix our models by hand!

```python
# blog/models/post.py

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db import models

from baseapp.models import BaseModelWithSoftDelete


__all__ = [
    'Post',
]


class Post(BaseModelWithSoftDelete):
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('Author'),
    )
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('Category'),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title'),
    )
    body = models.TextField(
        verbose_name=_('Body'),
    )

    class Meta:
        app_label = 'blog'
        verbose_name = _('Post')
        verbose_name_plural = _('Post')

    def __str__(self):
        return self.title

```

We’ll keep `blog/models/category.py` same, `Category` will have only `title`
field:

```python
# blog/models/category.py

from django.utils.translation import ugettext_lazy as _
from django.db import models

from baseapp.models import BaseModelWithSoftDelete


__all__ = [
    'Category',
]


class Category(BaseModelWithSoftDelete):
    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )

    class Meta:
        app_label = 'blog'
        verbose_name = _('Category')
        verbose_name_plural = _('Category')
    
    def __str__(self):
        return self.title


```


Now It’s time to create migrations:

```bash
$ python manage.py makemigrations --name create_post_and_category
Migrations for 'blog':
  applications/blog/migrations/0001_create_post_and_category.py
    - Create model Category
    - Create model Post
```

Now migrate!

```bash
$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, baseapp, blog, contenttypes, sessions
Running migrations:
  Applying blog.0001_create_post_and_category... OK
```

Now time to run server and dive in to admin page!

```bash
$ python manage.py runserver
Performing system checks...

System check identified no issues (0 silenced).
September 21, 2017 - 13:34:54
Django version 1.11.4, using settings 'config.settings.development'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Open `http://127.0.0.1:8000/admin/` and use your superuser credentials.

---

## Project File/Folder Structure

What I’ve changed ?

- All Django apps live under `applications/` folder.
- All of the models live under `models/` folder.
- All of the admin files live under `admin/` folder.
- Every app should contain It’s own `urls.py`.
- All settings related files will live under `config/settings/` folder.
- Every environment has It’s own setting such as `config/settings/development.py`.
- Every environment/settings can have It’s own package/module requirements.
- All of the templates live under basedir’s `templates/APP_NAME` folder.
- All of the locales live under basedir’s `locale/LANG/...` folder.
- Lastly, Ruby and Python can be friends in a Django Project!

Here is directory/file structure:

    .
    ├── applications
    │   └── baseapp
    │       ├── admin
    │       ├── libs
    │       ├── management
    │       ├── middlewares
    │       ├── migrations
    │       ├── mixins
    │       ├── models
    │       ├── static
    │       ├── templatetags
    │       ├── tests
    │       ├── utils
    │       ├── widgets
    │       ├── __init__.py
    │       ├── apps.py
    │       ├── urls.py
    │       └── views.py
    ├── config
    │   ├── settings
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   ├── development.example.py
    │   │   ├── development.py
    │   │   ├── heroku.py
    │   │   └── test.py
    │   ├── __init__.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── db
    │   └── development.sqlite3
    ├── locale
    │   └── tr
    │       └── LC_MESSAGES
    ├── media
    │   └── avatar
    ├── requirements
    │   ├── base.pip
    │   ├── development.pip
    │   └── heroku.pip
    ├── static
    ├── templates
    │   └── baseapp
    │       ├── base.html
    │       └── index.html
    ├── LICENSE.txt
    ├── Procfile
    ├── README.md
    ├── Rakefile
    ├── manage.py
    ├── requirements.txt
    └── runtime.txt

---

## Settings and Requirements Abstraction

By default, `manage.py` looks for `DJANGO_ENV` environment variable. Builds 
`DJANGO_SETTINGS_MODULE` environment variable according to `DJANGO_ENV` variable.
If your `DJANGO_ENV` environment variable is set to `production`, this means that
you are running `config/settings/production.py`.

Also `config/wsgi.py` looks for `DJANGO_ENV` environment variable too. For
example, If you want to deploy this application to **HEROKU**, you need
`config/settings/heroku.py` and must add config variable `DJANGO_ENV` and set
it to `heroku` on HEROKU site. (*You’ll find more information further below*)

All the other settings files (*according to environment*) imports
`config/settings/base.py` and gets everything from it. `development.py` is
un-tracked/git-ignored file. Original file is `development.example.py`. You
need to create a copy of it! (*if you follow along from the beginning, you’ve already did this*)

All the base/common required Python packages/modules are defined under `requirements/base.pip`:

```python
Django==1.11.4
Pillow==4.2.1
```

### `development.py`

Logging is enabled. In `CUSTOM_LOGGER_OPTIONS`, you can specify un-wanted file
types not to log your dev-console. You can un-comment `django.db.backends` if
you want to see the SQL queries. Example:

```python
LOGGING = {
    :
    :
    'loggers': {
        :
        :
        'django.db.backends': {
            'handlers': ['console_sql'],
            'level': 'DEBUG',
        },
        
    }
}
```

By default, this template ships with 2 awesome/handy Django packages:

- [Django Extensions][01]
- [Django Debug Toolbar][02]

We are using `Werkzeug` as Django server and overriding It’s logging formats.
Django Extension adds great functionalities:

- `admin_generator`
- `clean_pyc`
- `clear_cache`
- `compile_pyc`
- `create_app`
- `create_command`
- `create_jobs`
- `create_template_tags`
- `delete_squashed_migrations`
- `describe_form`
- `drop_test_database`
- `dumpscript`
- `export_emails`
- `find_template`
- `generate_secret_key`
- `graph_models`
- `mail_debug`
- `notes`
- `passwd`
- `pipchecker`
- `print_settings`
- `print_user_for_session`
- `reset_db`
- `runjob`
- `runjobs`
- `runprofileserver`
- `runscript`
- `runserver_plus`
- `set_default_site`
- `set_fake_emails`
- `set_fake_passwords`
- `shell_plus`
- `show_template_tags`
- `show_templatetags`
- `show_urls`
- `sqlcreate`
- `sqldiff`
- `sqldsn`
- `sync_s3`
- `syncdata`
- `unreferenced_files`
- `update_permissions`
- `validate_templates`

One of my favorite: `python manage.py show_urls` :)

`AUTH_PASSWORD_VALIDATORS` are removed for development purposes. You can enter
simple passwords such as `1234`. `MEDIA_ROOT` is set to basedir’s `media` folder,
`STATICFILES_DIRS` includes basedir’s `static` folder.

All the required modules are defined under `requirements/development.pip`:

```python
# requirements/development.pip
-r base.pip
ipython==6.1.0
django-extensions==1.9.0
Werkzeug==0.12.2
django-debug-toolbar==1.8
```

### `test.py`

Basic settings for running tests.

### `heroku.py`

You can deploy your app to HEROKU super easy. Just set your `ALLOWED_HOSTS`.
Add your heroku domain here:

```python
ALLOWED_HOSTS = [
    'lit-eyrie-63238.herokuapp.com', # example heroku domain
]
```

All the required modules are defined under `requirements/heroku.pip`:

```python
# requirements/heroku.pip
-r base.pip
gunicorn==19.7.1
psycopg2==2.7.3
dj-database-url==0.4.2
whitenoise==3.3.0
```

By default, Heroku requires `requirements.txt`. Therefore we have it too :)

```python
# requirements.txt
-r requirements/heroku.pip
```

Heroku also requires `Procfile` and `runtime.txt`. Both provided in the basedir.
Don’t forget to create heroku config variables:

```bash
$ heroku login
$ heroku apps:create
$ heroku addons:create heroku-postgresql:hobby-dev
$ heroku config:set DJANGO_ENV="heroku"
$ heroku config:set DJANGO_SECRET='YOUR_GENERATED_RANDOM_SECRET'
$ heroku config:set WEB_CONCURRENCY=3
$ git push heroku master
$ heroku run python manage.py migrate
$ heroku run python manage.py createsuperuser
```

### Others

If you are using different platform or OS, such as Ubuntu or your custom
servers, you can follow the settings and requirements conventions. If you name
it `production`, create your `config/settings/production.py` and
`requirements/production.pip`. You must set you `DJANGO_ENV` to `production`
and don’t forget to set `DJANGO_ENV` and `DJANGO_SECRET` on your production
server!

---

## `User` model

This is custom model which uses `AbstractBaseUser` and `PermissionsMixin`.
Fields are:

- `created_at`
- `updated_at`
- `email`
- `first_name`
- `middle_name` (optional)
- `last_name`
- `avatar` (optional)
- `is_active`
- `is_staff`
- `is_superuser`

Username field is set to: `email`. Your users will login using their email’s
and password’s by default. You can modify everything if you like to. This also
mimics like default User model of Django. Available methods are:

- `get_short_name`
- `get_full_name`

---

## `BaseModel`

This is a common model. By default, `BaseModel` contains these fields:

- `created_at`
- `updated_at`
- `status`

Also has custom manager called: `objects_bm`. There are 4 basic status types:

```python
STATUS_OFFLINE = 0
STATUS_ONLINE = 1
STATUS_DELETED = 2
STATUS_DRAFT = 3
```

Custom manager has custom querysets against these statuses such as:

```python
>>> Post.objects_bm.deleted()  # filters: status = STATUS_DELETED
>>> Post.objects_bm.actives()  # filters: status = STATUS_ONLINE
>>> Post.objects_bm.offlines() # filters: status = STATUS_OFFLINE
>>> Post.objects_bm.drafts()   # filters: status = STATUS_DRAFT
```

## `BaseModelWithSoftDelete`

This model inherits from `BaseModel` and provides fake deletion which is
probably called **SOFT DELETE**. Works with related objects who has
`on_delete` option is set to `models.CASCADE`. This means, when you call
model’s `delete()` method or QuerySet’s `delete()` method, it acts like delete
action but never deletes the data.

Just sets the status field to `STATUS_DELETED` and sets `deleted_at` field to
**NOW**.

This works exactly like Django’s `delete()`. Broadcasts `pre_delete` and
`post_delete` signals and returns the number of objects marked as deleted and
a dictionary with the number of deletion-marks per object type.

```python
>>> Post.objects_bm.all()

SELECT "blog_post"."id",
       "blog_post"."created_at",
       "blog_post"."updated_at",
       "blog_post"."status",
       "blog_post"."deleted_at",
       "blog_post"."author_id",
       "blog_post"."category_id",
       "blog_post"."title",
       "blog_post"."body"
  FROM "blog_post"
 LIMIT 21

Execution time: 0.000135s [Database: default]

<BaseModelWithSoftDeleteQuerySet [<Post: Python post 1>, <Post: Python post 2>, <Post: Python post 3>]>

>>> Category.objects_bm.all()

SELECT "blog_category"."id",
       "blog_category"."created_at",
       "blog_category"."updated_at",
       "blog_category"."status",
       "blog_category"."deleted_at",
       "blog_category"."title"
  FROM "blog_category"
 WHERE "blog_category"."deleted_at" IS NULL
 LIMIT 21

<BaseModelWithSoftDeleteQuerySet [<Category: Python>]>

>>> Category.objects_bm.delete()
(4, {'blog.Category': 1, 'blog.Post': 3})

>>> Category.objects_bm.all()
<BaseModelWithSoftDeleteQuerySet []>       # rows are still there! don’t panic!

>>> Category.objects.all()
<QuerySet [<Category: Python>]>

```

`BaseModelWithSoftDeleteQuerySet` has these query options according to
`status` field:

- `.all()`
- `.delete()`
- `.undelete()`
- `.deleted()`

When soft-delete enabled (*during model creation*), Django admin will
automatically use `BaseAdminWithSoftDelete` which is inherited from:
 `BaseAdmin` <- `admin.ModelAdmin`.

---

## `BaseAdmin`, `BaseAdminWithSoftDelete`

Inherits from `admin.ModelAdmin`. By default, adds `status` to `list_filter`.
You can disable this via setting `sticky_list_filter = None`. When model is
created with `rake new:model...` or from management command, admin file is
automatically generated. 

Example for `Post` model admin.

```python
from django.contrib import admin

from baseapp.admin import BaseAdminWithSoftDelete

from ..models import Post


__all__ = [
    'PostAdmin',
]


class PostAdmin(BaseAdminWithSoftDelete):
    # sticky_list_filter = None
    # hide_deleted_at = False
    pass


admin.site.register(Post, PostAdmin)

```

By default, `deleted_at` excluded from admin form like `created_at` and
`updated_at` fields. You can also override this via `hide_deleted_at` attribute.
Comment/Uncomment lines according to your needs! This works only in `BaseAdminWithSoftDelete`.

`BaseAdminWithSoftDelete` also comes with special admin action. You can
recover/make active (*undelete*) multiple objects like deleting items.

---

## Custom logger and log formatters

Template ships with `CustomWerkzeugLogFormatter` and `CustomSqlLogFormatter`.
Default development server uses [Werkzeug][03]. Logging is customized against
Werkzeug’s output. Example usage:

```python
import logging
logger = logging.getLogger('user_logger') # config/setting/development.py
logger.warning('This is Warning')
```

`werkzueg_filter_extenstions_callback` is stands for `CUSTOM_LOGGER_OPTIONS`’s
`hide_these_extensions` settings.

---

## `CustomLocaleMiddleware`

This is mostly used for our custom projects. Injects `LANGUAGE_CODE` variable to
`request` object. `/en/path/to/page/` sets `request.LANGUAGE_CODE` to `en` otherwise `tr`.

```python
# add this to your settings/base.py
MIDDLEWARE += [
    'baseapp.middlewares.CustomLocaleMiddleware',
]
```

---

## `HtmlDebugMixin`

`HtmlDebugMixin` injects `{{ IS_DEBUG }}` and `{{ LANG }}` template variables
to context. Also with `self.hdbg(arg, arg, arg)` method, you can debug
anything from view to html template...

```python
# example: views.py

from django.views.generic.base import TemplateView

from baseapp.mixins import HtmlDebugMixin

class IndexView(HtmlDebugMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        self.hdbg('This', 'is', 'an', 'example', 'of')
        self.hdbg('self.hdbg', 'usage')
        self.hdbg(self.request.__dict__)
        return kwargs

```

Just add `{% hdbg %}` in to your `templates/index.html`:

```django
<!-- example: index.html -->
<h1>Hello World</h1>
{% hdbg %}
```

Outputs to Html:

    ('This', 'is', 'an', 'example', 'of')
    ('self.hdbg', 'usage')
    ({'COOKIES': {'__utma': '****',
                  '__utmz': '****',
                  'csrftoken': '****',
                  'djdt': 'hide',
                  'language': 'tr'},
      'META': {'CSRF_COOKIE': '****',
               'CSRF_COOKIE_USED': True,
               'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'HTTP_ACCEPT_ENCODING': 'gzip, deflate',
               'HTTP_ACCEPT_LANGUAGE': 'en-us',
               'HTTP_CONNECTION': 'keep-alive',
               'HTTP_COOKIE': '****; ',
               'HTTP_DNT': '1',
               'HTTP_HOST': '127.0.0.1:8000',
               'HTTP_UPGRADE_INSECURE_REQUESTS': '1',
               'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) '
                                  'AppleWebKit/603.3.8 (KHTML, like Gecko) '
                                  'Version/10.1.2 Safari/603.3.8',
               'PATH_INFO': '/__baseapp__/',
               'QUERY_STRING': '',
               'REMOTE_ADDR': '127.0.0.1',
               'REMOTE_PORT': 61081,
               'REQUEST_METHOD': 'GET',
               'SCRIPT_NAME': '',
               'SERVER_NAME': '127.0.0.1',
               'SERVER_PORT': '8000',
               'SERVER_PROTOCOL': 'HTTP/1.1',
               'SERVER_SOFTWARE': 'Werkzeug/0.12.2',
               'werkzeug.request': <BaseRequest 'http://127.0.0.1:8000/__baseapp__/' [GET]>,
               'wsgi.errors': <_io.TextIOWrapper name='<stderr>' mode='w' encoding='UTF-8'>,
               'wsgi.input': <_io.BufferedReader name=6>,
               'wsgi.multiprocess': False,
               'wsgi.multithread': False,
               'wsgi.run_once': False,
               'wsgi.url_scheme': 'http',
               'wsgi.version': (1, 0)},
      '_cached_user': <django.contrib.auth.models.AnonymousUser object at 0x111360e48>,
      '_messages': <django.contrib.messages.storage.fallback.FallbackStorage object at 0x111360748>,
      '_post_parse_error': False,
      '_read_started': False,
      '_stream': <django.core.handlers.wsgi.LimitedStream object at 0x1113602e8>,
      'content_params': {},
      'content_type': '',
      'csrf_processing_done': True,
      'environ': {'CSRF_COOKIE': '****',
                  'CSRF_COOKIE_USED': True,
                  'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                  'HTTP_ACCEPT_ENCODING': 'gzip, deflate',
                  'HTTP_ACCEPT_LANGUAGE': 'en-us',
                  'HTTP_CONNECTION': 'keep-alive',
                  'HTTP_COOKIE': '****',
                  'HTTP_DNT': '1',
                  'HTTP_HOST': '127.0.0.1:8000',
                  'HTTP_UPGRADE_INSECURE_REQUESTS': '1',
                  'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X '
                                     '10_12_6) AppleWebKit/603.3.8 (KHTML, like '
                                     'Gecko) Version/10.1.2 Safari/603.3.8',
                  'PATH_INFO': '/__baseapp__/',
                  'QUERY_STRING': '',
                  'REMOTE_ADDR': '127.0.0.1',
                  'REMOTE_PORT': 61081,
                  'REQUEST_METHOD': 'GET',
                  'SCRIPT_NAME': '',
                  'SERVER_NAME': '127.0.0.1',
                  'SERVER_PORT': '8000',
                  'SERVER_PROTOCOL': 'HTTP/1.1',
                  'SERVER_SOFTWARE': 'Werkzeug/0.12.2',
                  'werkzeug.request': <BaseRequest 'http://127.0.0.1:8000/__baseapp__/' [GET]>,
                  'wsgi.errors': <_io.TextIOWrapper name='<stderr>' mode='w' encoding='UTF-8'>,
                  'wsgi.input': <_io.BufferedReader name=6>,
                  'wsgi.multiprocess': False,
                  'wsgi.multithread': False,
                  'wsgi.run_once': False,
                  'wsgi.url_scheme': 'http',
                  'wsgi.version': (1, 0)},
      'method': 'GET',
      'path': '/__baseapp__/',
      'path_info': '/__baseapp__/',
      'resolver_match': ResolverMatch(func=baseapp.views.IndexView, args=(), kwargs={}, url_name=index, app_names=[], namespaces=['baseapp']),
      'session': <django.contrib.sessions.backends.db.SessionStore object at 0x111360240>,
      'user': <SimpleLazyObject: <django.contrib.auth.models.AnonymousUser object at 0x111360e48>>},)

---

## `baseapp.utils.console`

Do you need to debug an object from the View or anywhere from your Python
script? Sometimes you need to print out some variable(s) or values to console
and you want to keep it safe right? `print()` is very dangerous if you forget
on production server.

`console()`, `console.dir()` they both work only under `DEBUG = True` mode.

```python
# example: views.py

from baseapp.utils import console

class IndexView(TemplateView):
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        console('Hello', 'World')
        console.dir(self.request.user)
        return kwargs
```

Now `console.dir()` outputs to terminal:

    instance of AnonymousUser | <class 'django.utils.functional.SimpleLazyObject'>**
    (   {   'arg': (   <SimpleLazyObject: <django.contrib.auth.models.AnonymousUser object at 0x10c3229e8>>,),
            'instance_attributes': ['_setupfunc', '_wrapped'],
            'internal_methods': [   '__class__', '__delattr__', '__dict__',
                                    '__dir__', '__doc__', '__eq__', '__format__',
                                    '__ge__', '__getattribute__', '__gt__',
                                    '__hash__', '__init__', '__init_subclass__',
                                    '__le__', '__lt__', '__module__', '__ne__',
                                    '__new__', '__reduce__', '__reduce_ex__',
                                    '__repr__', '__setattr__', '__sizeof__',
                                    '__str__', '__subclasshook__', '__weakref__'],
            'private_methods': ['_groups', '_user_permissions'],
            'public_attributes': [   'check_password', 'delete',
                                     'get_all_permissions',
                                     'get_group_permissions', 'get_username',
                                     'groups', 'has_module_perms', 'has_perm',
                                     'has_perms', 'id', 'is_active',
                                     'is_anonymous', 'is_authenticated',
                                     'is_staff', 'is_superuser', 'pk', 'save',
                                     'set_password', 'user_permissions',
                                     'username'],
            'public_methods': ['_setupfunc']},)
    ********************************************************************************

You can set defaults for `console`:

```python
from baseapp.utils import console

console.configure(
    char='x',            # banners will use `x` character
    source='console.py', # banner title will be `console.py`
    width=8,             # output width will wrap to 8 chars (demo purpose)
    indent=8,            # 8 characters will be userd for indention (demo purpose)
    color='white',       # banner color will be: white
)

console.configure(color='default') # resets color
console('Hello again...')
```

There are few basic color options available:

- black
- red
- green
- yellow
- blue
- magenta
- cyan
- white
- default

---

## `baseapp.utils.numerify`

Little helper for catching **QUERY_STRING** parameters for numerical values:

```python
from baseapp.utils import numerify

>>> numerify("1")
1
>>> numerify("1a")
-1
>>> numerify("ab")
-1
>>> numerify("abc", default=44)
44
```

---

## `baseapp.utils.urlify`

Turkish language and Django’s `slugify` are not working well together. This
little pre-processor will prep string for slugification :)

```python
from django.utils.text import slugify
from baseapp.utils import urlify

>>> slugify(urlify('Merhaba Dünya!'))
'merhaba-dunya'

>>>  slugify(urlify('Merhaba Dünya! ĞŞİ'))
'merhaba-dunya-gsi'
```

---

## `baseapp.utils.save_file`

While using `FileField`, sometimes you need to handle uploaded files. In this
case, you need to use `upload_to` attribute. Take a look at the example in `baseapp/models/user.py`:

```python
from baseapp.utils import save_file as custom_save_file
:
:
:
class User(AbstractBaseUser, PermissionsMixin):
    :
    :
    avatar = models.FileField(
        upload_to=save_user_avatar,
        verbose_name=_('Profile Image'),
        null=True,
        blank=True,
    )
    :
    :
```

`save_user_avatar` returns `custom_save_file`’s return value. Default
configuration of for `custom_save_file` is 
`save_file(instance, filename, upload_to='upload/%Y/%m/%d/')`. Uploads are go to
such as `MEDIA_ROOT/upload/2017/09/21/`...

Make your custom uploads like:

```python
from baseapp.utils import save_file as custom_save_file

def my_custom_uploader(instance, filename):
    # do your stuff
    # at the end, call:
    return custom_save_file(instance, filename, upload_to='images/%Y/')


class MyModel(models.Model):
    image = models.FileField(
        upload_to='my_custom_uploader',
        verbose_name=_('Profile Image'),
    )

```

## `AdminImageFileWidget`

Use this widget in your admin forms:

```python
from baseapp.widgets import AdminImageFileWidget

class MyAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.FileField: {'widget': AdminImageFileWidget},
    }

```

This widget uses `Pillow` (*Python Image Library*) which ships with your `base.pip`
requirements file. Show image preview, width x height if the file is image.

---

## Rakefile

If you have Ruby installed, you’ll have lots of handy tasks for the project.
Type `rake -T` for list of tasks:

```bash
$ rake -T
rake db:migrate[database]                                        # Run migration for given database (default: 'default')
rake db:roll_back[name_of_application,name_of_migration]         # Roll-back (name of application, name of migration)
rake db:shell                                                    # run database shell ..
rake db:show[name_of_application]                                # Show migrations for an application (default: 'all')
rake db:update[name_of_application,name_of_migration,is_empty]   # Update migration (name of application, name of migration?, is empty?)
rake locale:compile                                              # Compile locale dictionary
rake locale:update                                               # Update locale dictionary
rake new:application[name_of_application]                        # Create new Django application
rake new:model[name_of_application,name_of_model,type_of_model]  # Create new Model for given application
rake run_server                                                  # Run server
rake shell                                                       # Run shell+
rake test:baseapp                                                # Run test against baseapp
```

Default task is `run_server`. Just type `rake` that’s it! `runserver` uses
`runserver_plus`. This means you have lots of debugging options!

### `rake db:migrate[database]`

Migrates database with given database name. Default is `default`. If you like
to work multiple databases:

```python
# config/settings/development.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db', 'development.sqlite3'),
    },
    'my_database': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db', 'my_database.sqlite3'),
    }
}
```

You can just call `rake db:migrate` or specify different database like: 
`rake db:migrate[my_database]` :)

### `rake db:roll_back[name_of_application,name_of_migration]`

Your database must be rollable :) To see available migrations: 
`rake db:roll_back[NAME_OF_YOUR_APPLICATION]`. Look at the list and choose your
target migration (*example*): `rake db:roll_back[baseapp,0001_create_custom_user]`.

```bash
# example scenario
$ rake db:roll_back[baseapp]
Please select your migration:
baseapp
 [X] 0001_create_custom_user
 [X] 0002_post_model

$ rake db:roll_back[baseapp,0001_create_custom_user]
```

### `rake db:shell`

Runs default database client.

### `rake db:show[name_of_application]`

Show migrations. Examples:

```bash
$ rake db:show # shows everything
admin
 [X] 0001_initial
 [X] 0002_logentry_remove_auto_add
auth
 [X] 0001_initial
 [X] 0002_alter_permission_name_max_length
 [X] 0003_alter_user_email_max_length
 [X] 0004_alter_user_username_opts
 [X] 0005_alter_user_last_login_null
 [X] 0006_require_contenttypes_0002
 [X] 0007_alter_validators_add_error_messages
 [X] 0008_alter_user_username_max_length
baseapp
 [X] 0001_create_custom_user
blog
 [X] 0001_create_post_and_category
contenttypes
 [X] 0001_initial
 [X] 0002_remove_content_type_name
sessions
 [X] 0001_initial
```

or just a specific app:

```bash
$ rake db:show[blog]
blog
 [X] 0001_create_post_and_category
```

### `rake db:update[name_of_application,name_of_migration,is_empty]`

When you add/change something in the model, you need to create migrations. Use
this task. Let’s say you have added new field to `Post` model in your `blog`
app:

```bash
$ rake db:update[blog]                           # automatic migration (example)
Migrations for 'blog':
  applications/blog/migrations/0003_auto_20170921_1357.py
    - Alter field category on post
    - Alter field title on post

$ rake db:update[blog,add_new_field_to_post]     # migration with name (example)
Migrations for 'blog':
  applications/blog/migrations/0002_add_new_field_to_post.py

$ rake db:update[blog,add_new_field_to_post,yes] # migration with name (example)
Migrations for 'blog':
  applications/blog/migrations/0002_empty_mig.py
```

### `rake locale:compile` and `rake locale:update`

When you make changes in your application related to locales, run: `rake locale:update`.
When you finish editing your `django.po` file, run `rake locale:compile`.

### `rake new:application[name_of_application]`

Creates new application!

```bash
$ rake new:application[blog]
```

### `rake new:model[name_of_application,name_of_model,type_of_model]`

Creates new model! Available model types are: `django` (default), `basemodel`
and `softdelete`.

```bash
$ rake new:model[blog,Post]                # will create model using Django’s `models.Model`
$ rake new:model[blog,Post,basemodel]      # will create model using our `BaseModel`
$ rake new:model[blog,Post,softdelete]     # will create model using our `BaseModelWithSoftDelete`
```

### `rake shell`

Runs Django repl/shell with use `shell_plus` of [django-extensions][01].
 `rake shell`. This loads everything to your shell! Also you can see the
SQL statements while playing in shell.

### `rake test:baseapp`

Runs tests of baseapp!

---

## Tests

```bash
$ DJANGO_ENV=test python manage.py test baseapp -v 2 # or
$ DJANGO_ENV=test python manage.py test baseapp.tests.CustomUserTestCase # single, or
$ rake test:baseapp
```

---

## Notes

If you created models via management command or rake task, you’ll have admin
file automatically and generated against your model type. If you created a model
with `BaseModelWithSoftDelete`, you’ll have `BaseAdminWithSoftDelete` set.

`BaseAdminWithSoftDelete` uses `objects_bm` in `get_queryset` and by default,
you’ll have extra actions and soft delete feature. If you don’t want to use
`objects_bm` manager, you need to override it manually:

```python
# example: blog/admin/post.py

from django.contrib import admin

from baseapp.admin import BaseAdminWithSoftDelete

from ..models import Post


__all__ = [
    'PostAdmin',
]


class PostAdmin(BaseAdminWithSoftDelete):
    # sticky_list_filter = None
    # hide_deleted_at = False
    
    def get_queryset(self, request):
        return self.model.objects.get_queryset()  # this line!


admin.site.register(Post, PostAdmin)

```

---

## Manual Usage

Let’s assume you need a model called: `Page`. Create a file under `YOUR_APP/models/page.py`:

```python
# YOUR_APP/models/page.py

from django.db import models


__all__ = [
    'Page',
]

class Page(models.Model):
    # define your fields here...
    pass

# YOUR_APP/models/__init__.py
# append:
from .page import *

```

Now make migrations etc... Use it as `from YOUR_APP.models import Page` :)

---

## Contributer(s)

* [Uğur "vigo" Özyılmazel](https://github.com/vigo) - Creator, maintainer

---

## Contribute

All PR’s are welcome!

1. `fork` (https://github.com/vigo/django-project-template/fork)
1. Create your `branch` (`git checkout -b my-features`)
1. `commit` yours (`git commit -am 'added killer options'`)
1. `push` your `branch` (`git push origin my-features`)
1. Than create a new **Pull Request**!

---

## License

This project is licensed under MIT

---

## Change Log

**2017-10-02**

- Added: `created_at` and `updated_at` fields to custom User model.

[01]: https://github.com/django-extensions/django-extensions "Django Extensions"
[02]: https://django-debug-toolbar.readthedocs.io/en/stable/ "Django Debug Toolbar"
[03]: http://werkzeug.pocoo.org "Werkzeug"