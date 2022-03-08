
from odoo import api, models, modules,fields, _
from odoo.exceptions import UserError

class ProjectTaskExt(models.Model):
    _inherit = 'product.template'

    style_code = fields.Char(string="Style Code")
    _sql_constraints = [
        ('style_code_unique', 'unique(style_code)', 'This Style Code is already exist, use a different code!'), ]

    @api.constrains('style_code')
    def product_uom_qty_order_val(self):
        if self.style_code:
            contains_digit = self.style_code.isdigit()
            if not contains_digit:
                raise UserError(('Sorry! Only Integer Values are allowed in Style Code field.'))
            else:
                if len(str(self.style_code)) != 8:
                    raise UserError(("Length must be 8 digits"))
                else:
                    pass

