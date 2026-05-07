import io
import base64
import xlsxwriter
from odoo import models, fields

class SaleReportWizard(models.TransientModel):
    _name = 'sale.report.wizard'
    _description = 'Sales Report Wizard'

    date_from = fields.Date()
    date_to = fields.Date()
    partner_id = fields.Many2one('res.partner')

    def action_generate_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Sales Report')

        bold = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        number_format = workbook.add_format({'num_format': '#,##0.00'})

        headers = ['Customer', 'Order', 'Date', 'Product', 'Treatment In', 'Treatment Out', 'Quantity', 'Total']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        domain = [('state', 'in', ['sale', 'done'])]

        if self.date_from:
            domain.append(('date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_order', '<=', self.date_to))
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))

        orders = self.env['sale.order'].search(domain, order="date_order asc")

        row = 1
        grand_total = 0

        for order in orders:
            for line in order.order_line:
                sheet.write(row, 0, order.partner_id.name or '')
                sheet.write(row, 1, order.name)
                sheet.write(row, 2, order.date_order, date_format)
                sheet.write(row, 3, line.product_id.name or '')
                sheet.write(row, 3, line.product_id.treatment_in or '')
                sheet.write(row, 3, line.product_id.treatment_out or '')
                sheet.write(row, 4, line.product_uom_qty or 0)
                sheet.write(row, 5, line.price_subtotal or 0, number_format)

                grand_total += line.price_subtotal or 0
                row += 1

        sheet.write(row, 4, 'Grand Total', bold)
        sheet.write(row, 5, grand_total, number_format)

        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 25)
        sheet.set_column('E:E', 12)
        sheet.set_column('F:F', 15)

        workbook.close()
        output.seek(0)

        file_data = base64.b64encode(output.read())

        attachment = self.env['ir.attachment'].create({
            'name': 'Sales_Report.xlsx',
            'type': 'binary',
            'datas': file_data,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }