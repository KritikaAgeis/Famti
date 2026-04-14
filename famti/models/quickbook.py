from odoo import models, fields
import requests
from odoo.http import request
from odoo import http


class QuickbookConfig(models.Model):
    _name = 'quickbook.config'

    name = fields.Char(default="QuickBooks Config",required=True)
    client_id = fields.Char(string="Client ID",required=True)
    client_secret = fields.Char(string="Client Secret",required=True)
    redirect_uri = fields.Char(string="Redirect URI",required=True)
    realm_id = fields.Char()

    access_token = fields.Text(string="Access Token",)
    refresh_token = fields.Text()
    status = fields.Selection([('draft','Draft'),('connected', 'Connected'),('disconnected', 'Disconnected')],default='draft')


    def action_connect(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/quickbook/connect?config_id={self.id}',
            'target': 'self',
        }

    def is_connected(self):
        if self.status == 'connected' and self.access_token and self.refresh_token:
            return True
        else:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/quickbook/connect?config_id={self.id}',
                'target': 'self',
            }

    def refresh_access_token(self):
        config = self
        TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        response = requests.post(
            TOKEN_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            auth=(config.client_id, config.client_secret),
            data={
                "grant_type": "refresh_token",
                "refresh_token": config.refresh_token
            }
        )
        data = response.json()
        if 'access_token' in data:
            config.write({
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token') or config.refresh_token,
            })
            return 'Successfully Updated Access Token!'
        else:
            raise Exception("Refresh token failed")

    def fetch_invoices(self):
        self.ensure_one()
        self.is_connected()
        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{self.realm_id}/query"
        query = "SELECT * FROM Invoice"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/text"
        }
        response = requests.post(url, headers=headers, data=query)
        data = response.json()
        if self.status == 'connected' and 'fault' in data:
            token_expired = data['fault']['error'][0]['detail']
            if token_expired == 'Token expired':
                resp=self.refresh_access_token()
        invoices = data.get('QueryResponse', {}).get('Invoice', [])
        print("Invoices fetched:", len(invoices))
        for inv in invoices:
            self._create_odoo_invoice(inv)

    def _create_odoo_invoice(self, inv):
        qb_id = inv.get('Id')
        existing_invoice = self.env['account.move'].search(
            [('quickbook_id', '=', qb_id)],
            limit=1
        )
        partner_name = inv.get('CustomerRef', {}).get('name')

        partner = self.env['res.partner'].search(
            [('name', '=', partner_name)],
            limit=1
        )

        if not partner:
            partner = self.env['res.partner'].create({
                'name': partner_name
            })

        lines = []
        for line in inv.get('Line', []):
            if line.get('Amount'):
                lines.append((0, 0, {
                    'name': line.get('Description', ''),
                    'quantity': 1,
                    'price_unit': line.get('Amount')
                }))

        vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': lines,
            'quickbook_id': qb_id,
            'invoice_date': inv.get('TxnDate'),
        }

        if existing_invoice:
            print(f"Updating invoice QB ID: {qb_id}")
            existing_invoice.write(vals)
        else:
            print(f"Creating invoice QB ID: {qb_id}")
            self.env['account.move'].create(vals)


