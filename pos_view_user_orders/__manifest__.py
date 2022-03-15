# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "POS Display Orders User-wise",
  "summary"              :  """The module allows you to admin to restrict the POS user to view only those orders which belong to the user’s particular POS""",
  "category"             :  "Point of Sale",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-POS-View-User-Orders.html",
  "description"          :  """POS Display Orders User-wise
Odoo POS View User Orders
POS restrict user
Restrict POS user
Display user orders
Restrict POS user orders
Sort POS order view""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_view_user_orders&lifetime=90&lout=1&custom_url=/",
  "depends"              :  ['point_of_sale'],
  "data"                 :  [
                             'views/res_user_view.xml',
                             'security/pos_order_security.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  15,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
