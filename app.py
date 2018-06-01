"""
    This code is released under an MIT license
"""
# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
from esipy import App
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.exceptions import APIException

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

import config
import hashlib
import hmac
import logging
import random
import time

from danger_systems import find_danger_systems

# logger stuff
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)

# init app and load conf
app = Flask(__name__)
app.config.from_object(config)

# init db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# init flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# -----------------------------------------------------------------------
# Database models
# -----------------------------------------------------------------------
class User(db.Model, UserMixin):
    # our ID is the character ID from EVE API
    character_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=False
    )
    character_owner_hash = db.Column(db.String(255))
    character_name = db.Column(db.String(200))

    # SSO Token stuff
    access_token = db.Column(db.String(100))
    access_token_expires = db.Column(db.DateTime())
    refresh_token = db.Column(db.String(100))

    def get_id(self):
        """ Required for flask-login """
        return self.character_id

    def get_sso_data(self):
        """ Little "helper" function to get formated data for esipy security
        """
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': (
                self.access_token_expires - datetime.utcnow()
            ).total_seconds()
        }

    def update_token(self, token_response):
        """ helper function to update token data from SSO response """
        self.access_token = token_response['access_token']
        self.access_token_expires = datetime.fromtimestamp(
            time.time() + token_response['expires_in'],
        )
        if 'refresh_token' in token_response:
            self.refresh_token = token_response['refresh_token']


# -----------------------------------------------------------------------
# Flask Login requirements
# -----------------------------------------------------------------------
@login_manager.user_loader
def load_user(character_id):
    """ Required user loader for Flask-Login """
    return User.query.get(character_id)


# -----------------------------------------------------------------------
# ESIPY Init
# -----------------------------------------------------------------------
# create the app
esiapp = App.create(config.ESI_SWAGGER_JSON)

# init the security object
esisecurity = EsiSecurity(
    app=esiapp,
    redirect_uri=config.ESI_CALLBACK,
    client_id=config.ESI_CLIENT_ID,
    secret_key=config.ESI_SECRET_KEY,
)

# init the client
esiclient = EsiClient(
    security=esisecurity,
    cache=None,
    headers={'User-Agent': config.ESI_USER_AGENT}
)


# -----------------------------------------------------------------------
# Login / Logout Routes
# -----------------------------------------------------------------------
def generate_token():
    """Generates a non-guessable OAuth token"""
    chars = ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    rand = random.SystemRandom()
    random_string = ''.join(rand.choice(chars) for _ in range(40))
    return hmac.new(
        config.SECRET_KEY.encode('utf-8'),
        random_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


@app.route('/sso/login')
def login():
    """ this redirects the user to the EVE SSO login """
    token = generate_token()
    session['token'] = token
    return redirect(esisecurity.get_auth_uri(
        scopes=['esi-location.read_location.v1', 'publicData'],
        state=token,
    ))


@app.route('/sso/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/sso/callback')
def callback():
    """ This is where the user comes after he logged in SSO """
    # get the code from the login process
    code = request.args.get('code')
    token = request.args.get('state')

    # compare the state with the saved token for CSRF check
    sess_token = session.pop('token', None)
    if sess_token is None or token is None or token != sess_token:
        return 'Login EVE Online SSO failed: Session Token Mismatch', 403

    # now we try to get tokens
    try:
        auth_response = esisecurity.auth(code)
    except APIException as e:
        return 'Login EVE Online SSO failed: %s' % e, 403

    # we get the character informations
    cdata = esisecurity.verify()

    # if the user is already authed, we log him out
    if current_user.is_authenticated:
        logout_user()

    # now we check in database, if the user exists
    # actually we'd have to also check with character_owner_hash, to be
    # sure the owner is still the same, but that's an example only...
    try:
        user = User.query.filter(
            User.character_id == cdata['CharacterID'],
        ).one()

    except NoResultFound:
        user = User()
        user.character_id = cdata['CharacterID']

    user.character_owner_hash = cdata['CharacterOwnerHash']
    user.character_name = cdata['CharacterName']
    user.update_token(auth_response)

    # now the user is ready, so update/create it and log the user
    try:
        db.session.merge(user)
        db.session.commit()

        login_user(user)
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=3)
    except:
        logger.exception("Cannot login the user - uid: %d" % user.character_id)
        db.session.rollback()
        logout_user()


    return redirect(url_for("index"))


# -----------------------------------------------------------------------
# Index Routes
# -----------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    num_of_kills = 0
    current_char_location = None
    num_of_jumps = None
    hours = None
    character_id = None
    systems_with_kill = None


    if current_user.is_authenticated:
        # give the token data to esisecurity, it will check alone
        # if the access token need some update
        esisecurity.update_token(current_user.get_sso_data())

        op = esiapp.op['get_characters_character_id_location'](
            character_id=current_user.character_id
        )

        char_location = esiclient.request(op).data

        char_system_info_req = esiapp.op['get_universe_systems_system_id'](system_id=char_location['solar_system_id'])
        char_system_info = esiclient.request(char_system_info_req).data
        character_id = current_user.character_id

        if request.method == 'POST':
            # Change settings
            if 'update_info' in request.form:
                num_of_jumps = request.form['num_of_jumps']
                if num_of_jumps:
                    session['num_of_jumps'] = num_of_jumps
                hours = request.form['hours']
                if hours:
                    session['hours'] = hours

        if 'num_of_jumps' not in session:
            session['num_of_jumps'] = '1'
        num_of_jumps = session['num_of_jumps']

        if 'hours' not in session:
            session['hours'] = '1'
        hours = session['hours']

        if request.method == 'POST':
            # Find the danger systems
            if 'run_app' in request.form:
                char_location = char_system_info['system_id']
                systems_with_kill = find_danger_systems(char_location=str(char_location), num_jumps=int(num_of_jumps), hours=int(hours))
        current_char_location = char_system_info['name']
        if systems_with_kill:
            num_of_kills = systems_with_kill.__len__()
    return render_template('base.html', **{
        'char_location': current_char_location,
        'char_avatar_url': 'https://image.eveonline.com/Character/' + str(character_id) + '_256.jpg',
        'num_of_jumps': num_of_jumps,
        'hours': hours,
        'systems_with_kill': systems_with_kill,
        'num_of_kills': num_of_kills
    })


if __name__ == '__main__':
    app.run(port=config.PORT, host=config.HOST)

