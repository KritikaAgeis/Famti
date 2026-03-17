from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    show_supervisor_button = fields.Boolean(compute="_compute_stage_buttons",store=False)
    show_approve_button = fields.Boolean(compute="_compute_stage_buttons",store=False)
    show_submit_button =  fields.Boolean( compute="_compute_stage_buttons", store=False)
    show_responsible = fields.Boolean(compute="_compute_responsible_field", store=False)
    show_scrap_button = fields.Boolean(compute="_compute_stage_buttons", store=False)

    contractor_name = fields.Char(string="Contractor Name", required="True")
    contractor_phone = fields.Char(string="Phone No", required="True")

    @api.depends('maintenance_team_id')
    def _compute_responsible_field(self):
        for rec in self:
            rec.show_responsible = False
            if rec.maintenance_team_id and rec.maintenance_team_id.name == "External Maintenance":
                rec.show_responsible = True

    @api.depends('stage_id')
    def _compute_stage_buttons(self):
        for rec in self:
            rec.show_supervisor_button = False
            rec.show_approve_button = False
            rec.show_submit_button = False
            rec.show_scrap_button = False

            if rec.stage_id.name == "To Approve":
                rec.show_supervisor_button = True

            if rec.stage_id.name == "In Progress":
                rec.show_approve_button = True

            if rec.stage_id.name == "New Request":
                rec.show_submit_button = True

            if rec.stage_id.name == "Scrap":
                rec.show_scrap_button = True


    def send_for_cfo_appoval(self):
        for rec in self:
            # find CFO stage
            cfo_stage = self.env['maintenance.stage'].search(
                [('name', '=', 'In Progress')],	
                limit=1
            )
            if rec.stage_id.name == 'To Approve':
                rec.stage_id = cfo_stage.id
            else:
                raise UserError(_('Only To Approve Will Be Send To Approve By Supervisor'))

        
    def maintenance_approval(self):
        for rec in self:

            if not rec.duration:
                raise UserError(_("Please enter the Duration before approving the maintenance."))

            cfo_stage = self.env['maintenance.stage'].search(
                [('name', '=', 'Repaired')],
                limit=1
            )
            if rec.stage_id.name == 'In Progress':
                rec.stage_id = cfo_stage.id
            else:
                raise UserError(_('Only In Progress Will Be Send To Approve By Maintenance'))
    
    def submit_for_approval(self):
        for rec in self:
            cfo_stage = self.env['maintenance.stage'].search(
                [('name', '=', 'To Approve')],
                limit=1
            )
            if rec.stage_id.name == 'New Request':
                rec.stage_id = cfo_stage.id
            else:
                raise UserError(_('Only New Request Will Be Send To In Progress'))

    def action_scrap_confirm(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm Scrap',
            'res_model': 'scrap.confirm.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }
