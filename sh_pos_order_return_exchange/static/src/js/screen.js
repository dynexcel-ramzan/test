odoo.define("sh_pos_order_list.screen", function (require) {
    "use strict";

    const { debounce } = owl.utils;
    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");
    const { useListener } = require("web.custom_hooks");
    const rpc = require("web.rpc");
    var core = require("web.core");
    var framework = require("web.framework");
    var QWeb = core.qweb;
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    var field_utils = require("web.field_utils");

    class OrderListScreen extends PosComponent {
        constructor() {
            super(...arguments);
            this.state = {
                query: null,
                selectedTemplate: this.props.template,
            };
            this.order_no_return = [];
            this.return_filter = false;
            this.updateTemplateList = debounce(this.updateTemplateList, 70);
        }
        back() {
            this.trigger("close-temp-screen");
        }
        change_date() {
            this.state.query = $("#date1")[0].value;
            this.render();
        }
        updateOrderList(event) {
            this.state.query = event.target.value;

            if (event.code === "Enter") {
                const serviceorderlistcontents = this.posorderdetail;
                if (serviceorderlistcontents.length === 1) {
                    this.state.selectedQuotation = serviceorderlistcontents[0];
                }
            } else {
                this.render();
            }
        }
        get posorderdetail() {
            var self = this;

            if (this.state.query && this.state.query.trim() !== "") {
                var templates = this.get_order_by_name(this.state.query.trim());
                return templates;
            } else {
                self.order_no_return = [];
                self.return_order = [];
                _.each(self.all_order, function (order) {
                    if ((order.is_return_order && order.return_status && order.return_status != "nothing_return") || (!order.is_return_order && !order.is_exchange_order)) {
                        self.order_no_return.push(order);
                    } else {
                        self.return_order.push(order);
                    }
                });
                if (!self.return_filter) {
                    return self.order_no_return;
                } else {
                    return self.return_order;
                }
            }
        }
        get_order_by_name(name) {
            var self = this;
            if(self.return_filter){
            	return _.filter(self.env.pos.db.all_return_order, function (template) {
                    if (template.name.indexOf(name) > -1) {
                        return true;
                    } else if (template["pos_reference"].indexOf(name) > -1) {
                        return true;
                    } else if (template["partner_id"] && template["partner_id"][1] && template["partner_id"][1].toLowerCase().indexOf(name) > -1) {
                        return true;
                    } else if (template["date_order"].indexOf(name) > -1) {
                        return true;
                    } else {
                        return false;
                    }
                });
            }else{
            	return _.filter(self.env.pos.db.all_non_return_order, function (template) {
                    if (template.name.indexOf(name) > -1) {
                        return true;
                    } else if (template["pos_reference"].indexOf(name) > -1) {
                        return true;
                    } else if (template["partner_id"] && template["partner_id"][1] && template["partner_id"][1].toLowerCase().indexOf(name) > -1) {
                        return true;
                    } else if (template["date_order"].indexOf(name) > -1) {
                        return true;
                    } else {
                        return false;
                    }
                });
            }
            
        }

        clickLine(event) {
            var self = this;
            self.hasclass = true;
            if ($(event.currentTarget).hasClass("highlight")) {
                self.hasclass = false;
            }
            $(".sh_order_list .highlight").removeClass("highlight");
            $(event.currentTarget).closest("table").find(".show_order_detail").removeClass("show_order_detail");
            $(event.currentTarget).closest("table").find(".show_order_detail").removeClass("show_order_detail");
            $(event.currentTarget).closest("table").find(".show_order_detail").removeClass("show_order_detail");
            var order_id = $(event.currentTarget).attr("data-order-id");
            if(!order_id){
            	order_id = $(event.currentTarget).attr("data-id");
            }
            var order_data = self.env.pos.db.order_by_uid[order_id];
            if (!order_data) {
                order_data = self.env.pos.db.order_by_id[order_id];
            }
            if (order_data && self.hasclass) {
                self.selected_pos_order = order_id;

                if (order_data.sh_line_id) {
                    _.each(order_data.sh_line_id, function (pos_order_line) {
                        $(event.currentTarget).addClass("highlight");
                        $(event.currentTarget)
                            .closest("table")
                            .find("tr#" + order_data.pos_reference.split(" ")[1])
                            .addClass("show_order_detail");
                        $(event.currentTarget)
                            .closest("table")
                            .find("#" + pos_order_line)
                            .addClass("show_order_detail");
                    });
                } else {
                    _.each(order_data.lines, function (pos_order_line) {
                        $(event.currentTarget).addClass("highlight");
                        $(event.currentTarget)
                            .closest("table")
                            .find("tr#" + order_data.pos_reference.split(" ")[1])
                            .addClass("show_order_detail");
                        $(event.currentTarget)
                            .closest("table")
                            .find("#" + self.env.pos.db.order_line_by_id[pos_order_line].id)
                            .addClass("show_order_detail");
                    });
                }
            }
        }
        return_order_filter() {
            var self = this;
            var previous_order = self.env.pos.db.all_order;
            if (!$(".return_order_button").hasClass("highlight")) {
                self.order_no_return = [];
                $(".return_order_button").addClass("highlight");
                
                self.return_filter = true;
                $('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.all_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                $('.sh_pagination').pagination('selectPage', 1);
            } else {
                self.return_order = [];
                $(".return_order_button").removeClass("highlight");
                self.return_filter = false;
                $('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.all_non_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                $('.sh_pagination').pagination('selectPage', 1);
            }
            self.render();
        }
        reorder_pos_order(event) {
            var self = this;
            var order_id = event.currentTarget.closest("tr").attributes[0].value;

            var order_data = self.env.pos.db.order_by_uid[order_id];
            if (!order_data) {
                order_data = self.env.pos.db.order_by_id[order_id];
            }
            var order_line = [];

            if (self.env.pos.get_order() && self.env.pos.get_order().get_orderlines() && self.env.pos.get_order().get_orderlines().length > 0) {
                var orderlines = self.env.pos.get_order().get_orderlines();
                _.each(orderlines, function (each_orderline) {
                    if (self.env.pos.get_order().get_orderlines()[0]) {
                        self.env.pos.get_order().remove_orderline(self.env.pos.get_order().get_orderlines()[0]);
                    }
                });
            }

            var current_order = self.env.pos.get_order();

            _.each(order_data.lines, function (each_order_line) {
                var line_data = self.env.pos.db.order_line_by_id[each_order_line];
                if (!line_data) {
                    line_data = self.env.pos.db.order_line_by_uid[each_order_line[2].sh_line_id];
                }
                var product = self.env.pos.db.get_product_by_id(line_data.product_id[0]);
                if (!product) {
                    product = self.env.pos.db.get_product_by_id(line_data.product_id);
                }
                current_order.add_product(product, {
                    quantity: line_data.qty,
                    price: line_data.price_unit,
                    discount: line_data.discount,
                });
            });
            if (order_data.partner_id[0]) {
                self.env.pos.get_order().set_client(self.env.pos.db.get_partner_by_id(order_data.partner_id[0]));
            }
            current_order.assigned_config = order_data.assigned_config;
            self.trigger("close-temp-screen");
        }
        print_pos_order(event) {
            var self = this;
            var order_id = event.currentTarget.closest("tr").attributes[0].value;
            var order_data = self.env.pos.db.order_by_uid[order_id];
            if (!order_data) {
                order_data = self.env.pos.db.order_by_id[order_id];
            }
            var order_line = [];

            if (self.env.pos.get_order() && self.env.pos.get_order().get_orderlines() && self.env.pos.get_order().get_orderlines().length > 0) {
                var orderlines = self.env.pos.get_order().get_orderlines();
                _.each(orderlines, function (each_orderline) {
                    if (self.env.pos.get_order().get_orderlines()[0]) {
                        self.env.pos.get_order().remove_orderline(self.env.pos.get_order().get_orderlines()[0]);
                    }
                });
            }

            var current_order = self.env.pos.get_order();

            _.each(order_data.lines, function (each_order_line) {
                var line_data = self.env.pos.db.order_line_by_id[each_order_line];
                if (!line_data) {
                    line_data = self.env.pos.db.order_line_by_uid[each_order_line[2].sh_line_id];
                }
                var product = self.env.pos.db.get_product_by_id(line_data.product_id[0]);
                if (!product) {
                    product = self.env.pos.db.get_product_by_id(line_data.product_id);
                }
                current_order.add_product(product, {
                    quantity: line_data.qty,
                    price: line_data.price_unit,
                    discount: line_data.discount,
                });
            });
            current_order.name = order_data.pos_reference;
            current_order.assigned_config = order_data.assigned_config;
            self.trigger("close-temp-screen");
            self.showScreen("ReceiptScreen");
        }
        return_pos_order(event) {
            var self = this;
            self.env.pos.is_return = true;
            self.env.pos.is_exchange = false;
            var order_line = [];
            var order_id = event.currentTarget.closest("tr").attributes[0].value;
            if (order_id) {
                var order_data = self.env.pos.db.order_by_uid[order_id];
                if (!order_data) {
                    order_data = self.env.pos.db.order_by_id[order_id];
                }
                if (order_data && order_data.lines) {
                    _.each(order_data.lines, function (each_order_line) {
                        var line_data = self.env.pos.db.order_line_by_id[each_order_line];
                        if (!line_data) {
                            line_data = self.env.pos.db.order_line_by_uid[each_order_line[2].sh_line_id];
                        }
                        if (line_data) {
                            order_line.push(line_data);
                        }
                    });
                }
            }
            let { confirmed, payload } = this.showPopup("TemplateReturnOrderPopupWidget", { lines: order_line, order: order_id });
            if (confirmed) {
            } else {
                return;
            }
        }
        exchange_pos_order(event) {
            var self = this;
            self.env.pos.is_return = false;
            self.env.pos.is_exchange = true;

            var order_line = [];
            var order_id = event.currentTarget.closest("tr").attributes[0].value;
            if (order_id) {
                var order_data = self.env.pos.db.order_by_uid[order_id];
                if (!order_data) {
                    order_data = self.env.pos.db.order_by_id[order_id];
                }
                if (order_data && order_data.lines) {
                    _.each(order_data.lines, function (each_order_line) {
                        var line_data = self.env.pos.db.order_line_by_id[each_order_line];
                        if (!line_data) {
                            line_data = self.env.pos.db.order_line_by_uid[each_order_line[2].sh_line_id];
                        }
                        if (line_data) {
                            order_line.push(line_data);
                        }
                    });
                }
            }

            let { confirmed, payload } = this.showPopup("TemplateReturnOrderPopupWidget", { lines: order_line, order: order_id });
            if (confirmed) {
            } else {
                return;
            }
        }
        mounted(){
        	var self = this
        	$(".sh_pagination").pagination({
      			pages:Math.ceil(self.env.pos.order_length / self.env.pos.config.sh_how_many_order_per_page),
      			displayedPages:1,
      			edges:1,
      			cssStyle: "light-theme",
      			showPageNumbers: false,
      		    showNavigator: true,
      			onPageClick: function(pageNumber) { 
      				
      				try {
      					if(!self.return_filter){
      						
      						rpc.query({
        	                    model: "pos.order",
        	                    method: "search_return_order",
        	                    args: [self.env.pos.config,pageNumber+1]
        	                }).then(function (orders) {
        	                	if(orders){
        	                		if(orders['order'].length == 0){
        	                			$($('.next').parent()).addClass('disabled')
        	                			$(".next").replaceWith(function(){
        	                		        $("<span class='current next'>Next</span>");
        	                		    });
        	                		}
        	                	}
        	                	
        	                }).catch(function (reason) {
        	                    
        	                });
      						
      						rpc.query({
        	                    model: "pos.order",
        	                    method: "search_return_order",
        	                    args: [self.env.pos.config,pageNumber]
        	                }).then(function (orders) {
        	                	self.env.pos.db.all_order = [];
        	                	self.env.pos.db.order_by_id = {};
        	                	
        	                	if(orders){
        	                		if(orders['order']){
        	                            self.env.pos.db.all_orders(orders['order']);
        	                		}
        	                		if(orders['order_line']){
        	                			self.env.pos.db.all_orders_line(orders['order_line']);
        	                		}
        	                	}
        	                	self.all_order = self.env.pos.db.all_order;
        	                	
        	                	self.render()
        	                }).catch(function (reason) {
        	                    var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(pageNumber) - 1)
        	                    var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page)
        	                    self.env.pos.db.all_order = self.env.pos.db.all_non_return_order.slice(showFrom, showTo)
        	                    self.env.pos.db.all_display_order = self.env.pos.db.all_order;
        	                    self.all_order = self.env.pos.db.all_order;
        	                    self.render()
        	                });
      						
      					}else{
      						rpc.query({
        	                    model: "pos.order",
        	                    method: "search_return_exchange_order",
        	                    args: [self.env.pos.config,pageNumber+1]
        	                }).then(function (orders) {
        	                	if(orders){
        	                		if(orders['order'].length == 0){
        	                			$($('.next').parent()).addClass('disabled')
        	                			$(".next").replaceWith(function(){
        	                		        $("<span class='current next'>Next</span>");
        	                		    });
        	                		}
        	                	}
        	                }).catch(function (reason) {
        	                	
        	                	var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(pageNumber + 1) - 1)
        	                    var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page)
        	                    var order = self.env.pos.db.all_return_order.slice(showFrom, showTo)
        	                    if(order && order.length == 0){
        	                    	$($('.next').parent()).addClass('disabled')
    	                			$(".next").replaceWith(function(){
    	                		        $("<span class='current next'>Next</span>");
    	                		    });
        	                    }
        	                	
        	                });
      						
      						rpc.query({
        	                    model: "pos.order",
        	                    method: "search_return_exchange_order",
        	                    args: [self.env.pos.config,pageNumber]
        	                }).then(function (orders) {
        	                	self.env.pos.db.all_order = [];
        	                	self.env.pos.db.order_by_id = {};
        	                	
        	                	if(orders){
        	                		if(orders['order']){
        	                            self.env.pos.db.all_orders(orders['order']);
        	                		}
        	                		if(orders['order_line']){
        	                			self.env.pos.db.all_orders_line(orders['order_line']);
        	                		}
        	                	}
        	                	self.all_order = self.env.pos.db.all_order;
        	                	self.env.pos.db.all_display_order = self.env.pos.db.all_order;
        	                	self.render()
        	                }).catch(function (reason) {
        	                    
        	                    var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(pageNumber) - 1)
        	                    var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page)
        	                    self.env.pos.db.all_order = self.env.pos.db.all_return_order.slice(showFrom, showTo)
        	                    self.all_order = self.env.pos.db.all_order;
        	                    self.render()
        	                    
        	                });
      					}
      					
      				} catch (error) {
      	            }
      				
      			}
      		});
        	super.mounted()
        	if(!self.return_filter){
        		$('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.all_non_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
        	}else{
        		$('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.all_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
        	}
        	$('.sh_pagination').pagination('selectPage', 1);
        }
    }
    OrderListScreen.template = "OrderListScreen";
    Registries.Component.add(OrderListScreen);

    const PosReturnPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
            }
            cancel_return_order() {
                var self = this;

                if (this.env.pos.get_order() && this.env.pos.get_order().get_orderlines() && this.env.pos.get_order().get_orderlines().length > 0) {
                    var orderlines = this.env.pos.get_order().get_orderlines();
                    _.each(orderlines, function (each_orderline) {
                        if (self.env.pos.get_order().get_orderlines()[0]) {
                            self.env.pos.get_order().remove_orderline(self.env.pos.get_order().get_orderlines()[0]);
                        }
                    });
                }
                self.env.pos.get_order().is_return_order(false);
                self.env.pos.get_order().return_order = false;
                self.env.pos.get_order().is_exchange_order(false);
                self.env.pos.get_order().exchange_order = false;
                self.env.pos.get_order().set_old_pos_reference(false);
                self.showScreen("ProductScreen");
            }
            async _finalizeValidation() {
            	var self = this
                if (this.currentOrder.is_paid_with_cash() && this.env.pos.config.iface_cashdrawer) {
                    this.env.pos.proxy.printer.open_cashbox();
                }

                this.currentOrder.initialize_validation_date();
                this.currentOrder.finalized = true;

                let syncedOrderBackendIds = [];

                try {
                    if (this.currentOrder.is_to_invoice()) {
                        syncedOrderBackendIds = await this.env.pos.push_and_invoice_order(this.currentOrder);
                    } else {
                        syncedOrderBackendIds = await this.env.pos.push_single_order(this.currentOrder);
                    }
                } catch (error) {
                    if (error instanceof Error) {
                        throw error;
                    } else {
                        await this._handlePushOrderError(error);
                    }
                }
                if (syncedOrderBackendIds.length && this.currentOrder.wait_for_push_order()) {
                    const result = await this._postPushOrderResolve(this.currentOrder, syncedOrderBackendIds);
                    if (!result) {
                        await this.showPopup("ErrorPopup", {
                            title: "Error: no internet connection.",
                            body: error,
                        });
                    }
                }
                if (this.currentOrder.return_order) {
                    this.currentOrder.is_return_order(true);
                    if (this.currentOrder.old_pos_reference) {
                        this.currentOrder.set_old_pos_reference(this.currentOrder.old_pos_reference);
                        this.currentOrder.set_old_sh_uid(this.currentOrder.old_sh_uid);
                    }
                }
                if (this.currentOrder.exchange_order) {
                    this.currentOrder.is_exchange_order(true);
                    if (this.currentOrder.old_pos_reference) {
                        this.currentOrder.set_old_pos_reference(this.currentOrder.old_pos_reference);
                        this.currentOrder.set_old_sh_uid(this.currentOrder.old_sh_uid);
                    }
                }
                this.showScreen(this.nextScreen);

                // If we succeeded in syncing the current order, and
                // there are still other orders that are left unsynced,
                // we ask the user if he is willing to wait and sync them.
                if (syncedOrderBackendIds.length && this.env.pos.db.get_orders().length) {
                    const { confirmed } = await this.showPopup("ConfirmPopup", {
                        title: this.env._t("Remaining unsynced orders"),
                        body: this.env._t("There are unsynced orders. Do you want to sync these orders?"),
                    });
                    if (confirmed) {
                        // NOTE: Not yet sure if this should be awaited or not.
                        // If awaited, some operations like changing screen
                        // might not work.
                        this.env.pos.push_orders();
                    }
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PosReturnPaymentScreen);

    return { OrderListScreen, PosReturnPaymentScreen };
});
