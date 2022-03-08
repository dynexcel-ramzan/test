odoo.define('point_of_sale.WkAlertPopUp', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class WkAlertPopUp extends AbstractAwaitablePopup {
        getPayload() {
            return null;
        }
    }
    WkAlertPopUp.template = 'WkAlertPopUp';
    WkAlertPopUp.defaultProps = {
        title: 'Confirm ?',
        body: '',
    };

    Registries.Component.add(WkAlertPopUp);

    return WkAlertPopUp;


});