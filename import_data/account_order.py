# -*- encoding: utf-8 -*-

from openerp.osv import  osv, orm
import time
from datetime import date
from datetime import datetime, timedelta
import base64
import xmlrpclib
from openerp import pooler, sql_db , models, api ,fields
from openerp.api import Environment
from openerp.tools.translate import _



class account_ordre(models.Model):
	 
	_name = "account.ordre"
	_order ="id asc"

	name =fields.Char('Titre/Mois')
	date_debut = fields.Date('Date du',default=fields.Datetime.now)
	date_fin = fields.Date('Date au')

	@api.one
	@api.onchange('date_debut')
	def onchange_date_fin(self):
			if self.date_debut:
				self.date_fin = datetime.strptime(str(self.date_debut), "%Y-%m-%d") + timedelta(days=30)
			else:
				raise osv.except_osv(
					_('Attention!'),
					_('Prière de choisir une date debut')
					)

