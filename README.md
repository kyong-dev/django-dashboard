# Django Server Boilerplate

This boilerplate project simplifies the initiation of web applications using Django 5.0.3, with integrations for AWS services, environment variable management, uWSGI, Nginx, and PostgreSQL.

## Features

- **Django 5.1.2**: High-level Python Web framework.
- **Django Swagger**: Interactive API documentation.
- **AWS Services**: S3, EC2, Lambda, CloudWatch Logs, and IAM.
- **.env**: Secure environment variable management.
- **uWSGI**: Application server interfacing with Nginx.
- **Nginx**: Reverse proxy for uWSGI.
- **PostgreSQL**: Powerful, open-source database system.
- **BLACK**: Code Formatter.

## Getting Started

### Prerequisites

- Python 3.11+
- Pip and virtualenv
- AWS CLI configured
- PostgreSQL installed

### Installation

Clone the repository and set up the environment:

```bash
git clone https://github.com/siimtech/django-dashboard.git
cd django-dashboard
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure environment variables using `.env`.

### Running the Project

Apply database migrations and run the server:

```bash
python manage.py migrate
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000`.

### API Documentation

- **Swagger**: `http://your-domain/swagger/`
- **Django Ninja**: `http://your-domain/api/docs/`

## Contributing

Submit pull requests or open issues for improvements or bug fixes.

## Testing

Run tests and generate a coverage report:

```bash
python manage.py test
coverage run --source='.' manage.py test
coverage html
```

View the report in `htmlcov/index.html`.

## Code Quality and Linting

### Black

Install and format code using Black:

```bash
pip install black
black .
```

### Pip Upgrader

Upgrade all packages at once

```bash
pip install pip-upgrader
pip-upgrade requirements.txt
```

```bash
Available upgrades:
+------+-----------------+-----------------+----------------+---------------------+
| No.  | Package         | Current version | Latest version | Release date        |
+------+-----------------+-----------------+----------------+---------------------+
|  1   |  bcrypt         | 4.2.0           | 4.2.1          | 2024-11-19 20:07:21 |
|  2   |  boto3          | 1.35.54         | 1.35.77        | 2024-12-09 20:46:19 |
|  3   |  botocore       | 1.35.54         | 1.35.77        | 2024-12-09 20:46:02 |
|  4   |  cryptography   | 43.0.3          | 44.0.0         | 2024-11-27 18:05:55 |
|  5   |  django         | 5.1.2           | 5.1.4          | 2024-12-04 15:09:01 |
|  6   |  django-unfold  | 0.40.0          | 0.43.0         | 2024-12-09 15:55:39 |
|  7   |  packaging      | 24.1            | 24.2           | 2024-11-08 09:47:44 |
|  8   |  s3transfer     | 0.10.3          | 0.10.4         | 2024-11-20 21:06:03 |
|  9   |  six            | 1.16.0          | 1.17.0         | 2024-12-04 17:35:26 |
|  10  |  sqlparse       | 0.5.1           | 0.5.2          | 2024-11-14 10:06:25 |
+------+-----------------+-----------------+----------------+---------------------+
```

### Django Debug Toolbar

How to set up Django Debug Toolbar in your Django project.

```bash
pip install django-debug-toolbar
```

settings.py
```python
INSTALLED_APPS = [
    # ... other installed apps in settings.py...
    'debug_toolbar',
]
# ...

MIDDLEWARE = [
    # ... other middlewares in settings.py...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# ...
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
```

urls.py
```python
from django.conf import settings
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    # other URLs...
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

```bash
python manage.py collectstatic
```


### ER Diagram

Install and Generate ER Diagram using pydotplus:

```python
INSTALLED_APPS = [
    # ... other installed apps in settings.py...
    'django_extensions',
]
```

```bash
pip install django-extensions
pip install pydotplus 

python manage.py graph_models -a -g -o er_diagram.png
```


## Security Best Practices

### Managing Environment Variables

Use environment variables for sensitive data, and do not commit `.env` files to version control.

### Updating Dependencies

Regularly update dependencies:

```bash
pip install --upgrade -r requirements.txt
```

### Django Security Middleware

Include the following in `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # other middleware...
]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Using HTTPS

Always use HTTPS. Use Let's Encrypt for SSL/TLS certificates.

## Monitoring and Logging

### AWS CloudWatch Logs

Configure Django to send logs to CloudWatch:

1. Install `watchtower`:

    ```bash
    pip install watchtower
    ```

2. Update the logging configuration in `settings.py`:

    ```python
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'watchtower': {
                'level': 'DEBUG',
                'class': 'watchtower.CloudWatchLogHandler',
                'boto3_session': boto3.Session(),
                'log_group': 'your-log-group',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['watchtower'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }
    ```

## Deployment Instructions

### Setting Up AWS EC2

1. Launch an EC2 instance (e.g., Ubuntu).
2. SSH into your instance:

    ```bash
    ssh -i your-key.pem ubuntu@your-ec2-instance-ip
    ```

3. Install necessary software:

    ```bash
    sudo apt update
    sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
    sudo pip3 install virtualenv
    ```

4. Clone the repository:

    ```bash
    git clone https://github.com/siimtech/django-boilerplate.git
    cd django-boilerplate
    ```

5. Follow the installation instructions.
6. Configure uWSGI and Nginx:
    - `uwsgi.ini`:

        ```ini
        [uwsgi]
        module = yourproject.wsgi:application
        master = true
        processes = 10
        socket = /run/uwsgi/yourproject.sock
        chmod-socket = 660
        vacuum = true
        die-on-term = true
        ```

    - Nginx configuration:

        ```nginx
        server {
            listen 80;
            server_name your-domain.com;

            location / {
                uwsgi_pass unix:/run/uwsgi/yourproject.sock;
                include uwsgi_params;
            }

            location /static/ {
                alias /home/ubuntu/yourproject/static/;
            }

            location /media/ {
                alias /home/ubuntu/yourproject/media/;
            }
        }
        ```

7. Start uWSGI and Nginx:

    ```bash
    sudo systemctl start uwsgi
    sudo systemctl enable uwsgi
    sudo systemctl restart nginx
    ```

8. Secure your deployment with HTTPS:

    ```bash
    sudo apt-get install certbot python3-certbot-nginx
    sudo certbot --nginx -d your-domain.com
    ```

## Troubleshooting

### Common Issues

#### Database Connection Error

- Ensure PostgreSQL is running and accessible.
- Verify `DATABASES` configuration in `settings.py`.

#### Static Files Not Displaying

- Run:

    ```bash
    python manage.py collectstatic
    ```

- Check Nginx configuration.

#### AWS Permissions Issues

- Verify IAM roles and policies.
- Check AWS credentials.

#### Application Fails to Start

- Check EC2 and CloudWatch logs.
- Validate `uwsgi.ini` and Nginx configuration.

With these enhancements, your Django Server Boilerplate is robust and ready for development and deployment scenarios.