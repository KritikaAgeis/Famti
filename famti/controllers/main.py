from odoo import http
from odoo.http import request
import requests
import urllib.parse
from werkzeug.utils import redirect
import urllib.parse

AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"


class QuickbookController(http.Controller):

    @http.route('/quickbook/connect', type='http', auth='user')
    def quickbook_connect(self, **kwargs):

        config_id = kwargs.get('config_id')
        config = request.env['quickbook.config'].sudo().browse(int(config_id))

        if not config.exists():
            return "QuickBooks Configuration Missing!"

        redirect_uri = urllib.parse.quote(config.redirect_uri)

        auth_url = (
            f"{AUTH_URL}?"
            f"client_id={config.client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=com.intuit.quickbooks.accounting&"
            f"state={config.id}"
        )
        print("Redirecting to:", auth_url)

        return redirect(auth_url)


    @http.route('/quickbook/callback', type='http', auth='user')
    def quickbook_callback(self, **kwargs):

        code = kwargs.get('code')
        realm_id = kwargs.get('realmId')
        state = kwargs.get('state')

        if not code:
            return "Error: No code received"

        config = request.env['quickbook.config'].sudo().browse(int(state))

        if not config.exists():
            return "Invalid configuration!"

        response = requests.post(
            TOKEN_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            auth=(config.client_id, config.client_secret),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": config.redirect_uri
            }
        )

        data = response.json()

        config.write({
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'realm_id': realm_id,
            'status': 'connected'
        })

        return """
            <h3>QuickBooks Connected Successfully </h3>
            <p>You can close this window.</p>"""
