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
    final_destination_id = fields.Many2one('freight.port', string="Final Destination",
                                      help="Final Destination of the freight order",tracking=True)
    eta = fields.Datetime(string="Estimated Time of Arrival")
    document_ids = fields.One2many('freight.order.document','freight_order_id',
        string="Documents"
    )
    etd_discharge_port = fields.Datetime(string="ETD (Discharge Port)")
    eta_destination = fields.Datetime(string="ETA (Destination / Toronto)")

    


class FreightOrder(models.Model):
    _inherit = 'freight.order.line'
    _description = 'Freight Order Lines'


    purchase_id = fields.Many2one('purchase.order', string="Purchase Order", related='order_id.purchase_id', store=True, readonly=True)   
    sale_id = fields.Many2one('sale.order', string="Sale Order", related='order_id.sale_id', store=True, readonly=True)   
    container_number = fields.Char(string="Container Number", tracking=True)

class FreightOrderDocument(models.Model):
    _name = 'freight.order.document'
    _description = 'Freight Order Documents'

    freight_order_id = fields.Many2one(
        'freight.order',
        string="Freight Order",
        ondelete='cascade'
    )

    document_type = fields.Selection([
        ('commercial_invoice', 'Commercial Invoice'),
        ('packing_list', 'Packing List (Excel/PDF)'),
        ('mbl', 'Master Bill of Lading'),
        ('hbl', 'House Bill of Lading'),
        ('coa', 'COA'),
        ('heat_certificate', 'Heat Treatment Certificate'),
        ('emanifest', 'E-manifest / ACI'),
    ], string="Document Type", required=True)

    file = fields.Binary(string="Upload Document")
    file_name = fields.Char(string="File Name")
