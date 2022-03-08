from odoo import models, fields, api


class DesignSample(models.Model):
    _name = 'design.sample'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Design Sample"

    name = fields.Char(string="Sample Reference", readonly=True, required=True, copy=False, default='New')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')
    
    sample_name = fields.Char(string="Product")
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    
    design_sample_lines = fields.One2many('design.sample.line', 'design_sample_id', string='Design Sample Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
    cmt_cost = fields.Float(string='CMT Cost')
    currency_id = fields.Char(string='Currency')
    currency_rate = fields.Float(string='Currency Rate')
    concern_person = fields.Char(string='Concern Person')
    is_sample_rcvd = fields.Boolean(string='Sample Recieved?')
    is_pack_rcvd = fields.Boolean(string='Tech Pack Recieved?')
    is_sample_sent = fields.Boolean(string='Sample Sent?')
    sampl_rqst_date = fields.Date(string='Sample Request Date')
    sample_dispatch_date = fields.Date(string='Sample Dispatch Date')
    sample_sent_date = fields.Date(string='Sample Sent Date')
    code_awb = fields.Char(string='Code AWB#')
    product_categ_id = fields.Many2one('product.category', string='Product Category')
    total_value = fields.Float(string='Total Value', compute='_calculate_total_value', readonly=True)
    total_cost = fields.Float(string='Total Cost', compute='_calculate_total_cost', readonly=True)
    profit_percentage = fields.Float(string='Profit Percentage(%)')
    total_price = fields.Float(string='Total Price', compute='_calculate_total_price', readonly=True)
    quote_price = fields.Char(string='Quote Price')
    
    @api.multi
    def action_pending(self):
        return self.write({'state': 'pending'})
    
    @api.multi
    def action_approved(self):
        return self.write({'state': 'approved'})
    
    @api.multi
    def action_rejected(self):
        return self.write({'state': 'rejected'})
    
    @api.multi
    def action_cancel(self):
        return self.write({'state': 'draft'})
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
           'design.sample') or 'New'
        result = super(DesignSample, self).create(vals)
        return result


#     @api.model
#     def create(self, vals):
#         vals['name'] = self.env['ir.sequence'].get('design.sample') or ' '
#         res_id = super(DesignSample, self).create(vals)
#         return res_id
    
    def _calculate_total_value(self):
        for rs in self:
            sum_value = 0
            for line in rs.design_sample_lines:
                sum_value += line.value
        rs.total_value = sum_value
        
    def _calculate_total_cost(self):
        for record in self:
            record.total_cost = record.total_value + record.cmt_cost
            
            
    @api.depends('total_cost','profit_percentage','currency_rate')
    def _calculate_total_price(self):
        if self.profit_percentage > 0:
            for record in self:
                percentage_value = record.profit_percentage / 100
                percent_value = record.total_cost * percentage_value
                percentage_price = percent_value + record.total_cost
                record.total_price = percentage_price / record.currency_rate
    
class DesignSampleLine(models.Model):
    _name = 'design.sample.line'
    _description = "Design Sample Line"
    
    design_sample_id = fields.Many2one('design.sample', string='Design Reference', required=False, ondelete='cascade', index=True, copy=False, readonly=True)
    product_name = fields.Char(string='Name', required=True)
    arranged_by = fields.Char(string='Arranged By')
    qty = fields.Float(string='Quantity')
    unit = fields.Char(string='Unit')
    aprx_cost = fields.Float(string='Aprx. Cost')
    value = fields.Float(string='Value', compute='_calculate_value', required=True)
    
    @api.depends('qty','aprx_cost')
    def _calculate_value(self):
        for record in self:
            record.value = record.qty * record.aprx_cost