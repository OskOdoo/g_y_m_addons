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



class situation_client(models.AbstractModel):
	_name = "situation.client"

	_order='name desc'

	date_debut = fields.Date('Date debut')
	date_fin = fields.Date('Date fin',default=fields.Datetime.now)
	adherent = fields.Many2one('gym.adherent','Client')
	reste = fields.Float('Recettes',readonly=True)
	nombre_paiem = fields.Integer('Nombre de paiements effectués',readonly=True)
	liste_client = fields.Text('Liste clients',default='',size=24)

	@api.one
	@api.onchange('date_debut','date_fin','adherent')
	def get_all_paiement_effectuee(self):
		cmpt = 0
		if self.adherent:
			abonnement = self.env[('paiement.abonnement')].search([('date_facture','>=',self.date_debut),('date_facture','<=',self.date_fin),('adherent','=',self.adherent.id),('reste_a_payer','!=',0.0),('state','!=','cancel')])
		else:
			abonnement = self.env[('paiement.abonnement')].search([('date_facture','>=',self.date_debut),('date_facture','<=',self.date_fin),('reste_a_payer','!=',0.0),('state','!=','cancel')])

		for record in abonnement:	
			cmpt += 1
		self.nombre_paiem = cmpt
		return self.nombre_paiem


	###################################################################
	@api.one
	@api.onchange('date_debut','date_fin','adherent')
	def get_all_paiement(self):
		total_gain = 0.0
		liste = ""
		if self.adherent:
			abonnement = self.env[('paiement.abonnement')].search([('date_facture','>=',self.date_debut),('date_facture','<=',self.date_fin),('adherent','=',self.adherent.id),('reste_a_payer','!=',0.0)])
		else:
			abonnement = self.env[('paiement.abonnement')].search([('date_facture','>=',self.date_debut),('date_facture','<=',self.date_fin),('reste_a_payer','!=',0.0)])
		if abonnement:
			for record in abonnement:
					total_gain += record.reste_a_payer
					liste += "Facture: "+str(record.name)+" Client: "+"<strong>"+str(record.adherent.name)+"</strong>"+"  Reste: "+"<strong>"+str(record.reste_a_payer)+"</strong>"+"<br/>"+"___________________"+"<br/>"
		self.liste_client = liste			
		self.reste = total_gain
		return  True
