from fabric.api import run
from fabric.state import env
from fabric.context_managers import cd
from fabric.operations import run, local, sudo, _handle_failure

def dev():
    env.hosts = ['cityfusion@cityfusion.dev.peakxp.com']
    env.hg_directory = '/home/cityfusion/devsite/cityfusion'
    env.wsgi_filename = 'djangodev.wsgi'

#def production():
#    env.hosts = ['circulate@cityfusion.ca']
#    env.hg_directory = '/home/circulate/prodsite/circulate'
#    env.wsgi_filename = 'django.wsgi'

def host_type():
    run('uname -a')

def django_admin(cmd):
    return ". venv/bin/activate; cd cityfusion; python manage.py %s" % (cmd)

def check_schema(app):
    return local(
        django_admin("schemamigration %s --auto" % (app,)), 
        capture=False)
    
def schemas():
    orig = env.warn_only
    env.warn_only = True

    res = check_schema("gb_profile")

    env.warn_only = orig

def committed():
    output = local("hg st")
    if output:
        _handle_failure("Found uncommitted mercurial files")

def update():
    schemas()
    committed()
    local("hg push")

    with cd(env.hg_directory):
        run("hg pull")
        run("hg update")
        run("source venv/bin/activate; pip install -r requirements.txt")
        run(django_admin("syncdb --noinput"))
        run(django_admin("migrate"))
        run(django_admin("collectstatic --noinput"))
        run("touch bin/" + env.wsgi_filename)

def make_virtualenv():
    local("virtualenv --no-site-packages venv")
    update_virtualenv()

def update_virtualenv():
    local("source venv/bin/activate; pip install -r requirements.txt")


def pip_freeze():
    local("source venv/bin/activate; pip freeze > requirements.txt")

def echo_shell():
    print env.shell
