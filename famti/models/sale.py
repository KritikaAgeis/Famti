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

    partner_lc_document = fields.Binary(
        related='partner_id.lc_document',
        readonly=True
    )

    customer_email = fields.Char(string="Email")
    customer_phone = fields.Char(string="Contact")

    so_type = fields.Selection([
        ('sample', 'Sample'),
        ('normal', 'Normal'),
        ('tolling', 'Tolling'),
        ('fgf', 'FGF'),
    ], string='SO Type', tracking=True, default='sample')



    @api.depends('partner_id')
    def _compute_partner_credit_info(self):
        for order in self:
            partner = order.partner_id
            order.partner_credit_limit = partner.credit_limit or 0.0
            order.partner_outstanding = partner.credit or 0.0
            order.partner_lc_document = partner.lc_document or False


    def _get_unpaid_invoices(self):
        self.ensure_one()
        return self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.company_id.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
        ])

    def _check_credit_and_overdue(self):
        self.ensure_one()
        partner = self.partner_id

        unpaid_invoices = self._get_unpaid_invoices()
        outstanding = sum(unpaid_invoices.mapped('amount_residual'))
        if partner.credit_limit and outstanding + self.amount_total > partner.credit_limit:
            return (
                f"The customer's credit limit of {partner.credit_limit} has been exceeded."
                f"The current outstanding amount is {outstanding},"
                f"and the value of this sales order is {self.amount_total}."
            )

        today = date.today()
        for inv in unpaid_invoices:
            if inv.invoice_date_due < today:
                overdue_days = (today - inv.invoice_date_due).days
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
                if not order.order_line:
                    raise UserError("Sales Order must have at least one order line.")
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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    description = fields.Text(string="Product Description")
    remarks = fields.Text(string="Remarks")

    treatment_in = fields.Selection([
        ('corona', 'Corona'),
        ('met_corona', 'Met on Corona'),
        ('met_chemical', 'Met on Chemical'),
        ('met_plain', 'Met on Plain'),
        ('plain', 'Plain'),
        ('pvdc', 'PVDC COATED'),
        ('soft_touch', 'SOFT TOUCH'),
        ('alox', 'Top coat Alox'),
    ], string="Treatment IN")

    treatment_out = fields.Selection([
        ('acrylic', 'ACRYLIC'),
        ('corona', 'Corona'),
        ('met_plain', 'Met on Plain'),
        ('met_corona', 'Met on Corona'),
        ('met_corona_out', 'Metallized on Corona Outside'),
        ('met_chemical', 'Metallized on Chemical'),
        ('plain', 'Plain'),
        ('pvdc_out', 'PVDC COATED'),
    ], string="Treatment OUT")

    thickness_val = fields.Float(string="Thickness",help="This helps to categorise specific product.")
    thickness_uom = fields.Selection(selection=[('guage','Guage'),('micron','Micron'),('mm','MM'),('mil','Mil')],default='micron',string=" ")
    width_val = fields.Float(string="Width",help="This helps to categorise specific product.")
    width_uom = fields.Selection(selection=[('mm','MM'),('inch','Inch'),('mm','MM'),('mil','Mil')],default='mm',string=" ")
    core_id = fields.Selection(selection=[('3','3 Inch'),('6','6 Inch')],string="Core")
    length_val = fields.Float(string="Length", help="Product Length")
    length_uom = fields.Selection(selection=[('m','M'),('feet','Feet')],default='feet',string=" ")
    pieces = fields.Float(string="Pieces")