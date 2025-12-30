from odoo import _, models, fields, api
import logging
from odoo.exceptions import AccessError, UserError, ValidationError
_logger = logging.getLogger(__name__)

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = "id desc"

    name = fields.Char('Title' )
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Available Form', default=lambda self: fields.Datetime.now(), copy=False)
    expected_price = fields.Float('Expected Price')
    best_price = fields.Float('Best Offer', compute='_compute_best_price')
    selling_price = fields.Float('Selling Price' , readonly=True, copy=False)
    bedrooms = fields.Integer('Bedrooms', default=2)
    living_area = fields.Integer('Living Area(sqm)')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area')
    facades = fields.Integer('Facades')
    garden_orientation = fields.Selection(
        # string='Type',
        selection=[('north', 'North'),
                   ('south', 'South'),
                   ('east', 'East'),
                   ('west', 'West')]
        )
    total_area = fields.Integer('Total Area(spm)', compute='_compute_total_area', store=True)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
        ('new', 'New'),
        ('received', 'Offer Received'),
        ('accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancel', 'Cancelled'),
        ], string='Status', required=True, copy=False, default='new'
    )
    property_type_id = fields.Many2one('estate.property.type', 'Property Type')
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner' , string='Buyer', copy=False)
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    company_id = fields.Many2one('res.company', 'Company', required=False) 

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)',
         'The expected price must be postive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)',
         'The selling price must be postive')
    ]

    @api.constrains('selling_price','expected_price')
    def _check_selling_and_expected_price(self):
        for record in self:
            expected_percentage = record.expected_price * (90 / 100)
            if record.selling_price > 0:
                if record.selling_price < expected_percentage:
                    raise ValidationError("The Selling Price must be at least 90% of the expected price.")

    @api.ondelete(at_uninstall=False)
    def _unlink_except_new_or_cancel(self):
        for record in self:
            if record.state not in ('new', 'cancel'):
                raise UserError(_('You can not delete new and cancel state. You must first cancel it.'))
    
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for rec in self:
            if rec.offer_ids:
                for offer in rec.offer_ids:
                    if rec.best_price < offer.price:
                        rec.best_price = offer.price
                    else:
                        rec.best_price = rec.best_price
            else:
                rec.best_price = 0
        
    @api.onchange("garden")
    def _onchange_garden(self):
        for rec in self:
            if rec.garden:
                rec.garden_area = 10
                rec.garden_orientation = 'north'
            else:
                rec.garden_area = 0
                rec.garden_orientation = False

    def action_received(self):
        for rec in self:
            rec.state = 'received'

    def action_accepted(self):
        for rec in self:
            rec.state = 'accepted'

    def action_sold(self):
        for rec in self:
            if rec.state == 'cancel':
                raise UserError(_('Canceled property can not be sold.'))
            rec.state = 'sold'
        
    def action_cancel(self):
        for rec in self:
            if rec.state == 'sold':
                raise UserError(_('Sold property can not be sold.'))
            rec.state = 'cancel'

    def action_new(self):
        for rec in self:
            rec.state = 'new'

    def action_sold(self):
        for rec in self:
            if rec.state == 'cancel':
                raise UserError(_('Canceled property can not be sold.'))
            rec.state = 'sold'

    def action_cancel(self):
        for rec in self:
            if rec.state == 'sold':
                raise UserError(_('Sold property can not be cancel.'))
            rec.state = 'cancel'
