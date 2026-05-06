[1mdiff --git a/famti/controllers/main.py b/famti/controllers/main.py[m
[1mindex eb93cc0..92f1512 100644[m
[1m--- a/famti/controllers/main.py[m
[1m+++ b/famti/controllers/main.py[m
[36m@@ -1,31 +1,37 @@[m
 from odoo import http[m
 from odoo.http import request[m
 import requests[m
[32m+[m[32mimport uuid[m
[32m+[m[32mfrom werkzeug.utils import redirect[m
 [m
 class QuickbookController(http.Controller):[m
 [m
     @http.route('/quickbook/connect', type='http', auth='user')[m
     def connect(self):[m
         config = request.env['quickbook.config'].sudo().search([], limit=1)[m
[32m+[m[32m        state = str(uuid.uuid4())[m
 [m
[31m-        url = f"https://appcenter.intuit.com/connect/oauth2?" \[m
[31m-              f"client_id={config.client_id}&" \[m
[31m-              f"redirect_uri={config.redirect_uri}&" \[m
[31m-              f"response_type=code&" \[m
[31m-              f"scope=com.intuit.quickbooks.accounting"[m
[31m-        res = request.redirect(url)[m
[31m-        print(f'data---------------',res)[m
[31m-        return res[m
[31m-[m
[32m+[m[32m        url = ([m
[32m+[m[32m            "https://appcenter.intuit.com/connect/oauth2?"[m
[32m+[m[32m            f"client_id={config.client_id}&"[m
[32m+[m[32m            f"redirect_uri={config.redirect_uri}&"[m
[32m+[m[32m            f"response_type=code&"[m
[32m+[m[32m            f"scope=com.intuit.quickbooks.accounting&"[m
[32m+[m[32m            f"state={state}"[m
[32m+[m[32m        )[m
[32m+[m[32m        print(f"url=========={url}")[m
[32m+[m[32m        return request.redirect(url)[m
 [m
     @http.route('/quickbook/callback', type='http', auth='public')[m
     def callback(self, **kwargs):[m
[31m-        print(f'callback hit---------------',kwargs)[m
         code = kwargs.get('code')[m
         realm_id = kwargs.get('realmId')[m
[32m+[m
         config = request.env['quickbook.config'].sudo().search([], limit=1)[m
[31m-        token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"[m
[31m-        response = requests.post(token_url,[m
[32m+[m[32m        print(f'callback hit---------------',kwargs)[m
[32m+[m
[32m+[m[32m        response = requests.post([m
[32m+[m[32m            "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",[m
             headers={[m
                 "Accept": "application/json",[m
                 "Content-Type": "application/x-www-form-urlencoded"[m
[36m@@ -37,13 +43,12 @@[m [mclass QuickbookController(http.Controller):[m
                 "redirect_uri": config.redirect_uri[m
             }[m
         )[m
[32m+[m[32m        print(f'data---------------',response)[m
         data = response.json()[m
[31m-        print(f'data----45-----------',data)[m
         config.write({[m
             'access_token': data.get('access_token'),[m
             'refresh_token': data.get('refresh_token'),[m
             'realm_id': realm_id,[m
[31m-            'status': 'connected',[m
[31m-[m
         })[m
[31m-        return "Connected Successfully"[m
\ No newline at end of file[m
[32m+[m[32m        return "Connected Successfully"[m
[41m+[m
