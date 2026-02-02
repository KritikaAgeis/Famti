from odoo import models, fields

class StockLot(models.Model):
    _inherit = 'stock.lot'

    thickness = fields.Float(string="Thickness (micron)",tracking=True)
    weight = fields.Float(string="Weight (kg)",tracking=True)
    core_id = fields.Char(string="Core Id",tracking=True)

    qc_status = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], default='pending',tracking=True)

    qc_remark = fields.Text(string="QC Remarks",tracking=True)
    upload_doc = fields.Binary(string="Upload Document",tracking=True)
    failure_reasons = fields.Selection([('physical_damage','Physical Damage'),
                                        ('qlty_fail','Quality / Specification Failure'),
                                       ('manuf_defect','Manufacturing Defects'),
                                        ('others','Others')],
                                       string="Failure Reasons",tracking=True)
    category = fields.Char(string="Film Category",tracking=True,help="This helps to categorise specific product.")
    film = fields.Char(string="Film",tracking=True,help="Product Film.")
    film_type = fields.Char(string="Film Type",tracking=True,help="Film Type")
    lot_number = fields.Char(string="Lot Number",tracking=True,help="Lot Number")
    pallet_no = fields.Char(string="Pallet Number",tracking=True,help="Pallet Number")



    def action_coa_passed(self):
        self.qc_status = 'passed'

    def action_coa_failed(self):
        self.qc_status = 'failed'

    def action_reset_to_draft(self):
        self.qc_status = 'pending'

    def action_pass_coa_rolls(self):
        rolls = self.filtered(lambda r: r.qc_status == 'pending')
        if not rolls:
            return True
        res=rolls.write({'qc_status': 'passed'})
        return res
