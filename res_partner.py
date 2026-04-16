# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    """
    Extends res.partner to identify professional customers and automate 
    their access to specific website pricelists.
    """
    _inherit = "res.partner"

    is_professional = fields.Boolean(string="Is Professional")

    def write(self, vals):
        """
        Overrides write to detect when a partner becomes 'professional'.
        If so, it ensures all associated users are added to all existing 
        pricelist switch assignments.
        """
        res = super().write(vals)
        if vals.get('is_professional'):
            # If partner becomes professional, add all its users to ALL pricelist switch records
            for partner in self:
                users = partner.user_ids
                if users:
                    # sudo() used to ensure assignments can be updated regardless of user permissions
                    assignments = self.env['app.tegel.be.pricelist'].sudo().search([])
                    if assignments:
                        # Link newly professional users to all switch records
                        assignments.write({'user_ids': [(4, user_id) for user_id in users.ids]})
        return res

class ResUsers(models.Model):
    """
    Extends res.users to handle automatic pricelist switch assignment 
    during user creation or partner reassignment.
    """
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides create to check if the new user belongs to a professional 
        partner. If yes, it adds the user to all pricelist switch assignments.
        """
        users = super().create(vals_list)
        for user in users:
            if user.partner_id.is_professional:
                assignments = self.env['app.tegel.be.pricelist'].sudo().search([])
                if assignments:
                     assignments.write({'user_ids': [(4, user.id)]})
        return users

    def write(self, vals):
        """
        Overrides write to check if a user is reassigned to a professional 
        partner. If so, it updates their pricelist switch access.
        """
        res = super().write(vals)
        if 'partner_id' in vals:
            for user in self:
                if user.partner_id.is_professional:
                    assignments = self.env['app.tegel.be.pricelist'].sudo().search([])
                    if assignments:
                        assignments.write({'user_ids': [(4, user.id)]})
        return res
