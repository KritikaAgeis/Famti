from odoo import fields, models

class FreightService(models.Model):
    """For Creating services available for freight"""
    _name = 'freight.service'
    _description = 'Freight Service'

    name = fields.Char(string='Name', required=True, help='Name of service')
    sale_price = fields.Float(string='Sale Price', required=True,
                              help='Sale price of the service')
    line_ids = fields.One2many('freight.service.line', 'service_id',
                               string='Service Lines',
                               help="Service lines corresponding to a service")
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)


class FreightServiceLine(models.Model):
    _name = 'freight.service.line'
    _description = 'Freight Service Line'

    partner_id = fields.Many2one('res.partner', string="Vendor",
                                 help='Partner corresponding to the service')
    sale = fields.Float(string='Sale Price',
                        help='Mention the price for the service')
    service_id = fields.Many2one('freight.service', string='Service',
                                 help='Relation from freight service')
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)
