from odoo import fields, models


class CustomClearanceRevision(models.Model):
    """Allows custom clearance for freight orders"""
    _name = 'clearance.revision'
    _description = 'Custom Clearance Revision'

    name = fields.Char(string='Name', help='Name of the revision')
    reason = fields.Text(string='Reason', help='Reason for revision')
    clearance_id = fields.Many2one('custom.clearance',
                                   string='Custom Clearance',
                                   help='Relation from custom clearance')
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)
