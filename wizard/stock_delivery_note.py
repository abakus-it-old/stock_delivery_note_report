from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class stock_delivery_note_report(models.Model):
    _name = "stock.delivery.note"
    
    date = fields.Datetime("Date")
    partner_invoice_id = fields.Many2one('res.partner',string="Invoice address")
    partner_shipping_id = fields.Many2one('res.partner',string="Shipping address")
    picking_ids = fields.Many2many('stock.picking',string="Picking lists")