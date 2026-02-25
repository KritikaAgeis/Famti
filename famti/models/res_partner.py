from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import timedelta


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_supplier = fields.Boolean(string="Supplier")
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)


    iso_vendor_certificate = fields.Binary(string="ISO Vendor Certificate",
        attachment=True
    )
    iso_certificate_name = fields.Char(string="Certificate Name")
    
    vendor_document_expiry = fields.Date(string="Certificate Expiry Date")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified_vendor', 'Certificate Verified'),
        ('certificate_expired', 'Certificate Expired'),
    ], string="Vendor Status", default='draft', tracking=True)

    gst_verified = fields.Boolean(string="GST Verified")

    credit_grace_days = fields.Integer(string="Credit Grace Period (Days)", default=0)
    lc_required = fields.Boolean(string="LC Required")
    lc_document = fields.Binary(string="LC Document")


    def action_iso_certificate_updated(self):
        for rec in self:
            rec.state = 'verified_vendor'

    def action_iso_certificate_renew(self):
        for rec in self:
            rec.state = 'verified_vendor'


    def _cron_vendor_document_expiry_reminder(self):
        today = fields.Date.today()
        last_reminder_day = today + timedelta(days=2)

        vendors = self.search([
            ('is_supplier', '=', True),
            ('vendor_document_expiry', '>=', today),
            ('vendor_document_expiry', '<=', last_reminder_day),
            ('email', '!=', False),
        ])

        template = self.env.ref(
            'famti.mail_template_vendor_document_expiry',
            raise_if_not_found=False
        )

        for vendor in vendors:
            if vendor.vendor_document_expiry == today:
                vendor.write({
                    'state': 'certificate_expired'
                })

            subject = "Vendor Certificate Expiry Reminder"
            body = f"""
                Dear {vendor.name},

                Your certificate will expire on {vendor.vendor_document_expiry}.

                Please renew and share the updated certificate before the expiry date.

                Thank you,
                {self.env.user.company_id.name}
                """
            self.env['mail.mail'].create({
                'subject': subject,
                'body_html': body.replace('\n', '<br/>'),
                'email_to': vendor.email,
            }).send()

    
