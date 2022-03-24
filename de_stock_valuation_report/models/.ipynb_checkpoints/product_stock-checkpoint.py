# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductStockReport(models.AbstractModel):
    _name = "report.de_stock_valuation_report.de_stock_valuation_pdf_report"
    _description = "Product Stock Reprot"

    def get_report_values(self,docids,data=None):
        
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

        return {
            'doc_ids': self.ids,
            'doc_model': 'product.stock.valuation.wizard',
            'dat': dat,
            'data': data,
            'get_saleprice': self._get_saleprice,
            'get_product_name': self._get_product_name,
        }
    
    def _get_product_name(self, product_id):
        """
        return Product display name of the product
        """
        products = self.env['product.product'].search([('id', '=', product_id)], limit=1)
        for p in products:
            return p.name
        
        
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
            
        #else:
            #pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', product_id)], limit=1)
            #base_pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_item.base_pricelist_id.id), ('product_id', '=', product_id)], limit=1)
            
        #if pricelist_item.compute_price == 'fixed':
            #saleprice = pricelist_item.fixed_price
        #elif pricelist_item.compute_price == 'percentage':
            #seleprice = list_price
            #saleprice = pricelist_item.percent_price
        #elif pricelist_item.compute_price == 'formula':
            #if pricelist_item.base == 'list_price':
                #saleprice = list_price * (pricelist_item.price_discount / 100)
            #elif pricelist_item.base == 'standard_price':
                #saleprice = product_id.standard_price * (pricelist_item.price_discount/100)
            #elif pricelist_item.base == 'pricelist':
                #saleprice = base_pricelist_item.fixed_price * (pricelist_item.price_discount/100)
        #else:
            #saleprice = list_price
        #saleprice = list_price   
        return saleprice
    
    
    
    
class ProductStockReportXlsx(models.AbstractModel):
    _name = "report.de_stock_valuation_report.de_stock_valuation_xlsx_report"
    _description = "Product Stock Xlsx Reprot"

    def get_report_values(self,docids,data=None):
        
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

        return {
            'doc_ids': self.ids,
            'doc_model': 'product.stock.valuation.wizard',
            'dat': dat,
            'data': data,
            'get_saleprice': self._get_saleprice,
            'get_product_name': self._get_product_name,
        }
    
    def _get_product_name(self, product_id):
        """
        return Product display name of the product
        """
        products = self.env['product.product'].search([('id', '=', product_id)], limit=1)
        for p in products:
            return p.name
        
        
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
            
        #else:
            #pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', product_id)], limit=1)
            #base_pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_item.base_pricelist_id.id), ('product_id', '=', product_id)], limit=1)
            
        #if pricelist_item.compute_price == 'fixed':
            #saleprice = pricelist_item.fixed_price
        #elif pricelist_item.compute_price == 'percentage':
            #seleprice = list_price
            #saleprice = pricelist_item.percent_price
        #elif pricelist_item.compute_price == 'formula':
            #if pricelist_item.base == 'list_price':
                #saleprice = list_price * (pricelist_item.price_discount / 100)
            #elif pricelist_item.base == 'standard_price':
                #saleprice = product_id.standard_price * (pricelist_item.price_discount/100)
            #elif pricelist_item.base == 'pricelist':
                #saleprice = base_pricelist_item.fixed_price * (pricelist_item.price_discount/100)
        #else:
            #saleprice = list_price
        #saleprice = list_price   
        return saleprice