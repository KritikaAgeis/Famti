from odoo import models, fields
import requests
from odoo.http import request
from odoo import http


class QuickbookConfig(models.Model):
    _name = 'quickbook.config'
    _description = 'quickbook.config'

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

    def ensure_valid_token(self):
        self.ensure_one()
        if not self.access_token:
            raise Exception("QuickBooks not connected")
        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{self.realm_id}/companyinfo/{self.realm_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            self.refresh_access_token()

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

    # ------------------------
    # ITEM
    # ------------------------
    def get_or_create_item(self, name):
        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{self.realm_id}/query"
        headers_query = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/text"
        }
        query = f"SELECT * FROM Item WHERE Name = '{name}'"
        res = requests.post(url, headers=headers_query, data=query)
        data = res.json()
        items = data.get('QueryResponse', {}).get('Item', [])
        if items:
            return items[0]['Id']
        create_url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{self.realm_id}/item"
        headers_create = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "Name": name,
            "Type": "Service",
            "IncomeAccountRef": {"value": "79"},
            "Taxable": True
        }
        res = requests.post(create_url, headers=headers_create, json=payload)
        #print("QB CREATE ITEM RESPONSE:", res.text)
        data = res.json()
        if 'Item' not in data:
            raise Exception(f"Item creation failed: {data}")
        return data['Item']['Id']


    def get_or_create_customer(self, partner):
        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{self.realm_id}/query"
        headers_query = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/text"
        }
        name = partner.name.replace("'", "")
        query = f"SELECT * FROM Customer WHERE DisplayName = '{name}'"
        res = requests.post(url, headers=headers_query, data=query)
        data = res.json()
        customers = data.get('QueryResponse', {}).get('Customer', [])
        if customers:
            return customers[0]['Id']

        # CREATE CUSTOMER WITH FULL DATA IN QUICKBOOKS
        create_url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{self.realm_id}/customer"
        headers_create = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "DisplayName": name,
            "PrimaryEmailAddr": {
                "Address": partner.email or "test@example.com"
            },
            "PrimaryPhone": {
                "FreeFormNumber": partner.phone or ""
            },
            "BillAddr": {
                "Line1": partner.street or "",
                "City": partner.city or "",
                "PostalCode": partner.zip or "",
                "CountrySubDivisionCode": partner.state_id.code if partner.state_id else "",
                "Country": partner.country_id.name if partner.country_id else ""
            }
        }
        res = requests.post(create_url, headers=headers_create, json=payload)
        data = res.json()
        if 'Customer' not in data:
            raise Exception(f"Customer creation failed: {data}")
        return data['Customer']['Id']

    def qb_request(self, method, url, headers, **kwargs):
        try:
            res = requests.request(method, url, headers=headers, timeout=30, **kwargs)
            if res.status_code not in (200, 201):
                raise Exception(f"QB API Error {res.status_code}: {res.text}")
            return res.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"QB Request Failed: {str(e)}")


    def get_qb_invoice(self, doc_number):
        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{self.realm_id}/query"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/text"
        }
        query = f"SELECT * FROM Invoice WHERE DocNumber = '{doc_number}'"
        data = self.qb_request("POST", url, headers, data=query)
        invoices = data.get('QueryResponse', {}).get('Invoice', [])
        return invoices[0] if invoices else None

    def _get_qb_tax_code(self, tax):
        """
        Return QuickBooks TaxCodeRef value
        """
        if not tax:
            return "NON"

        if tax.qb_tax_code:
            return tax.qb_tax_code

        if tax.amount > 0:
            return "TAX"

        return "NON"


    def _prepare_qb_invoice_lines(self, invoice):
        lines = []
        for line in invoice.invoice_line_ids:
            item_id = self.get_or_create_item(line.product_id.name)
            tax = line.tax_ids[:1]
            tax_code = self._get_qb_tax_code(tax)
            lines.append({
                "DetailType": "SalesItemLineDetail",
                "Amount": line.price_subtotal,
                "Description": line.name,
                "SalesItemLineDetail": {
                    "ItemRef": {"value": item_id},
                    "Qty": line.quantity,
                    "UnitPrice": line.price_unit,
                    "TaxCodeRef": {
                        "value": tax_code
                    }
                }
            })

        return lines

    def create_or_update_qb_invoice(self, invoice):
        self.ensure_valid_token()
        self.ensure_one()

        customer_id = self.get_or_create_customer(invoice.partner_id)
        existing_invoice = self.get_qb_invoice(invoice.name)

        lines = self._prepare_qb_invoice_lines(invoice)

        payload = {
            "Line": lines,
            "CustomerRef": {
                "value": customer_id,
                "name": invoice.partner_id.name
            },
            "TxnDate": str(invoice.invoice_date),
            "DueDate": str(invoice.invoice_date_due or invoice.invoice_date),
            "DocNumber": invoice.name,

            "BillAddr": {
                "Line1": invoice.partner_id.street or "",
                "City": invoice.partner_id.city or "",
                "PostalCode": invoice.partner_id.zip or ""
            },

            "ShipAddr": {
                "Line1": invoice.partner_shipping_id.street or "",
                "City": invoice.partner_shipping_id.city or "",
                "PostalCode": invoice.partner_shipping_id.zip or ""
            }
        }

        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{self.realm_id}/invoice"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # UPDATE
        if existing_invoice:
            balance = float(existing_invoice.get("Balance", 0))

            #Don't update paid invoice of quickbooks
            if balance == 0:
                #print("Invoice already paid → skipping update")
                return existing_invoice

            payload.update({
                "Id": existing_invoice["Id"],
                "SyncToken": existing_invoice["SyncToken"],
                "sparse": True
            })

            #print("Updating invoice in QB...")
            res = requests.post(url, headers=headers, json=payload)

        #CREATE
        else:
            #print("Creating invoice in QB...")
            res = requests.post(url, headers=headers, json=payload)

        #print("QB RESPONSE:", res.text)

        if res.status_code not in (200, 201):
            raise Exception(f"QB API Error {res.status_code}: {res.text}")

        data = res.json()

        if 'Invoice' not in data:
            raise Exception(f"Invoice failed: {data}")

        return data['Invoice']



    def fetch_invoices(self):
        self.ensure_one()
        self.ensure_valid_token()
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
        #print("Invoices fetched:", len(invoices))
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
            #print(f"Updating invoice QB ID: {qb_id}")
            existing_invoice.write(vals)
        else:
            #print(f"Creating invoice QB ID: {qb_id}")
            self.env['account.move'].create(vals)


