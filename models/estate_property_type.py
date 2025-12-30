from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = "name asc"

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. House is better.")
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer('Offer Count', compute='_compute_offer_count')

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
        'Name must be unique!')
    ]

    @api.depends('offer_ids')
    def _compute_offer_count(self):
       for rec in self:
            rec.offer_count = len(rec.offer_ids)

    def action_view_offer(self):
        action = self.env["ir.actions.actions"]._for_xml_id("text.action_text_offer")
        
        if self.offer_count > 1:
            action['domain'] = [('id', 'in', self.offer_ids.ids)]
            
        elif self.offer_count == 1:
            form_view = [(self.env.ref('text.text_offer_form').id, 'form')]
            action['views'] = form_view
            action['res_id'] = self.offer_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    