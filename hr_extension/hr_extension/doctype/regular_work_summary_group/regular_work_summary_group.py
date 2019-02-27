# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aleksas Pielikis and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe.utils
from frappe.model.document import Document
from frappe import _
from hr_extension.hr_extension.doctype.regular_work_summary.regular_work_summary import get_user_emails_from_group
from calendar import day_name, month_name, monthrange
from datetime import datetime

class RegularWorkSummaryGroup(Document):
	def validate(self):
		if self.users:
			if not frappe.flags.in_test and not is_incoming_account_enabled():
				frappe.throw(_('Please enable default incoming account before creating Regular Work Summary Group'))

def trigger_emails():
	'''Send emails to Employees at the given hour asking
			them what did they work on today'''
	groups = frappe.get_all("Regular Work Summary Group")
	for d in groups:
		print(d)
		group_doc = frappe.get_doc("Regular Work Summary Group", d)

		if (is_current_hour(group_doc)
			and is_current_day(group_doc)
			and is_current_month(group_doc)
			and not is_holiday_today(group_doc.holiday_list)
			and group_doc.enabled):
			emails = get_user_emails_from_group(group_doc, 'Reminder')
			# find emails relating to a company
			if emails:
				print(emails)
				regular_work_summary = frappe.get_doc(
					dict(doctype='Regular Work Summary', regular_work_summary_group=group_doc.name)
				).insert()
				regular_work_summary.send_mails(group_doc, emails)

def is_current_hour(group_doc):
	hour = group_doc.send_emails_at
	return frappe.utils.nowtime().split(':')[0] == hour.split(':')[0]

def is_current_day(group_doc):
	if group_doc.send_emails_frequency == 'Weekly':
		return day_name[datetime.today().weekday()] == group_doc.send_emails_week_day
	elif group_doc.send_emails_frequency in ['Monthly', 'Yearly']:
		month_day = int(group_doc.send_emails_month_day)
		today = datetime.today()
		if month_day < 0:
			month_day += monthrange(today.year, today.month)[1] + 1
		return today.day == month_day

	return True

def is_current_month(group_doc):
	if group_doc.send_emails_frequency == 'Yearly':
		return month_name[datetime.today().month] == group_doc.send_emails_month
	return True

def is_holiday_today(holiday_list):
	date = frappe.utils.today()
	if holiday_list:
		return frappe.get_all('Holiday List',
			dict(name=holiday_list, holiday_date=date)) and True or False
	else:
		return False

def send_summary():
	'''Send summary to everyone'''
	for d in frappe.get_all('Regular Work Summary', dict(status='Open')):
		regular_work_summary = frappe.get_doc('Regular Work Summary', d.name)
		regular_work_summary.send_summary()

def is_incoming_account_enabled():
	return frappe.db.get_value('Email Account', dict(enable_incoming=1, default_incoming=1))
