from odoo import models, fields,api
from odoo.exceptions import ValidationError
from odoo.http import request
import requests
import logging
_logger = logging.getLogger(__name__)


class EagleProperty(models.Model):
    _name = "eagle.property"
    _description = "Eagle Property"
    _order = 'construction_date DESC, id'
    _rec_name = 'name'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string="Property Name", required=True)
    construction_date = fields.Date("Construction Date", required=True, default=fields.Date.today)
    surface = fields.Float("Surface",compute="_compute_area", default=0.0)

    tag_ids = fields.Many2many('eagle.tag', string="Tags")
    room_ids = fields.One2many('eagle.property.room', inverse_name='property_id', string="Rooms")


    street = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    parent_id = fields.Many2one('eagle.property')
    child_ids = fields.One2many('eagle.property',inverse_name='parent_id')

    room_ids_count = fields.Integer(compute="_compute_room")

    @api.depends('room_ids')
    def _compute_room(self):
        for record in self:
            record.room_ids_count = len(record.room_ids)

    age = fields.Integer(compute="_compute_age",tracking=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Property name must be unique'),
    ]

    def action_open_room_ids(self):
        # action = self.env["ir.actions.actions"]._for_xml_id("eagle_estates.eagle_property_rooms_action")
        action = self.env.ref("eagle_estates.eagle_property_rooms_action").sudo().read()[0]
        action['domain'] = [('property_id'  ,'=' ,self.id)]
        return action
    def create_new_room(self):
        # action = self.env["ir.actions.actions"]._for_xml_id("eagle_estates.eagle_property_rooms_action")
        action = self.env.ref("eagle_estates.eagle_property_rooms_action").sudo().read()[0]
        action['context']={"default_property_id": self.id}
        action['views']=[(False,'form')]
        return action

    @api.depends('construction_date')
    def _compute_age(self):
        for record in self:
            record.age=fields.Date.today().year - record.construction_date.year


    @api.depends('room_ids','room_ids.surface')
    def _compute_area(self):
        for record in self:
            record.surface = sum(record.room_ids.mapped('surface'))


    @api.constrains('construction_date')
    def _constraint_con(self):
        for record in self:
            if record.construction_date > fields.Date.today():
                raise ValidationError("error")

    @api.depends('construction_date')
    def _compute_display_name(self):
        for record in self:
            name= record.name
            if record.construction_date:
                name = f"{name}({record.construction_date})"
                # name += " | " + (str(record.construction_date) if record.construction_date else "")
            record.display_name = name



    @api.model
    def _name_search(self, name='', domain=None, operator='ilike', limit=100, order=None):
        if name:
            domain +=['|',('name',operator,name),('construction_date',operator,name)]
        return self._search(domain,limit=limit,order=order)

    usd_to_iqd_rate = fields.Float(
        string="USD to IQD Rate",
        compute="fetch_usd_to_iqd",
        store=False  # You can set this to True if you want the value to be stored in the database
    )

    @api.depends('usd_to_iqd_rate')
    def fetch_usd_to_iqd(self):
        """Fetch exchange rate from an API and update the field."""
        api_url = "https://api.exchangerate-api.com/v4/latest/USD"  # Replace with your API URL
        for record in self:
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    iqd_rate = data['rates'].get('IQD', 0.0)
                    record.usd_to_iqd_rate = iqd_rate  # Set the field value here
                else:
                    record.usd_to_iqd_rate = 0.0  # Default to 0.0 if API fails
            except Exception as e:
                record.usd_to_iqd_rate = 0.0  # Default to 0.0 in case of exception
                _logger.error(f"Error fetching exchange rate: {str(e)}")