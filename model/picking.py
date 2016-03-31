from openerp import models,api
from datetime import datetime
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.float_utils import float_compare, float_round

 
class stock_delivery_labels(models.Model):
    _inherit = ['stock.picking']
  
    def get_report_data_picking_lists_out_from_partner(self, delivery_id, partner):
        cr = self.env.cr
        uid = self.env.user.id
        stock_picking_obj = self.pool.get('stock.picking')
        stock_picking_type_obj = self.pool.get('stock.picking.type')
        stock_picking_type_ids = stock_picking_type_obj.search(cr, uid, [('code','=','outgoing')],)

        current_picking_ids = stock_picking_obj.search(cr, uid, [('partner_id','=',partner.id),('picking_type_id','in',stock_picking_type_ids), ('id', '=', delivery_id)], order="date_done desc", limit=1)

        open_stock_picking_ids = stock_picking_obj.search(cr, uid, [('partner_id','=',partner.id),('picking_type_id','in',stock_picking_type_ids),('state','in',['confirmed','partially_available']), ('id', '!=', delivery_id)], order="date desc")
        
        picking_ids = []
        if current_picking_ids:
            picking_ids.extend(current_picking_ids)
        if open_stock_picking_ids:
            picking_ids.extend(open_stock_picking_ids)
        
        result = []
        
        move_state_dict = {'waiting':'Waiting Another Move',
                           'confirmed':'Waiting Avaibility',
                           'assigned':'Available',
                           'done':'Transferred',
                            }
        picking_state_dict = {'waiting':'Waiting Another Operation',
                              'confirmed':'Waiting Avaibility',
                              'assigned':'Ready to transfer',
                              'partially_available':'Partially Available',
                              'done':'Transferred',
                                }
        if picking_ids:
            for picking in stock_picking_obj.browse(cr, uid, picking_ids):
                picking_dict = {}
                picking_dict['name'] = picking.name
                picking_dict['origin'] = picking.origin
                
                if picking.state in picking_state_dict:
                    picking_dict['state'] = picking_state_dict[picking.state]
                else:
                    picking_dict['state'] = picking.state
                
                if picking.backorder_id:
                    picking_dict['backorder'] = picking.backorder_id.name
                else:
                    picking_dict['backorder'] = False
                 
                picking_dict['moves'] = []
                for move in picking.move_lines:
                    move_dict = {   'name':move.product_id.name,
                                    'brand':move.product_id.product_brand_id.name,
                                    'full_name':str(move.product_id.product_brand_id.name) + " - " + move.product_id.name,
                                    'ean13':move.product_id.ean13,
                                    'ref':move.product_id.default_code,
                                    'qty': move.product_uom_qty,
                                    'uom':move.product_uom.name,
                                    'date':move.date,
                                }
                    
                    if move.state in move_state_dict:
                        move_dict['state'] = move_state_dict[move.state]
                    else:
                        move_dict['state'] = move.state
                    
                    picking_dict['moves'].append(move_dict)
                
                
                picking_dict['moves'] = sorted(picking_dict['moves'], key=lambda k: k['full_name']) 
                result.append(picking_dict)
        return result
