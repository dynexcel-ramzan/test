from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings


class account_move(models.Model):
    _inherit = 'account.move'

    submit_to_approve = fields.Boolean(string="Is Approval", default=False, store=True)
    is_approved = fields.Boolean(string="Is Approved", default=False, store=True)
    is_lock = fields.Boolean(string="Is Lock", default=False, store=True)

    def action_approval(self):
        if not self.invoice_date:
            raise UserError(_('You can not submit Invoice/Bill if Invoice/Bill Date is missing.'))
        self.write({'state': 'approval', 'submit_to_approve': True, 'is_lock': True})

    def action_approved(self):
        self.write({'state': 'approved', 'is_approved': True})


