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



class AccountOrdre(models.Model):
	 
	_inherit = "account.ordre"



	description = fields.Text('Description')


class sale_order(models.Model):
	 
	_inherit = "sale.order"
	_mode_paiement = [
	('jours','Par Jour'),
	('mois', 'Par Mois'),
	('seance', 'Par séance')
	]

	@api.depends('jusqua')
	def _compute_solde(self):
		for record in self:
			dt = str(date.today())
			
			result = 0
			if record.jusqua and dt < record.jusqua:
						d1 = datetime.strptime(dt, "%Y-%m-%d")
						d2 = datetime.strptime(record.jusqua, "%Y-%m-%d")
						delta = abs((d2 - d1).days)
						result = delta
						if record.solde_jour and record.mode_p == 'jours' and delta >= record.solde_jour:
							res = (delta - record.solde_jour)
							result = delta - res                    
			else:
						result = 0
			record.solde = result
			return result


	
	def get_ordre_abonnement(self):
		id_returned = False
		res = self.env.cr.execute('select "id" from "account_ordre" order by "id" desc limit 1')
		if res:
			self.env.cr.fetchone()
		else: 
			return self.env.ref('import_data.ordre_one')
			
	

	@api.model		
	def _default_ordre_abonnement(self):
		
		return self.get_ordre_abonnement()


	@api.onchange('ordre_id')
	def onchange_date_debut(self):
		self.debut = self.ordre_id.date_debut			
		self.jusqua  = self.ordre_id.date_fin


 
	@api.multi
	@api.depends('jusqua')
	def _compute_cpmt(self):
		dt = str(date.today())
		for record in self:
			if record.debut and record.jusqua and dt > record.jusqua :
					d1 = datetime.strptime(dt, "%Y-%m-%d")
					d2 = datetime.strptime(record.jusqua, "%Y-%m-%d")
					record.cmpt = (d2 - d1).days

	ordre_id = fields.Many2one('account.ordre','Ordre du mois',default= lambda self: self._default_ordre_abonnement() )
	mode_p =fields.Selection(_mode_paiement,'Mode paiement',default='mois')
	child= fields.Many2one('gym.adherent','Enfant',required=True)
	debut = fields.Date('Depuis' )#, default=get_date_debut)
	jusqua = fields.Date('jusqu\' à')# , default=get_date_fin)
	solde = fields.Integer(compute='_compute_solde')
	cmpt = fields.Integer('Retardement',compute='_compute_cpmt')
	nb_mois = fields.Float(compute='get_total_mois')
	solde_jour = fields.Integer('Nombre jours')
	state_ab = fields.Selection([('draft','Brouillon'),('open','En cours'),('expired','Expiré'),('archived','Archivé')],string='Etat abonnement',default='draft')
	name= fields.Char('N° Abonnement', required=True, copy=False,
			 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True)

	



	def get_total_mois(self,debut,fin):
		nb_mois= 0
		d1 = datetime.strptime(fin, "%Y-%m-%d")
		d2 = datetime.strptime(debut, "%Y-%m-%d")
		delta = 0
		if d1 and d2 and self.mode_p == 'jours':

			delta = self.solde_jour/30.0


		if self.mode_p == 'mois':
			delta = d1.month - d2.month
		if d1 > d2 :
			nb_mois = float((d1.year - d2.year)*12) + delta
		self.nb_mois = nb_mois
		return nb_mois

	@api.onchange('jusqua','debut')
	def verifier_date(self):
		dt = str(date.today())
		for record in self:
			if record.debut and record.jusqua:
				record.nb_mois = self.get_total_mois(record.debut,record.jusqua)
				
			# if record.debut > record.jusqua:
			# 	raise osv.except_osv(
			# 		_('Attention!'),
			# 		_('Date debut est supperieur au date Fin !.'))
			if  record.jusqua < dt:
				record.solde = 0
				raise osv.except_osv(
					_('Attention!'),
					_('Date Fin est Inferieure a la date d\'aujourd\'hui !.'))