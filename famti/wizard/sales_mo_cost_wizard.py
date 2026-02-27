from odoo import models, fields, api

class ManufacturingCostWizard(models.TransientModel):
    _name = 'manufacturing.cost.wizard'
    _description = 'Manufacturing Cost Wizard'

    sale_id = fields.Many2one('sale.order', string="Sale Order")

    manufacturing_service_id = fields.Many2one(
        'product.product',
        string="Manufacturing Service",
        domain="[('type','=','service'),('mo_service_cost','=',True)]",
        required=True
    )

    total_cost = fields.Float(string="Total Manufacturing Cost")
    mo_id = fields.Many2one(
        'mrp.production',
        string="Manufacturing Order"
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product"
    )
    reference = fields.Char(string="Reference")
    quantity = fields.Float(string="Product Quantity")
    unit_cost = fields.Float(string="Unit Cost")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        sale_id = self.env.context.get('default_sale_id')
        if not sale_id:
            return res

        valuation = self.env['sale.mo.valuation'].search(
            [('sale_id', '=', sale_id)],
            order='id desc',
            limit=1
        )

        if valuation:
            res.update({
                'mo_id': valuation.mo_id.id,
                'product_id': valuation.product_id.id,
                'reference': valuation.reference,
                'quantity': valuation.quantity,
                'unit_cost': valuation.unit_cost,
                'total_cost': valuation.total_cost,
            })

        return res

    def action_confirm(self):
        existing_line = self.sale_id.order_line.filtered(
            lambda l: l.product_id == self.manufacturing_service_id
        )

        if existing_line:
            existing_line.price_unit = self.total_cost
            existing_line.product_uom_qty = 1
        else:
            self.env['sale.order.line'].create({
                'order_id': self.sale_id.id,
                'product_id': self.manufacturing_service_id.id,
                'product_uom_qty': 1,
                'price_unit': self.total_cost,
                'name': self.manufacturing_service_id.name,
            })