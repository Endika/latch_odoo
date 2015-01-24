# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2015 Endika Iglesias <endika2@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv


class latch_config_settings(osv.TransientModel):
    _name = 'latch.config.settings'
    _inherit = 'res.config.settings'
    _columns = {
        'app_id': fields.char('App id'),
        'secret_key': fields.char('Secret key'),
    }

    def get_default_conf(self, cr, uid, fields, context=None):
        conf_par = self.pool.get('ir.config_parameter')
        app_id = conf_par.get_param(cr, uid,
                                    'latch_odoo.app_id',
                                    default="",
                                    context=context)
        secret_key = conf_par.get_param(cr, uid,
                                        'latch_odoo.secret_key',
                                        default="",
                                        context=context)

        return {'app_id': app_id, 'secret_key': secret_key}

    def set_app_id(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            app_id = record.app_id
            config_parameters.set_param(cr, uid,
                                        'latch_odoo.app_id',
                                        app_id,
                                        context=context)

    def set_secret_key(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            secret_key = record.secret_key
            config_parameters.set_param(cr, uid,
                                        'latch_odoo.secret_key',
                                        secret_key,
                                        context=context)
