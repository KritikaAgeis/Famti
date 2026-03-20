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
    contractor_id = fields.Many2one('res.partner', string="Contractor")
    contractor_phone = fields.Char(string="Phone No", required="True")
    expected_duration = fields.Float(string="Expected Maintenance Duration")
    start_datetime = fields.Datetime(string="Start Date")
    end_datetime = fields.Datetime(string="End Date")
    track_ids = fields.One2many('maintenance.track','maintenance_id',
        string="Track Maintenance", tracking=True
    )
    email = fields.Char(string="Email", required="True")

    @api.depends('maintenance_team_id')
    def _compute_responsible_field(self):
        for rec in self:
            rec.show_responsible = False
            if rec.maintenance_team_id and rec.maintenance_team_id.name == "External Maintenance":
                rec.show_responsible = True

    @api.onchange('user_id', 'maintenance_team_id','contractor_id')
    def _onchange_email(self):
        for rec in self:
            if rec.maintenance_team_id and rec.maintenance_team_id.name == "External Maintenance":
                rec.email = rec.contractor_id.email if rec.contractor_id and rec.contractor_id.email else False
                rec.contractor_phone = rec.contractor_id.phone if rec.contractor_id and rec.contractor_id.phone else False
                rec.user_id = False
            else:
                rec.email = rec.user_id.email if rec.user_id else False
                rec.contractor_phone = rec.user_id.partner_id.phone if rec.user_id and rec.user_id.partner_id.phone else False
    
    @api.model
    def create(self, vals):
        rec = super().create(vals)

        if rec.maintenance_team_id and rec.maintenance_team_id.name == "External Maintenance":
            rec.activity_schedule_external()

        return rec
        
    def write(self, vals):
        res = super().write(vals)

        for rec in self:
            if rec.maintenance_team_id and rec.maintenance_team_id.name == "External Maintenance":
                rec.activity_schedule_external()

        return res

    def activity_schedule_external(self):
        for rec in self:
            if rec.maintenance_team_id.name == "External Maintenance":
                if not rec.email:
                    raise UserError("Enter contractor email")

                self.env['mail.activity'].create({
                    'res_model_id': self.env['ir.model']._get_id('maintenance.request'),
                    'res_id': rec.id,
                    'summary': 'External Maintenance',
                    'note': f"Assigned to Contractor: {rec.contractor_id.name} ({rec.email})",
                    'user_id': self.env.user.id  
                })

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
                for track in rec.track_ids:
                    if track.state not in ['repaired', 'scrap']:
                        track.state = 'in_progress'
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
                for track in rec.track_ids:
                    if track.state not in ['repaired', 'scrap']:
                        track.state = 'repaired'
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
                for track in rec.track_ids:
                    if track.state not in ['repaired', 'scrap']:
                        track.state = 'to_approve'
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

    def action_open_track_wizard(self):
        return {
            'name': 'Track Maintenance',
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.track.wizard',
            'view_mode': 'form',
            'target': 'new', 
            'context': {
                'default_maintenance_id': self.id,
            }
        }


class MaintenanceTrack(models.Model):
    _name = 'maintenance.track'
    _description = 'Maintenance Tracking'

    maintenance_id = fields.Many2one(
        'maintenance.request',
        string="Maintenance",
        ondelete='cascade'
    )

    team_id = fields.Many2one('maintenance.team', string="Team", tracking=True)
    user_id = fields.Many2one('res.users', string="Responsible", tracking=True)

    contractor_name = fields.Char(string="Contractor Name", tracking=True)
    contractor_id = fields.Many2one('res.partner', string="Contractor")
    phone = fields.Char(string="Phone No", tracking=True)
    email = fields.Char(string="Email")
    request_date = fields.Datetime(string="Request Date", tracking=True)
    schedule_date = fields.Datetime(string="Scheduled Date", tracking=True)

    start_datetime = fields.Datetime(string="Start Date", tracking=True)
    end_datetime = fields.Datetime(string="End Date", tracking=True)

    expected_duration = fields.Float(string="Expected Maintenance Duration", tracking=True)

    duration = fields.Float(string="Duration", tracking=True)

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string="Priority", tracking=True)
    show_responsible = fields.Boolean(compute="_compute_responsible_field",store=False)
    state = fields.Selection([
        ('new', 'New Request'),
        ('to_approve', 'To Approve'),
        ('in_progress', 'In Progress'),
        ('repaired', 'Repaired'),
        ('scrap', 'Scrap'),
    ], string="Status", default='new', tracking=True)


    notes = fields.Text(string="Notes", tracking=True)
    

    @api.depends('team_id')
    def _compute_responsible_field(self):
        for rec in self:
            rec.show_responsible = False
            if rec.team_id and rec.team_id.name == "External Maintenance":
                rec.show_responsible = True
    

    def action_open_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Track Maintenance',
            'res_model': 'maintenance.track',
            'view_mode': 'form',
            'view_id': self.env.ref('famti.view_maintenance_track_form').id,
            'res_id': self.id,
            'target': 'current',  
        }
