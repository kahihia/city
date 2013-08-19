from fabric.api import run
from fabric.state import env
from fabric.context_managers import cd
from fabric.operations import local

env.schema_apps = [ 'citi_user', 'home', 'event' ]
env.local_settings_file = 'alpha.settings'


def dev():
    env.hosts = ['root@dev.cityfusion.ca']
    env.project_folder = '/root/cityfusion_git'
    env.alpha_folder = '/root/cityfusion_git/alpha'
    env.settings_file = 'alpha.settings_prod'

def host_type():
    run('uname -a')

def django_admin(cmd):
    return ". venv/bin/activate; django-admin.py %s --settings=%s --pythonpath=." % (cmd, env.settings_file)

def django_admin_local(cmd):
    return ". venv/bin/activate; django-admin.py %s --settings=%s --pythonpath=." % (cmd, env.local_settings_file)


def upgrade():
    with cd(env.project_folder):
        run("git pull origin master")

    with cd(env.alpha_folder):
        run("python manage.py collectstatic")
        run("supervisorctl reload")

def make_virtualenv():
    local("virtualenv --no-site-packages venv")
    update_virtualenv()

def update_virtualenv():
    local("source venv/bin/activate; pip install -r requirements.txt")


def pip_freeze():
    local("source venv/bin/activate; pip freeze > requirements.txt")

def echo_shell():
    print env.shell

def test():
    local(django_admin("test event home citi_user"), capture=False)