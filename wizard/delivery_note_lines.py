from openerp import models, fields, api, _
import datetime
import logging
_logger = logging.getLogger(__name__)

class delivery_note_line(models.TransientModel):
    _name = "delivery.note.line"
    stock_move = fields.Many2one('stock.move',string='Stock move')
    product_name = fields.Char(string='Product', related='stock_move.product_id.name', readonly=True)
    ordered_product_qty = fields.Float(string='Ordered quantity', related='stock_move.product_qty', readonly=True)
    available_product_qty = fields.Float(string='Available Quantity', related='stock_move.product_id.qty_available', readonly=True)

class delivery_note_lines(models.TransientModel):
    _name = "delivery.note.lines"
    partner_id = fields.Many2one('res.partner',string="Customer")
    line_ids = fields.Many2many('delivery.note.line',string='Product lines')

    @api.onchange('partner_id')
    def onchange_customer(self):
        cr = self.env.cr
        uid = self.env.uid
        
        res_partner_obj = self.pool.get('res.partner')
        
        partner_ids = self.getAllChildrenAndParentsOfResPartner(self.partner_id.id)
       
        stock_picking_obj = self.pool.get('stock.picking')
        
        #check avaibility
        stock_picking_ids = stock_picking_obj.search(cr, uid, [('partner_id', 'in', partner_ids),('state', '=', 'confirmed')])
        if stock_picking_ids:
            stock_picking_obj.action_assign(cr, uid, stock_picking_ids)
        
        line_ids = []
        
        stock_picking_ids = stock_picking_obj.search(cr, uid, [('partner_id', 'in', partner_ids),('state', 'in', ['assigned','partially_available'])])
        if stock_picking_ids:
            stock_delivery_note_report_product_line_obj = self.pool.get('delivery.note.line')
            
            
            for picking in stock_picking_obj.browse(cr,uid,stock_picking_ids):
                for move_line in picking.move_lines:
                    #if the move is available
                    if move_line.state == 'assigned':
                        line_id = stock_delivery_note_report_product_line_obj.create(cr, uid, {'stock_move': move_line.id})
                        line_ids.append(line_id)
        
        self.line_ids = line_ids
        
    def update_line_ids(self, cr, uid, partner_id, delivery_note_lines_id):
        res_partner_obj = self.pool.get('res.partner')
        
        partner_ids = self.getAllChildrenAndParentsOfResPartner(cr, uid, partner_id)
        
        
        stock_picking_obj = self.pool.get('stock.picking')
        
        #check avaibility
        stock_picking_ids = stock_picking_obj.search(cr, uid, [('partner_id', 'in', partner_ids),('state', '=', 'confirmed')])
        if stock_picking_ids:
            stock_picking_obj.action_assign(cr, uid, stock_picking_ids)
        
        line_ids = []
        
        stock_picking_ids = stock_picking_obj.search(cr, uid, [('partner_id', 'in', partner_ids),('state', 'in', ['assigned','partially_available'])])
        if stock_picking_ids:
            stock_delivery_note_report_product_line_obj = self.pool.get('delivery.note.line')
            
            
            for picking in stock_picking_obj.browse(cr,uid,stock_picking_ids):
                for move_line in picking.move_lines:
                    #if the move is available
                    if move_line.state == 'assigned':
                        line_id = stock_delivery_note_report_product_line_obj.create(cr, uid, {'stock_move': move_line.id})
                        line_ids.append(line_id)
        
        delivery_note_lines = self.pool.get('delivery.note.lines').browse(cr, uid, delivery_note_lines_id)
        delivery_note_lines.line_ids = line_ids

    def transfer_products_and_create_delivery_note(self, cr, uid, ids, context={}):
        stock_picking_obj = self.pool.get('stock.picking')
        stock_delivery_note_report_product_lines_obj = self.pool.get('delivery.note.lines')
        lines = stock_delivery_note_report_product_lines_obj.browse(cr,uid,ids)
        picking_ids = []
        if lines.line_ids:
            for line in lines.line_ids:
                picking_id = line.stock_move.picking_id.id
                stock_move_id = line.stock_move.id
                
                if picking_id not in picking_ids:
                    picking_ids.append(picking_id)
                
                if line.available_product_qty >= line.ordered_product_qty:
                    product_qty = line.ordered_product_qty
                elif line.available_product_qty < line.ordered_product_qty:
                    product_qty = line.available_product_qty
                                
                stock_picking_obj.transfer_stock_move_of_a_picking(cr, uid, picking_id, stock_move_id, product_qty)
            
            for picking_id in picking_ids:
                picking = stock_picking_obj.browse(cr, uid, picking_id)
                stock_picking_obj._create_backorder(cr, uid, picking, context=context)
            
            parentCustomerId = self.getFirstParentIdOfResPartner(cr, uid, lines.partner_id.id)
            
            stock_delivery_note_report_obj = self.pool.get('stock.delivery.note')
            stock_delivery_note_report_id = stock_delivery_note_report_obj.create(cr, uid, {'partner_shipping_id': lines.partner_id.id, 'partner_invoice_id': parentCustomerId})
            stock_delivery_note_report = stock_delivery_note_report_obj.browse(cr,uid,stock_delivery_note_report_id)
            stock_delivery_note_report.date = datetime.datetime.now()
            stock_delivery_note_report.picking_ids = picking_ids
            
            lines.line_ids = []
            
            return self.pool.get('report').get_action(cr, uid, stock_delivery_note_report_id, 'stock_delivery_note_report.report_delivery_order', context=context)
        return False
        
        
    def transfer_products_and_create_delivery_note_from_partner_id(self,cr, uid, partner_id):
        delivery_note_lines_obj = self.pool.get('delivery.note.lines')
        delivery_note_lines_id = delivery_note_lines_obj.create(cr, uid, {'partner_id': partner_id})
        self.update_line_ids(cr, uid, partner_id, delivery_note_lines_id)
        return self.transfer_products_and_create_delivery_note(cr, uid, delivery_note_lines_id)
        
    def print_last_delivery_note_from_partner_id(self,cr, uid, partner_id):
        delivery_note_lines_obj = self.pool.get('delivery.note.lines')
        delivery_note_lines_id = delivery_note_lines_obj.create(cr, uid, {'partner_id': partner_id})
        return self.print_last_delivery_note(cr, uid, delivery_note_lines_id)
        
    def print_order_form_from_partner_id(self,cr, uid, partner_id):
        delivery_note_lines_obj = self.pool.get('delivery.note.lines')
        delivery_note_lines_id = delivery_note_lines_obj.create(cr, uid, {'partner_id': partner_id})
        return self.print_order_form(cr, uid, delivery_note_lines_id)     
    
    def print_last_delivery_note(self, cr, uid, ids, context=None):
        stock_delivery_note_report_obj = self.pool.get('stock.delivery.note')
        stock_delivery_note_report_product_lines_obj = self.pool.get('delivery.note.lines')
        lines = stock_delivery_note_report_product_lines_obj.browse(cr,uid,ids)
        
        parentCustomerId = self.getFirstParentIdOfResPartner(cr, uid, lines.partner_id.id)

        stock_delivery_note_report_id = stock_delivery_note_report_obj.search(cr, uid, [('partner_invoice_id', '=', parentCustomerId)], limit=1, order='date asc')

        if stock_delivery_note_report_id:
            return self.pool.get('report').get_action(cr, uid, stock_delivery_note_report_id, 'stock_delivery_note_report.report_delivery_order', context=context)
        
        return False
        
    def print_order_form(self, cr, uid, ids, context=None):
        stock_picking_obj = self.pool.get('stock.picking')
        stock_delivery_note_report_product_lines_obj = self.pool.get('delivery.note.lines')
        lines = stock_delivery_note_report_product_lines_obj.browse(cr,uid,ids)
        
        partner_ids = self.getAllChildrenAndParentsOfResPartner(cr, uid, lines.partner_id.id)
        stock_picking_ids = stock_picking_obj.search(cr, uid, [('partner_id', 'in', partner_ids),('state', 'in', ['waiting','confirmed','assigned','partially_available'])])

        partner_shipping_id = lines.partner_id.id
        partner_invoice_id = self.getFirstParentIdOfResPartner(cr, uid, lines.partner_id.id)
        
        stock_order_form_obj = self.pool.get('stock.order.form')
        stock_order_form_id = stock_order_form_obj.create(cr, uid, {'partner_shipping_id': partner_shipping_id, 'partner_invoice_id': partner_invoice_id})
        stock_order_form = stock_order_form_obj.browse(cr,uid,stock_order_form_id)
        stock_order_form.picking_ids = stock_picking_ids

        return self.pool.get('report').get_action(cr, uid, stock_order_form_id, 'stock_delivery_note_report.report_order_form', context=context)

    def getFirstParentIdOfResPartner(self, cr, uid, partner_id):
        res_partner_obj = self.pool.get('res.partner')
        customer_id = partner_id
        customer = res_partner_obj.browse(cr,uid,customer_id)
        hasCustomerParent = True
        #search the first parent
        while(hasCustomerParent):
            if customer.parent_id:
                customer_id = customer.parent_id.id
                customer = res_partner_obj.browse(cr,uid,customer_id)
            else:
                hasCustomerParent = False
        return customer.id
        
    def getAllChildrenAndParentsOfResPartner(self, cr, uid, partner_id):
        partner_ids = []
        res_partner_obj = self.pool.get('res.partner')
        customer_id = self.getFirstParentIdOfResPartner(cr, uid, partner_id)
        customer = res_partner_obj.browse(cr,uid,customer_id)
        
        #adds the first parent
        partner_ids.append(customer.id)
        
        hasCustomerChildren = True
        children_ids = []
        for child in customer.child_ids:
            children_ids.append(child.id)
        
        #takes all the children of the first parent
        while(hasCustomerChildren):
            if len(children_ids)>0:
                children_ids_tmp = []
                for child in res_partner_obj.browse(cr,uid,children_ids):
                    partner_ids.append(child.id)
                    if child.child_ids:
                        for childOfChild in child.child_ids:
                            children_ids_tmp.append(childOfChild.id)
                children_ids = children_ids_tmp
            else:
                hasCustomerChildren = False
        return partner_ids