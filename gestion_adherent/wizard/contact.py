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



class adherent_contact(models.AbstractModel):
	_name = "adherent.contact"

	_order='name desc'

	adherent = fields.Many2one('gym.adherent','Malade')
	resultat = fields.Text('Contacts')


	@api.one
	@api.onchange('adherent')
	def get_all_contact(self):
		liste = ""
		if self.adherent:
			adherent = self.env[('gym.adherent')].search([('id','=',self.adherent.id)])

			liste = "<b style='width:auto;color:blue ; size=90%;  font-size: 25px;  text-shadow: 0px 1px 1px rgba(0, 0, 0, 0.44);'> Père : <b/>"+str(adherent.pere)+"[ "+str(adherent.partner_mobile)+" ] <br/>"
			liste += "<b style='width:auto;color:blue ; size=90%;  font-size: 25px;  text-shadow: 0px 1px 1px rgba(0, 0, 0, 0.44);'> Mère : <b/>"+str(adherent.mere)+"[ "+str(adherent.partner_mobile)+" ] <br/>"
			i=1
			for rec in adherent.parents:
				liste += "<b style='width:auto;color:red ; size=90%;  font-size: 25px;  text-shadow: 0px 1px 1px rgba(0, 0, 0, 0.44);'> Tuteur "+ str(i) +": </b>"+str(rec.name)+" [ "+str(rec.mobile)+" ]["+str(rec.lien)+"]<br/>"
				i+=1
		# else :
		# 	adherent = self.env[('gym.adherent')].search([('id','!=',-1)])

		# 	for rec in adherent:
		# 		liste+="- - - - - - - - - - - - - - - - <br/>"
		# 		liste += "<b style='width:auto;color:blue ; size=90%;  font-size: 25px;  text-shadow: 0px 1px 1px rgba(0, 0, 0, 0.44);'>Malade :</b>" + str(rec.name)+" "+str(rec.prenom)+" <b> Père : <b/>"+str(rec.pere)+"["+str(rec.partner_mobile)+"] <br/>"
		# 		i=1
		# 		for item in rec.parents:
		# 			liste += "<b>Tuteur "+ str(i) +"</b> : "+str(item.name)+" ["+str(item.mobile)+" ]["+str(item.lien)+"]<br/>"
		# 			i+=1
		self.resultat = liste
		return True				
