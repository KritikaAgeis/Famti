from odoo import models, fields, api
from odoo.exceptions import UserError


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



    def action_cfo_approval(self):
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
