from odoo import models, fields
import requests

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
            # 'url': '/quickbook/connect',
            'url': f'/quickbook/connect?config_id={self.id}',
            'target': 'self',
        }


    def fetch_invoices(self):
        config = self.search([], limit=1)

        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{config.realm_id}/query"
        print("URL:", url)

        query = "select * from Invoice"

        headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, params={'query': query})
        data = response.json()
        invoices = data.get('QueryResponse', {}).get('Invoice', [])
        for inv in invoices:
            self._create_odoo_invoice(inv)



    def _create_odoo_invoice(self, inv):
        partner = self.env['res.partner'].search(
            [('name', '=', inv['CustomerRef']['name'])],
            limit=1
        )
        if not partner:
            partner = self.env['res.partner'].create({
                'name': inv['CustomerRef']['name']
            })
        lines = []
        for line in inv.get('Line', []):
            if line.get('Amount'):
                lines.append((0, 0, {
                    'name': line.get('Description', ''),
                    'quantity': 1,
                    'price_unit': line['Amount']
                }))

        self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': lines
        })


