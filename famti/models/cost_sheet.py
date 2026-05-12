from odoo import models, fields, api

class CostSheet(models.Model):
    _name = 'cost.sheet'
    _description = 'Cost Sheet'

    name = fields.Char(string="Cost Sheet No", required=True, copy=False, default="New")
    sale_order_id = fields.Many2one('sale.order', string="Sales Order",required=True)
    partner_id = fields.Many2one('res.partner', string="Customer",related='sale_order_id.partner_id',store=True,readonly=True)
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Float(string="Quantity (KG)")
    template_ids = fields.Many2many(
        'cost.sheet.template',
        string="Templates"
    )

    slitted_template_ids = fields.Many2many(
        'cs.slitted.template',
        string="Cost Sheet Template(Slitted)"
    )

    raw_material_cost = fields.Float(string="Raw Material Cost / KG")
    metallization_cost = fields.Float(string="Metallization Cost / KG")
    slitting_cost = fields.Float(string="Slitting Cost / KG")
    packing_cost = fields.Float(string="Packing Cost / KG")
    logistics_cost = fields.Float(string="Logistics Cost / KG")

    wastage_percent = fields.Float(string="Wastage %")

    total_cost_per_kg = fields.Float(string="Total Cost / KG", compute="_compute_total_cost", store=True)

    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)

    selling_price = fields.Float(string="Selling Price / KG")

    profit_per_kg = fields.Float(string="Profit / KG", compute="_compute_profit", store=True)

    total_profit = fields.Float(string="Total Profit", compute="_compute_profit", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'Submitted to CFO'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'cost.sheet.sequence'
            ) or 'New'

        return super().create(vals)

    def action_cfo_approval(self):
        if self.state == 'draft':
            self.write({'state': 'to_approve'})

    def action_approve(self):
        if self.state == 'to_approve':
            self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_reset_to_draft(self):
        if self.state not in ['draft','to_approve']:
            self.write({'state': 'draft'})


    def action_calculate_metaliser(self):
        templates = self.env['cost.sheet.template'].search([])
        self.template_ids = [(6, 0, templates.ids)]
        return True

    def action_calculate_slitter(self):
        templates = self.env['cs.slitted.template'].search([])
        self.slitted_template_ids = [(6, 0, templates.ids)]
        return True

    @api.depends('qty', 'wastage_percent', 'raw_material_cost',
                 'metallization_cost', 'slitting_cost',
                 'packing_cost', 'logistics_cost')
    def _compute_total_cost(self):
        for rec in self:

            base_cost = (
                    rec.raw_material_cost +
                    rec.metallization_cost +
                    rec.slitting_cost +
                    rec.packing_cost +
                    rec.logistics_cost
            )

            if rec.wastage_percent:
                net_qty = rec.qty * (1 - rec.wastage_percent / 100.0)
            else:
                net_qty = rec.qty

            rec.total_cost_per_kg = (base_cost * rec.qty) / net_qty if net_qty else 0
            rec.total_cost = rec.total_cost_per_kg * rec.qty

    @api.depends('selling_price', 'total_cost_per_kg', 'qty')
    def _compute_profit(self):
        for rec in self:
            rec.profit_per_kg = rec.selling_price - rec.total_cost_per_kg
            rec.total_profit = rec.profit_per_kg * rec.qty