from odoo import models, fields

class CostingSheet(models.Model):
    _name = 'costing.sheet'
    _description = 'Costing Sheet'

    name = fields.Char(string="Costing Reference", required=True, copy=False, default="New")
    customer_id = fields.Many2one('res.partner', string="Customer")
