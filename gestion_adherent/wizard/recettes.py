# -*- encoding: utf-8 -*-

from openerp.osv import  osv, orm
import time
from datetime import date
from datetime import datetime
import base64
import xmlrpclib
from openerp import pooler, sql_db , models, api ,fields
from openerp.api import Environment
from openerp.tools.translate import _



class recette_recette(models.AbstractModel):
	_name = "recette.recette"

	_order='name desc'

	date_debut = fields.Date('Date debut')
	date_fin = fields.Date('Date fin',default=fields.Datetime.now)
	recette = fields.Float('Recettes',readonly=True)
	depense = fields.Float('Total Dépenses',readonly=True)
	benfice = fields.Float('Bénéfices',readonly=True)
	nombre_paiem = fields.Integer('Nombre de paiements effectués',readonly=True)
	nombre_achat = fields.Integer("Nombre d'achat effectués",readonly=True)
	total_achat = fields.Float("Cout des achats",readonly=True)
	nb_salaire = fields.Integer("Cout des achats",readonly=True)
	total_salaire = fields.Float("Total des Salaires",readonly=True)
	total_ventes = fields.Float("Total des ventes",readonly=True)
	total_abonnement_payee = fields.Float("Total des paiements",readonly=True)
	nb_ventes = fields.Integer("Nombres des Ventes",readonly=True)

	@api.one
	@api.onchange('date_debut','date_fin')
	def get_all_paiement_effectuee(self):
		cmpt = 0
		abonnement = self.env[('paiement.abonnement')].search([('date_facture','>=',self.date_debut),('date_facture','<=',self.date_fin),('state','!=','cancel')])
		for record in abonnement:	
			cmpt += 1
		self.nombre_paiem = cmpt
		return self.nombre_paiem


	@api.one
	@api.onchange('date_debut','date_fin')
	def get_all_ventes_effectuee(self):
		cmpt = 0
		livraison = self.env[('livraison.repas')].search([('date','>=',self.date_debut),('date','<=',self.date_fin),('state','=','close')])
		for record in livraison:	
			cmpt += 1
		self.nb_ventes = cmpt
		return self.nb_ventes

	###################################################################
	@api.one
	@api.onchange('date_debut','date_fin')
	def get_all_paiement(self):
		total_gain = 0.0
		total_v = 0.0
		abonnement = self.env[('paiement.abonnement')].search([('date_facture','>=',self.date_debut),('date_facture','<=',self.date_fin),('state','!=','cancel')])
		livraison = self.env[('livraison.repas')].search([('date','>=',self.date_debut),('date','<=',self.date_fin),('state','=','close')])

		for record in livraison:
				total_v += record.price
		self.total_ventes = total_v

		for record in abonnement:
				total_gain += record.net_payee
		self.total_abonnement_payee = total_gain

		self.recette = total_gain + total_v
		return  True
	###################################################################

	@api.one
	@api.onchange('date_debut','date_fin')
	def get_all_achat_effectuee(self):
		cmpt = 0
		suma = 0.0
		abonnement = self.env[('depense.depense')].search([('date','>=',self.date_debut),('date','<=',self.date_fin),('type_depense','=','achat')])
		for record in abonnement:	
			cmpt += 1
			suma += record.frais
		self.nombre_achat = cmpt
		self.total_achat = suma
		return True


	@api.one
	@api.onchange('date_debut','date_fin')
	def get_all_salaire_effectuee(self):
		cmpt = 0
		suma = 0.0
		abonnement = self.env[('depense.depense')].search([('date','>=',self.date_debut),('date','<=',self.date_fin),('type_depense','in',('salaire','avance')),('bloc','=',False)])
		for record in abonnement:	
			cmpt += 1
			suma += record.frais
		self.nb_salaire = cmpt
		self.total_salaire = suma
		return True

	@api.one
	@api.onchange('date_debut','date_fin')
	def get_all_depense(self):
		total_dep = 0.0
		
		abonnement = self.env[('depense.depense')].search([('date','>=',self.date_debut),('date','<=',self.date_fin),('bloc','=',False)])
		"""
		raise osv.except_osv(
						_('Attention!'),
						_(str(abonnement)))
		"""
		for record in abonnement:
				total_dep += record.frais
		self.depense = total_dep
		return total_dep


	####################################################################
	@api.one
	@api.onchange('recette','depense','total_ventes')
	def get_all_benifice(self):
		total = 0.0 
		self.benfice = self.recette  - self.depense
		return self.benfice