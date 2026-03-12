from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FreightOrder(models.Model):
    _inherit = 'freight.order'
    _description = 'Freight Order'

    purchase_id = fields.Many2one(
        'purchase.order',
        string="Purchase Order"
    )
    
    sale_id = fields.Many2one(
        'sale.order',
        string="Sales Order"
    )
    
    logo = fields.Image("Logo", max_width=1920, max_height=1920, default=lambda self: self.env.company.logo)
    etd = fields.Datetime(string="Estimated Time of Departure")
    bl_number = fields.Char( string="Bill of Lading Number", tracking=True)
    gross_weight = fields.Float(string="Gross Weight")
    net_weight = fields.Float(string="Net Weight")

    


class FreightOrder(models.Model):
    _inherit = 'freight.order.line'
    _description = 'Freight Order Lines'


    purchase_id = fields.Many2one('purchase.order', string="Purchase Order", related='order_id.purchase_id', store=True, readonly=True)   
    sale_id = fields.Many2one('sale.order', string="Sale Order", related='order_id.sale_id', store=True, readonly=True)   
