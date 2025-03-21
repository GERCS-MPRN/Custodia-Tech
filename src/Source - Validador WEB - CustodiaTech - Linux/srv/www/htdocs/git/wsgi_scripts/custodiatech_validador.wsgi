import sys
import os
os.environ['TURNSTILE_SECRET_KEY'] = os.getenv('TURNSTILE_SECRET_KEY','SECRET_KEY')
os.environ['TURNSTILE_SITEKEY'] = os.getenv('TURNSTILE_SITEKEY', 'SITEKEY')
sys.path.insert(0, '/srv/www/htdocs/git')
from custodiatech_validador import app as application
