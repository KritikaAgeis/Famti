from odoo import api, fields, models, _


class FreightVessel(models.Model):
    _name = 'freight.vessel'

    name= fields.Char(string='Vessel Name',required=True)
    active = fields.Boolean(default=True)