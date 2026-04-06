from odoo import http
from odoo.http import request
import requests

class QuickbookController(http.Controller):

    @http.route('/quickbook/connect', type='http', auth='user')
    def connect(self):
        config = request.env['quickbook.config'].sudo().search([], limit=1)

        url = f"https://appcenter.intuit.com/connect/oauth2?" \
              f"client_id={config.client_id}&" \
              f"redirect_uri={config.redirect_uri}&" \
              f"response_type=code&" \
              f"scope=com.intuit.quickbooks.accounting"
        res = request.redirect(url)
        print(f'data---------------',res)
        return res


    @http.route('/quickbook/callback', type='http', auth='public')
    def callback(self, **kwargs):
        print(f'callback hit---------------',kwargs)
        code = kwargs.get('code')
        realm_id = kwargs.get('realmId')
        config = request.env['quickbook.config'].sudo().search([], limit=1)
        token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        response = requests.post(token_url,
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
        print(f'data----45-----------',data)
        config.write({
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'realm_id': realm_id,
            'status': 'connected',

        })
        return "Connected Successfully"