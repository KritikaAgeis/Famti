from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_bank_payment_html(self):
        bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if not bank_journal or not bank_journal.bank_account_id:
            return ""

        bank = bank_journal.bank_account_id.bank_id

        return f"""
            <p><strong>Payment Method:</strong></p>

            <p>
            1. Wire Transfer:<br/>
            {self.env.company.name} BANKING DETAILS<br/>
            BANK NAME: {bank.name}<br/>
            ACCOUNT NO.: {bank_journal.bank_account_id.acc_number}<br/>
            TRANSIT NO.: {bank_journal.bank_account_id.transit_no or ''}<br/>
            INST. NO.: {bank_journal.bank_account_id.institution_no or ''}
            </p>

            <p>
            2. By Cheque:<br/>
            Please make a cheque payment to {self.env.company.name}
            and kindly mention invoice number.
            </p>
            """

    @api.model
    def create(self, vals):
        if vals.get('move_type') == 'out_invoice':
            vals['narration'] = self._get_bank_payment_html()

        return super().create(vals)