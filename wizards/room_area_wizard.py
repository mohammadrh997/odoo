from odoo import fields, models,api


class RoomArea(models.TransientModel):
    _name = 'room.area'
    _description = 'Room Area'

    length = fields.Float()
    width = fields.Float()
    area = fields.Float(compute="_compute_area")
    room_id = fields.Many2one('eagle.property.room')

    @api.depends('length','width')
    def _compute_area(self):
        for record in self:
            record.area = record.length * record.width

    def action_confirm(self):
        self.room_id.surface = self.area
        return {'type': 'ir.actions.act_window_close'}

