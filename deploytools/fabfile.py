import random
import subprocess
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run

def deploy():
    completedProcess = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True)
    repo_url = completedProcess.stdout.strip()
    site_folder = f'/home/{env.user}/websites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _get_latest_source(repo_url.decode("utf-8"))
        _update_virtualenv()
        _create_or_update_dotenv()
        _update_database()

def _get_latest_source(repo_url):
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {repo_url} .')

    current_commit = local('git log -n l --format=%H', capture=True)
    run(f'git reset --hard {current_commit}')

def _update_virtualenv():
    if not exists('virtualenv/bin/pip'):
        run(f'python3.6 -m venv virtualenv')
        run('./virtualenv/bin/pip install -r requirements.txt')

def _create_or_update_dotenv():
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choice('abcdefghlmnopqrstuvwxyz0123456789', k=50))
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')

def _update_static_files():
    run('./virtualenv/bin/python manage.py collectstatic --noinput')

def _update_databse():
    run('./virtualenv/bin/python manage.py migrate --noinput')