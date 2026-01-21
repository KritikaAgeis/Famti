from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('to_approve', 'To Approve'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, tracking=True, default='draft')


    partner_credit_limit = fields.Monetary(
        string="Credit Limit",
        currency_field='currency_id',
        compute="_compute_partner_credit_info",
        store=False
    )

    partner_outstanding = fields.Monetary(
        string="Outstanding Amount",
        currency_field='currency_id',
        compute="_compute_partner_credit_info",
        store=False
    )

    @api.depends('partner_id')
    def _compute_partner_credit_info(self):
        for order in self:
            partner = order.partner_id
            order.partner_credit_limit = partner.credit_limit or 0.0
            order.partner_outstanding = partner.credit or 0.0


    def _get_unpaid_invoices(self):
        self.ensure_one()
        return self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
        ])

    def _check_credit_and_overdue(self):
        self.ensure_one()
        partner = self.partner_id

        unpaid_invoices = self._get_unpaid_invoices()
        outstanding = sum(unpaid_invoices.mapped('amount_residual'))
        print("-------outstanding--------",outstanding)
        if partner.credit_limit and outstanding + self.amount_total > partner.credit_limit:
            return (
                f"The customer's credit limit of {partner.credit_limit} has been exceeded."
                f"The current outstanding amount is {outstanding},"
                f"and the value of this sales order is {self.amount_total}."
            )


        today = date.today()
        print("===========",today)
        for inv in unpaid_invoices:
            print("-------------------",inv.invoice_date_due)
            if inv.invoice_date_due and inv.invoice_date_due < today:
                overdue_days = (today - inv.invoice_date_due).days
                print("====overdue_days===",overdue_days)
                if overdue_days > partner.credit_grace_days:
                    return (
                        f"The customer has overdue invoices beyond the allowed grace period."
                        f"Invoice {inv.name} is overdue by {overdue_days} days."
                    )

        return False
        


    def action_cfo_approval(self):
         for order in self:
            issue = order._check_credit_and_overdue()
            if issue:
                raise UserError(issue)
            else:
                self.write({'state': 'to_approve'})

    def action_approve(self):
        for order in self:
            if order.state == 'to_approve':
                order.write({'state': 'draft'})

            order.action_confirm()


    def action_reject(self):
        return self.action_cancel()

    def action_confirm(self):
        if self.state == 'to_approve' and not self.env.user.has_group(
                'famti.group_cheif_financial_officer'):
            raise UserError("Sale Order requires CFO approval.")
        return super().action_confirm()
