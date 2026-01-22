from odoo import models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_picking(self):
        # res = super()._prepare_picking()

        # qc_location = self.company_id.stock_location_id
        # print("===qc_location====",qc_location)
        # if qc_location:
        #     res['location_dest_id'] = qc_location.id

        # return res

        res = super()._prepare_picking()

        qc_location = self.company_id.stock_location_id
        print("--------qc_location------",qc_location)
        default_dest_location = res.get('location_dest_id')
        print("--------default_dest_location------",default_dest_location)

        if qc_location and default_dest_location != qc_location.id:
            print("false")
            res['location_dest_id'] = qc_location.id

        return res
