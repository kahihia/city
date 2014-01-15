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
    env.password = "123forfusion"
    env.branch = "master"

def prod():
    env.hosts = ['root@cityfusion.ca']
    env.project_folder = '/root/cityfusion_git'
    env.alpha_folder = '/root/cityfusion_git/alpha'
    env.password = "123forfusion"
    env.branch = "prod"


def host_type():
    run('uname -a')

def init_virtual_env():
    run("source /root/virtualenvs/cityfusion_env/bin/activate")

def upgrade():
    init_virtual_env()
    with cd(env.project_folder):
        run("git pull origin %s" % env.branch)        

    with cd(env.alpha_folder):
        run("python manage.py collectassets")
        run("python manage.py collectstatic --noinput")
        run("supervisorctl reload")

def install_requirements():
    init_virtual_env()
    with cd(env.project_folder):
        run("pip install -r requirements.txt")

def migrate(app):
    init_virtual_env()

    with cd(env.project_folder):
        run("git pull origin %s" % env.branch)

    with cd(env.alpha_folder):
        run("python manage.py migrate %s" % app)


def make_virtualenv():
    local("virtualenv --no-site-packages venv")
    update_virtualenv()

def update_virtualenv():
    local("source venv/bin/activate; pip install -r requirements.txt")


def pip_freeze():
    local("source venv/bin/activate; pip freeze > requirements.txt")

def echo_shell():
    print env.shell

def install_geoip():
    run("apt-get install geoip-bin")
    run("""
cat > /etc/GeoIP.conf << EOF
# GeoIP.conf file - used by geoipupdate program
# to update databases from http://www.maxmind.com
# UserId, LicenseKey, ProductIds from rpierce@verticalseven.com account
UserId 77474
LicenseKey q4XOEIJMFdId
ProductIds 132ca
EOF
    """)
    run("""crontab -l | { cat; echo "0 12 * * 3 geoipupdate"; } | crontab -""")
    run("geoipupdate")
    with cd(env.alpha_folder):
        run("rm geoip/*")
        run("ln -s /usr/share/GeoIP/GeoIPCityca.dat GeoIPCityca.dat")
        run("ln -s /usr/share/GeoIP/GeoIP.dat GeoIP.dat")

