from odoo import models
from odoo.exceptions import UserError
from odoo import _

class ScrapConfirmWizard(models.TransientModel):
    _name = 'scrap.confirm.wizard'
    _description = 'Scrap Confirmation'
    
    def action_confirm_scrap(self):
        active_id = self.env.context.get('active_id')
        rec = self.env['maintenance.request'].browse(active_id)

        scrap_stage = self.env['maintenance.stage'].search(
            [('name', '=', 'Scrap')],
            limit=1
        )

        rec.stage_id = scrap_stage.id