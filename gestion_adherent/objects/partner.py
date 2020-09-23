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
import json 
import math

class res_partner(models.Model):
	 

	_inherit = "res.partner"

	_cans_casnos = [
	('cnas_en_caisse','CNAS EN CAISSE'),
	('cnas_hors_caisse', 'CNAS HORS CAISSE'),
	('casnos', 'CASNOS'),
	('caisse_militaire', 'CAISSE MILITAIRE')
	]

	transporteur= fields.Boolean('Est un Transporteur')
	tuteur= fields.Boolean('Est un Tuteur')
	assure= fields.Boolean('Est un Assure',default=True)
	cni = fields.Char('CNI')
	prenom = fields.Char('Prénom')
	securite_s = fields.Char('Sécurité Social')
	date_expir = fields.Date('Date expiration SS')
	date_nais = fields.Date('Date de naissance')
	ldn = fields.Char('Lieu de naissance')
	cnas_casnos = fields.Selection(_cans_casnos,string='Classement')


	@api.one
	def onchange_date_expir(self):
		if self.date_expir < date.today():
			raise osv.except_osv(_('Attention !'), _('La couverture est expiré'))
