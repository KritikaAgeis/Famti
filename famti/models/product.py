from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mo_serial_no = fields.Boolean(string="Is Metalize")
    is_consumables = fields.Boolean(string="Is Consumables")
    supplier_name = fields.Many2one('res.partner',string="Supplier Name")
    material_type = fields.Char(string="Material Type")
    type_reference = fields.Char(string="Type")
    film_description = fields.Text(string="Film Description")
    treatment_in = fields.Char(string="Treatment In")
    treatment_out = fields.Char(string="Treatment Out")
    product_reference_code = fields.Char(string="Product Code")
    mo_service_cost = fields.Boolean(string="Is Manufacturing Cost")



class ProductProduct(models.Model):
    _inherit = "product.product"

    mo_serial_no = fields.Boolean(string="Is Metalize")
    is_consumables = fields.Boolean(string="Is Consumables")

    supplier_name = fields.Many2one('res.partner',string="Supplier Name")
    film_description = fields.Text(string="Film Description")
    material_type = fields.Char(string="Material Type")
    type_reference = fields.Char(string="Type")
    treatment_in = fields.Char(string="Treatment In")
    treatment_out = fields.Char(string="Treatment Out")
    mo_service_cost = fields.Boolean(string="Is Manufacturing Cost")

    low_stock_alert_sent = fields.Boolean(
        string="Low Stock Alert Sent",
        default=False
    )

    @api.model
    def check_low_stock_products(self):

        products = self.search([
            ('type', 'in', ['product', 'consu']),
            ('low_stock_alert_sent', '!=', True)
        ])

        low_stock_products = products.filtered(lambda p: p.qty_available < 20)
        print("low_stock_products==============",len(low_stock_products))

        if not low_stock_products:
            return

        group = self.env.ref('famti.group_inventory_dep_users', raise_if_not_found=False)
        if not group:
            return

        users = group.users.filtered(lambda u: u.email)
        if not users:
            return

        product_rows = ""
        for product in low_stock_products:
            product_rows += f"""
                <tr>
                    <td style="padding:8px;border:1px solid #ddd;">{product.default_code or '-'}</td>
                    <td style="padding:8px;border:1px solid #ddd;">{product.name}</td>
                    <td style="padding:8px;border:1px solid #ddd;text-align:center;">{product.qty_available}</td>
                </tr>
            """

        body_html = f"""
            <p>Dear Inventory Team,</p>

            <p>The following products are below minimum stock level (20 units):</p>

            <table style="border-collapse:collapse;width:100%;">
                <thead>
                    <tr>
                        <th style="padding:8px;border:1px solid #ddd;background:#f2f2f2;">
                            Product Code
                        </th>
                        <th style="padding:8px;border:1px solid #ddd;background:#f2f2f2;">
                            Product
                        </th>
                        <th style="padding:8px;border:1px solid #ddd;background:#f2f2f2;text-align:center;">
                            Available Quantity
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {product_rows}
                </tbody>
            </table>

            <br/>
            <p>
                A purchase requisition has been generated for the above low-stock products.
                Please review the requisition and proceed with submission to the CFO for approval.
            </p>

            <p>Regards,<br/>Fam Ti</p>
        """

        email_to = ",".join(users.mapped('email'))

        mail_values = {
            'subject': 'Low Stock Alert - Multiple Products',
            'body_html': body_html,
            'email_to': email_to,
        }

        self.env['mail.mail'].create(mail_values).send()

        recovered_products = self.search([
            ('type', 'in', ['product', 'consu']),
            ('low_stock_alert_sent', '=', True)
        ]).filtered(lambda p: p.qty_available >= 20)

        recovered_products.write({'low_stock_alert_sent': False})