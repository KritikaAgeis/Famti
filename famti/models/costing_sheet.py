from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

# class CostingSheet(models.Model):
#     _name = 'costing.sheet'
#     _description = 'Costing Sheet'
#
#     name = fields.Char(string="Costing Reference", required=True, copy=False, default="New")
#     customer_id = fields.Many2one('res.partner', string="Customer")


#Template with codes--------------------
class CostSheetTemplate(models.Model):
    _name = 'cost.sheet.template'
    _description = 'Cost Sheet Template (ROWS)'

    name = fields.Char(required=True)
    title = fields.Char(string="Title")
    code = fields.Char(string="Code")
    uom = fields.Char(string="UOM")
    default_value = fields.Float(string="Default Value",digits=(16, 10))
    formula = fields.Char(string="Formula")
    sequence = fields.Integer(string="Sequence")
    is_computed = fields.Boolean(default=False)
    # cs_id = fields.Many2one('costing.sheet')
    cost_sheet_id = fields.Many2one('cost.sheet',string="Cost Sheet")

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Code must be unique!')
    ]

    def read(self, fields=None, load='_classic_read'):
        # Call normal read
        res = super().read(fields, load)
        self.compute_all()
        return res

    def compute_all(self):
        records = self.search([])
        context = {r.code: r.default_value for r in records if r.code}
        # Step 2: compute all formulas in sequence order
        for rec in records.sorted(key=lambda r: r.sequence):
            if rec.formula:
                try:
                    value = safe_eval(rec.formula, context)
                    rec.default_value = value
                    context[rec.code] = value
                except Exception:
                    rec.default_value = 0

