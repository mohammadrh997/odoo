from odoo import models, fields


class EaglePropertyRoom(models.Model):
    _name = 'eagle.property.room'
    _description = 'Eagle Property Room'
    _rec_name = 'property_id'

    type = fields.Selection([('bedroom', 'Bedroom'), ('bathroom', 'Bathroom'), ('dining', 'Dining Room'),
                             ('living', 'Living Room'), ('garage', 'Garage'), ('kitchen', 'Kitchen'),
                             ('other', 'Other')], default="other")
    surface = fields.Float('Surface')
    property_id = fields.Many2one('eagle.property')

    street = fields.Char(related='property_id.street')
    zip = fields.Char(related='property_id.zip')
    city = fields.Char(related='property_id.city')
    state_id = fields.Many2one(related='property_id.state_id')
    country_id = fields.Many2one(related='property_id.country_id')

    construction_date = fields.Date(related='property_id.construction_date')


    def calculate_area(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "room.area",
            "view_mode": "form",
            "target": "new",
            "context": {"default_room_id": self.id,"default_area": self.surface}
        }
