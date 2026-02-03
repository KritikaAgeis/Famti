from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    stock_location_id = fields.Many2one('stock.location', string='QC Hold Location')
    incoming_picking_type_id = fields.Many2one('stock.picking.type',string='Operation Type',
        domain="[('code', '=', 'incoming')]",)
