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

class absence_adherent(models.Model):
	 

	_name = "absence.adherent"


	_order='date desc'


	name = fields.Char('Référence')
	adherent = fields.Many2one('gym.adherent','Adhrent')
	date =fields.Date('Date absence')
	date_rentre = fields.Date('Date Rentrée')
	motif = fields.Text('Motif d\'absence')
	type_abs= fields.Selection([('autorisee','Autorisée'),('nonautorise','Non autorisée')],'Type d\'absence')
	note = fields.Text('Notes')

