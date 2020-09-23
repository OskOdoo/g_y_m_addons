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

class diagnostic_malade(models.Model):
	 

	_name = "diagno.malade"
	_order='date desc'


	name = fields.Char('Référence')
	adherent = fields.Many2one('gym.adherent','Adherent')
	date =fields.Date('Date RDV')
	praticien = fields.Many2one('hr.employee','Praticien')
	specialite = fields.Many2one('hr.job','Spécialité')
	diagnostic = fields.Text('Diagnostic')
	note = fields.Text('Notes')
	maladie = fields.Many2many('maladie.adherent',string='Maladie')
	traitement = fields.Text('Traitement')
	date_remis= fields.Date('Date remise doc')



class maladie_adherent(models.Model):
	 

	_name = "maladie.adherent"


	name = fields.Char('Maladie')
	description = fields.Text('Description')

