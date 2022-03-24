# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateutil


class PosSlipData(models.AbstractModel):
    _name = 'report.de_pos_slip_pos_order.pos_slip_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        company_id = self.env.company.id
        active_ids = self.env.context.get('active_ids', [])
        # active_sale_order = self.env['pos.order'].browse(active_ids)
        docs = self.env['pos.order'].browse(docids)
        # config = self.env['pos.config'].search([('crm_team_id', '=', active_sale_order.team_id.id)])
        user = self.env.user
        company = self.env['res.company'].search([('id', '=', company_id)])
        return {
            'data': data,
            'docs': docs,
            # 'config': config,
            'user': user,
            'company': company,
        }
