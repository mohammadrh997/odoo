from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'


    property_id = fields.Many2one('eagle.property', string='Rooms')
