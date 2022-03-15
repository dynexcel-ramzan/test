/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_order_notes.pos_order_notes', function (require) {
"use strict";
    var pos_model = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;
    var SuperOrder = pos_model.Order;
    const ProductScreen = require('point_of_sale.ProductScreen');
    var SuperOrderline = pos_model.Orderline;
    const PosComponent = require('point_of_sale.PosComponent');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');


    
    pos_model.Order = pos_model.Order.extend({
        get_order_note: function(){
            return $("#order_note").val();
        },
        export_as_JSON: function() {
            var self = this;
            var loaded=SuperOrder.prototype.export_as_JSON.call(this);
            loaded.order_note=self.get_order_note(); 
            self.order_note = self.get_order_note(); 
            return loaded;
        },
        export_for_printing: function(){
            var self = this
            var receipt = SuperOrder.prototype.export_for_printing.call(this)
            receipt.order_note = self.order_note;
            return receipt
        }
    });
    
    pos_model.Orderline = pos_model.Orderline.extend({            
        initialize: function(attr,options){
            this.order_line_note='';
            SuperOrderline.prototype.initialize.call(this,attr,options);
        },
        export_for_printing: function(){
            var dict = SuperOrderline.prototype.export_for_printing.call(this);
            dict.order_line_note = this.order_line_note;
            return dict;
        },
        get_order_line_comment: function(){
            var self = this;        
            return self.order_line_note;
        },
        export_as_JSON: function() {
            var self = this;
            var loaded=SuperOrderline.prototype.export_as_JSON.call(this);
            loaded.order_line_note=self.get_order_line_comment();  
            return loaded;
        }
    });


    class OrderlineNoteButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        get currentOrder(){
            return this.env.pos.get_order();
        }
        async onClick() {
            var text_limit = this.env.pos.config.note_keyword_limit;
            var is_text_limit = this.env.pos.config.set_note_keyword_limit;
            if(typeof(this.currentOrder.get_selected_orderline())=='object'){
                const { confirmed } = await this.showPopup('WkTextAreaPopup', {
                    title: this.env._t('Add Note'),
                    value: this.currentOrder.get_selected_orderline().order_line_note,
                });
                console.log("confirmed",confirmed)
                console.log('$("textarea")',$("textarea"))
                $("textarea").css({"width":"92%","height":"56%","resize":"none"});
                if(text_limit && is_text_limit)
                    $("textarea").attr('maxlength',text_limit.toString());
                if (confirmed) {
                    // console.log("this getPayload",this.getPayload())
                    var note = $('textarea').val();
                    $('ul.orderlines li.selected ul div#extra_comments').text(note);
                    this.currentOrder.get_selected_orderline().order_line_note=note;
                }
            }
            else{
                this.showPopup('WkAlertPopUp',{
                    'title':'No Selected Order Line',
                    'body':'Please add/select an orderline'
                })

            }

        }
    }
    OrderlineNoteButton.template = 'OrderlineNoteButton';

    ProductScreen.addControlButton({
        component: OrderlineNoteButton,
        condition: function() {
            console.log("this",this.env.pos)
            return this.env.pos.config.on_product_line;
        },
    });

    Registries.Component.add(OrderlineNoteButton);

    return OrderlineNoteButton;

});    