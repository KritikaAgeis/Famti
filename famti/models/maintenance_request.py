from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    show_supervisor_button = fields.Boolean(compute="_compute_stage_buttons",store=False)
    show_approve_button = fields.Boolean(compute="_compute_stage_buttons",store=False)
    show_submit_button =  fields.Boolean( compute="_compute_stage_buttons", store=False)

    @api.depends('stage_id')
    def _compute_stage_buttons(self):
        for rec in self:
            rec.show_supervisor_button = False
            rec.show_approve_button = False
            rec.show_submit_button = False

            if rec.stage_id.name == "To Approve":
                rec.show_supervisor_button = True

            if rec.stage_id.name == "In Progress":
                rec.show_approve_button = True

            if rec.stage_id.name == "New Request":
                rec.show_submit_button = True


    def send_for_cfo_appoval(self):
        for rec in self:
            # find CFO stage
            cfo_stage = self.env['maintenance.stage'].search(
                [('name', '=', 'Repaired')],	
                limit=1
            )
            if rec.stage_id.name == 'To Approve':
                rec.stage_id = cfo_stage.id
            else:
                raise UserError(_('Only To Approve Will Be Send To Approve By Supervisor'))

        
    def maintenance_approval(self):
        for rec in self:
            cfo_stage = self.env['maintenance.stage'].search(
                [('name', '=', 'To Approve')],
                limit=1
            )
            if rec.stage_id.name == 'In Progress':
                rec.stage_id = cfo_stage.id
            else:
                raise UserError(_('Only In Progress Will Be Send To Approve By Maintenance'))
    
    def submit_for_approval(self):
        for rec in self:
            cfo_stage = self.env['maintenance.stage'].search(
                [('name', '=', 'In Progress')],
                limit=1
            )
            if rec.stage_id.name == 'New Request':
                rec.stage_id = cfo_stage.id
            else:
                raise UserError(_('Only New Request Will Be Send To In Progress'))





