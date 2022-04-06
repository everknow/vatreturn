import os

from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask_dance.consumer.requests import OAuth2Session
from functools import partial
from flask.globals import LocalProxy, _lookup_app_object

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class HMRCSession(OAuth2Session):
    def __init__(self, *args, **kwargs):
        super(HMRCSession, self).__init__(*args, **kwargs)
        self.headers["ACCEPT"] = "application/vnd.hmrc.1.0+json"
        self.headers["Content-Type"] = "application/json"


def make_hmrc_blueprint(
    api_host=None,
    client_id=None,
    client_secret=None,
    scope=None,
    redirect_url=None,
    redirect_to=None,
    login_url=None,
    authorized_url=None,
    session_class=None,
    storage=None,
):
    """
    Make a blueprint for authenticating with Hmrc using OAuth 2. This requires
    a client ID and client secret from Hmrc. You should either pass them to
    this constructor, or make sure that your Flask application config defines
    them, using the variables HMRC_OAUTH_CLIENT_ID and HMRC_OAUTH_CLIENT_SECRET.

    Args:
        client_id (str): The client ID for your application on Hmrc.
        client_secret (str): The client secret for your application on Hmrc
        scope (str, optional): comma-separated list of scopes for the OAuth token
        redirect_url (str): the URL to redirect to after the authentication
            dance is complete
        redirect_to (str): if ``redirect_url`` is not defined, the name of the
            view to redirect to after the authentication dance is complete.
            The actual URL will be determined by :func:`flask.url_for`
        login_url (str, optional): the URL path for the ``login`` view.
            Defaults to ``/hmrc``
        authorized_url (str, optional): the URL path for the ``authorized`` view.
            Defaults to ``/hmrc/authorized``.
        session_class (class, optional): The class to use for creating a
            Requests session. Defaults to
            :class:`~flask_dance.consumer.requests.OAuth2Session`.
        storage: A token storage class, or an instance of a token storage
                class, to use for this blueprint. Defaults to
                :class:`~flask_dance.consumer.storage.session.SessionStorage`.

    :rtype: :class:`~flask_dance.consumer.OAuth2ConsumerBlueprint`
    :returns: A :ref:`blueprint <flask:blueprints>` to attach to your Flask app.
    """
    hmrc_bp = OAuth2ConsumerBlueprint(
        "hmrc",
        __name__,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        base_url=api_host,
        authorization_url=os.path.join(api_host, "oauth/authorize"),
        token_url=os.path.join(api_host, "oauth/token"),
        auto_refresh_url=os.path.join(api_host, "oauth/token"),
        auto_refresh_kwargs={'client_id': client_id, 'client_secret': client_secret},
        redirect_url=redirect_url,
        redirect_to=redirect_to,
        login_url=login_url,
        authorized_url=authorized_url,
        session_class=session_class or HMRCSession,
        storage=storage,
        token_url_params={'include_client_id': True}
    )
    hmrc_bp.from_config["client_id"] = "HMRC_OAUTH_CLIENT_ID"
    hmrc_bp.from_config["client_secret"] = "HMRC_OAUTH_CLIENT_SECRET"

    @hmrc_bp.before_app_request
    def set_applocal_session():
        ctx = stack.top
        ctx.hmrc_oauth = hmrc_bp.session

    return hmrc_bp


hmrc = LocalProxy(partial(_lookup_app_object, "hmrc_oauth"))
