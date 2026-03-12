from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'


    def send_for_cfo_appoval(self):
        for rec in self:
            # find CFO stage
            cfo_stage = self.env['maintenance.stage'].search(
                [('name', '=', 'To Approve')],
                limit=1
            )
            if rec.stage_id.name == 'New Request':
                rec.stage_id = cfo_stage.id
            else:
                raise UserError(_('Only New Requests Will Be Send To Approve By CFO'))





