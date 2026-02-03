from odoo import models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_picking(self):
        res = super()._prepare_picking()

        company = self.company_id
        if company.incoming_picking_type_id:
            res['picking_type_id'] = company.incoming_picking_type_id.id

            if company.incoming_picking_type_id.default_location_dest_id:
                res['location_dest_id'] = (
                    company.incoming_picking_type_id.default_location_dest_id.id
                )

        if company.stock_location_id:
            res['location_dest_id'] = company.stock_location_id.id

        return res