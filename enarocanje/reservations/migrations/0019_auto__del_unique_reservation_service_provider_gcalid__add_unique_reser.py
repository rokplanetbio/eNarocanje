# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Reservation', fields ['service_provider', 'gcalid']
        db.delete_unique(u'reservations_reservation', ['service_provider_id', 'gcalid'])

        # Adding unique constraint on 'Reservation', fields ['service_provider', 'service_provider_employee', 'gcalid']
        db.create_unique(u'reservations_reservation', ['service_provider_id', 'service_provider_employee_id', 'gcalid'])


    def backwards(self, orm):
        # Removing unique constraint on 'Reservation', fields ['service_provider', 'service_provider_employee', 'gcalid']
        db.delete_unique(u'reservations_reservation', ['service_provider_id', 'service_provider_employee_id', 'gcalid'])

        # Adding unique constraint on 'Reservation', fields ['service_provider', 'gcalid']
        db.create_unique(u'reservations_reservation', ['service_provider_id', 'gcalid'])


    models = {
        u'ServiceProviderEmployee.serviceprovideremployee': {
            'Meta': {'object_name': 'ServiceProviderEmployee'},
            'active_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'active_to': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'employees'", 'to': u"orm['service.Service']"}),
            'service_provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'employees'", 'to': u"orm['accountext.ServiceProvider']"})
        },
        u'accountext.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'accountext.serviceprovider': {
            'Meta': {'object_name': 'ServiceProvider'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accountext.Category']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'gcal_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'gcal_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo_height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'logo_width': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'reservation_confirmation_needed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'subscription_end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 13, 0, 0)'}),
            'subscription_mail_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'UTC'", 'max_length': '30'}),
            'web': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        u'accountext.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '5'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'referral': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accountext.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'service_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'service_provider': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['accountext.ServiceProvider']", 'unique': 'True', 'null': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'customers.customer': {
            'Meta': {'object_name': 'Customer'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'last_reservation': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 4, 13, 0, 0)', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'service_provider': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['accountext.ServiceProvider']", 'null': 'True'})
        },
        u'reservations.gcal': {
            'Meta': {'object_name': 'GCal'},
            'credential': ('oauth2client.django_orm.CredentialsField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accountext.ServiceProvider']", 'primary_key': 'True'})
        },
        u'reservations.reservation': {
            'Meta': {'unique_together': "(('service_provider', 'service_provider_employee', 'gcalid'),)", 'object_name': 'Reservation'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['customers.Customer']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'emailsent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gcalid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'gcalimported': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deny': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isfromgcal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.Service']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'service_duration': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'service_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'service_provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'to': u"orm['accountext.ServiceProvider']"}),
            'service_provider_employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ServiceProviderEmployee.ServiceProviderEmployee']", 'null': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accountext.User']", 'null': 'True'}),
            'user_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'user_fullname': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'user_phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        u'service.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'service.service': {
            'Meta': {'object_name': 'Service'},
            'active_until': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service.Category']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'service_provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'services'", 'to': u"orm['accountext.ServiceProvider']"}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['reservations']