from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class stock_order_form(models.TransientModel):
    _name = "stock.order.form"
    
    partner_invoice_id = fields.Many2one('res.partner',string="Invoice address")
    partner_shipping_id = fields.Many2one('res.partner',string="Shipping address")
    picking_ids = fields.Many2many('stock.picking',string="Picking lists")
    
    #Used in the report 
    def get_stock_move_state(self, stock_move_state):
        move_state_dict = {'waiting':'Waiting Another Move',
                           'confirmed':'Waiting Avaibility',
                           'assigned':'Available',
                           'done':'Transferred',
                            }
        if stock_move_state in move_state_dict:
            return move_state_dict[stock_move_state]
        else:
            return stock_move_state
    
    #Used in the report                
    def get_stock_picking_state(self, stock_picking_state):
        picking_state_dict = {'waiting':'Waiting Another Operation',
                              'confirmed':'Waiting Avaibility',
                              'assigned':'Ready to transfer',
                              'partially_available':'Partially Available',
                              'done':'Transferred',
                                }
        if stock_picking_state in picking_state_dict:
            return picking_state_dict[stock_picking_state]
        else:
            return stock_picking_state                   