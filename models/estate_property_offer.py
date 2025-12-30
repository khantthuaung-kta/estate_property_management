from odoo import models, fields, api
from odoo import _
import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = "price desc"

    price = fields.Float('Price')
    status = fields.Selection(
        selection=[('accepted', 'Accepted'),
                   ('refused', 'Refused'),
                   ],
                   copy=False
    )
    partner_id = fields.Many2one('res.partner', required= True , string='Partner')
    property_id = fields.Many2one('estate.property', required=True, ondelete='cascade')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)
    validity = fields.Integer( 'Validity', default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    _sql_constraints = [
        ('check_price', 'CHECK(price >= 0)',
         'The offer price must be strictly postive')
    ]

    @api.model
    def create(self, vals):
        property_obj = self.env['estate.property'].browse(vals['property_id'])
        property_obj.write({'state': 'received'})
        for offer in property_obj.offer_ids:
            if offer.price > vals['price']:
                raise UserError(_("Your price is must be greather than %s", offer.price))
        return super(EstatePropertyOffer, self).create(vals)

    @api.depends("validity")
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = datetime.timedelta(days=rec.validity) + fields.Date.today()
        
    def _inverse_date_deadline(self):
        for rec in self:
            day_count = (rec.date_deadline - fields.Date.today()).days
            rec.validity = day_count

    def action_accepted(self):
        self.property_id.partner_id = self.partner_id.id
        self.property_id.selling_price = self.price
        self.status = 'accepted'
        expected_percentage = self.property_id.expected_price * (90 / 100)
        if self.price == 0:
                raise UserError(_("Your price is must be greather than %s", expected_percentage))

    
    def action_refused(self):
        self.status = 'refused'

