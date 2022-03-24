import xlwt
import xlrd

from odoo import models
import datetime
from odoo.exceptions import UserError

class PartnerXlsx(models.AbstractModel):
    _name = 'report.de_stock_valuation_report.de_stock_valuation_xlsx_report'

    _inherit = 'report.report_xlsx.abstract'
    
    def _get_saleprice(self, categ_id, product_tmpl_id, product_id, pricelist_id, list_price):
        """
        return sale price of the product
        """
        saleprice = list_price
        variant_pricelist_item = product_pricelist_item = categ_pricelist_item = self.env['product.pricelist.item']
        variant_pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', product_id)], limit=1)
        pricelist_item = variant_pricelist_item
        if not variant_pricelist_item:
            product_pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_tmpl_id', '=', product_tmpl_id)], limit=1)
            pricelist_item = product_pricelist_item
            if not product_pricelist_item:
                categ_pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('categ_id', '=', categ_id)], limit=1)
                pricelist_item = categ_pricelist_item
        
        
        base_pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=',pricelist_item.base_pricelist_id.id), ('product_tmpl_id', '=', product_tmpl_id)], limit=1)
        
        for pitem in pricelist_item:
            if pitem.compute_price == 'fixed':
                saleprice = pitem.fixed_price
            elif pitem.compute_price == 'percentage':
                saleprice = pitem.product_tmpl_id.list_price - (pitem.product_tmpl_id.list_price * (pitem.percent_price / 100))
            else:
                saleprice = pitem.product_tmpl_id.list_price
        return saleprice
    
    def generate_xlsx_report(self, workbook, data, partners):
                
        query_get_product = ''
        if data['product_id']:
            query_get_product = ' and (a.product_id = ' + str(data['product_id']) + ') '
        else:
            query_get_product = ''
        
                       
        query_get_pricelist = ''
        if data['pricelist_id']:
            query_get_pricelist = ' and (a.pricelist_id = ' + str(data['pricelist_id']) + ') '
        else:
            query_get_pricelist = ''
        
        
        cr = self._cr
        query = """
        select a.product_id, a.default_code, a.barcode, a.product_tmpl_id, a.product_name, a.categ_id, a.category_name, a.lot, max(a.list_price) as list_price, sum(a.quantity) as quantity  from (

select  p.default_code, t.categ_id, s.product_id, p.product_tmpl_id, p.barcode, t.name as product_name, g.name as category_name, b.name as lot, l.name as location, t.list_price, s.quantity
from stock_quant s
join product_product p on s.product_id = p.id
join product_template t on p.product_tmpl_id = t.id
join product_category g on t.categ_id = g.id
left join stock_location l on s.location_id = l.id
left join stock_production_lot b on s.lot_id = b.id
where l.usage != 'view'
and s.in_date <= %(dated)s
and l.id = %(location_id)s
        ) a where a.product_id is not null and a.categ_id in %(categ_ids)s """ + query_get_product + """
        group by a.product_name, a.product_id, a.categ_id, a.category_name, a.lot, a.product_tmpl_id,a.barcode,a.default_code
        having (sum(a.quantity)) > 0
        order by a.category_name
        """
        params = {
            'dated': data['dated'],
            'warehouse_id': data['warehouse_id'],
			'location_id': data['location_id'],
            'categ_ids': tuple(data['categ_ids']),
        }

        self.env.cr.execute(query, params=params)
        
        dat = cr.dictfetchall()


        
#             records = self.env['product.product'].search([('categ_id','=', data['categ_id.id'])])
        format1 = workbook.add_format(({'font_size': 10, 'align': 'vcenter', 'bold':True}))
        format2 = workbook.add_format(({'font_size': 10, 'align': 'vcenter', 'bold':True}))
        sheet1 = workbook.add_worksheet('Production Stock Report')
        sheet1.set_column(0,0,20)
        sheet1.set_column(0,1,50)
        sheet1.set_column(0,2,20)
        sheet1.set_column(0,3,50)
        sheet1.set_column(0,4,20)
        sheet1.set_column(0,5,50)
        sheet1.set_column(0,6,50)

        sheet1.write(0,0,'Category', format1)
        sheet1.write(0,1,'Product', format1)
        sheet1.write(0,2,'Barcode', format1)
        sheet1.write(0,3,'Quantity', format1)
        sheet1.write(0,4,'Price', format1)
        sheet1.write(0,5,'Original Price', format1)
        sheet1.write(0,6,'Valuation', format1)
        row = 1
        col = 0
            

        for d in dat:
            saleprice = get_saleprice(d['categ_id'], d['product_tmpl_id'], d['product_id'], data['pricelist_id'], d['list_price'])
        
            sale_value = saleprice * d['quantity']
            tot = tot + sale_value
            category_name = d['category_name']
            product = self.env['product.product'].search([('categ_id', '=', d['category_name'])])
            product_name = product.display_name
            barcode = d['barcode']
            quantity = d['quantity']
            
            sheet1.write(row,col,d['category_name'], format1)
            sheet1.write(row,col + 1,d['barcode'], format1)
            sheet1.write(row,col + 2,d['quantity'], format1)
            sheet1.write(row,col + 3,d.quantity, format1)
            sheet1.write(row,col + 4,d.sale_value, format1)
            sheet1.write(row,col + 5,d.tot, format1)
#             sheet1.write(row,col + 6,d.tot, format1)
            row = row + 1