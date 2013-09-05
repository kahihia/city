# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AdvertisingOrder.created'
        db.add_column(u'advertising_advertisingorder', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 9, 5, 0, 0), auto_now_add=True, blank=True),
                      keep_default=False)

        # Adding M2M table for field taxes on 'AdvertisingOrder'
        db.create_table(u'advertising_advertisingorder_taxes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('advertisingorder', models.ForeignKey(orm[u'advertising.advertisingorder'], null=False)),
            ('accounttax', models.ForeignKey(orm[u'accounts.accounttax'], null=False))
        ))
        db.create_unique(u'advertising_advertisingorder_taxes', ['advertisingorder_id', 'accounttax_id'])


    def backwards(self, orm):
        # Deleting field 'AdvertisingOrder.created'
        db.delete_column(u'advertising_advertisingorder', 'created')

        # Removing M2M table for field taxes on 'AdvertisingOrder'
        db.delete_table('advertising_advertisingorder_taxes')


    models = {
        u'accounts.account': {
            'Meta': {'object_name': 'Account'},
            'about_me': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'all_of_canada': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cities': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['cities.City']", 'symmetrical': 'False'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_open_graph': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'in_the_loop_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'in_the_loop_phonenumber': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'in_the_loop_with_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'in_the_loop_with_sms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_the_loop_with_website': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'location_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'location_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'location_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'native_region': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'native_for_accounts'", 'null': 'True', 'to': u"orm['cities.Region']"}),
            'not_from_canada': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'registered'", 'max_length': '15'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['cities.Region']", 'symmetrical': 'False'}),
            'reminder_active_type': ('django.db.models.fields.CharField', [], {'default': "'HOURS'", 'max_length': '10'}),
            'reminder_days_before_event': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'reminder_hours_before_event': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_on_week_day': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'reminder_on_week_day_at_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_phonenumber': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'reminder_single_events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['event.SingleEvent']", 'null': 'True', 'blank': 'True'}),
            'reminder_time_before_event': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_with_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reminder_with_sms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reminder_with_website': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tax_origin_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'my_profile'", 'unique': 'True', 'to': u"orm['auth.User']"}),
            'website': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'website_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'accounts.accounttax': {
            'Meta': {'object_name': 'AccountTax'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['cities.Region']", 'symmetrical': 'False'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '4'})
        },
        u'accounts.venueaccount': {
            'Meta': {'object_name': 'VenueAccount'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']"}),
            'cropping': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'facebook': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'myspace': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'twitter': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['accounts.VenueType']", 'symmetrical': 'False'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Venue']"})
        },
        u'accounts.venuetype': {
            'Meta': {'object_name': 'VenueType'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'advertising.advertising': {
            'Meta': {'object_name': 'Advertising'},
            'ad_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['advertising.AdvertisingType']"}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['advertising.AdvertisingCampaign']"}),
            'clicks': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'cpc_price': ('djmoney.models.fields.MoneyField', [], {'default': "'0.0'", 'max_digits': '10', 'decimal_places': '2', 'default_currency': "'CAD'"}),
            'cpc_price_currency': ('djmoney.models.fields.CurrencyField', [], {'default': "'CAD'", 'max_length': '3'}),
            'cpm_price': ('djmoney.models.fields.MoneyField', [], {'default': "'0.0'", 'max_digits': '10', 'decimal_places': '2', 'default_currency': "'CAD'"}),
            'cpm_price_currency': ('djmoney.models.fields.CurrencyField', [], {'default': "'CAD'", 'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'payment_type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'review_status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '10'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'advertising.advertisingcampaign': {
            'Meta': {'object_name': 'AdvertisingCampaign'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']"}),
            'all_of_canada': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ammount_spent': ('djmoney.models.fields.MoneyField', [], {'default': "'0.0'", 'max_digits': '18', 'decimal_places': '10', 'default_currency': "'CAD'"}),
            'ammount_spent_currency': ('djmoney.models.fields.CurrencyField', [], {'default': "'CAD'", 'max_length': '3'}),
            'budget': ('djmoney.models.fields.MoneyField', [], {'default': "'0.0'", 'max_digits': '10', 'decimal_places': '2', 'default_currency': "'CAD'"}),
            'budget_currency': ('djmoney.models.fields.CurrencyField', [], {'default': "'CAD'", 'max_length': '3'}),
            'ended': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'enough_money': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'owned_by_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['cities.Region']", 'symmetrical': 'False'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'venue_account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.VenueAccount']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'advertising.advertisingorder': {
            'Meta': {'object_name': 'AdvertisingOrder'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']"}),
            'budget': ('djmoney.models.fields.MoneyField', [], {'default': "'0.0'", 'max_digits': '10', 'decimal_places': '2', 'default_currency': "'CAD'"}),
            'budget_currency': ('djmoney.models.fields.CurrencyField', [], {'default': "'CAD'", 'max_length': '3'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['advertising.AdvertisingCampaign']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 9, 5, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1', 'blank': 'True'}),
            'taxes': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['accounts.AccountTax']", 'symmetrical': 'False'}),
            'total_price': ('djmoney.models.fields.MoneyField', [], {'default': "'0.0'", 'max_digits': '10', 'decimal_places': '2', 'default_currency': "'CAD'"}),
            'total_price_currency': ('djmoney.models.fields.CurrencyField', [], {'default': "'CAD'", 'max_length': '3'})
        },
        u'advertising.advertisingtype': {
            'Meta': {'object_name': 'AdvertisingType'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cpc_price': ('djmoney.models.fields.MoneyField', [], {'default': "'0.0'", 'max_digits': '10', 'decimal_places': '2', 'default_currency': "'CAD'"}),
            'cpc_price_currency': ('djmoney.models.fields.CurrencyField', [], {'default': "'CAD'", 'max_length': '3'}),
            'cpm_price': ('djmoney.models.fields.MoneyField', [], {'default': "'0.0'", 'max_digits': '10', 'decimal_places': '2', 'default_currency': "'CAD'"}),
            'cpm_price_currency': ('djmoney.models.fields.CurrencyField', [], {'default': "'CAD'", 'max_length': '3'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
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
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'cities.city': {
            'Meta': {'object_name': 'City'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_std': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'population': ('django.db.models.fields.IntegerField', [], {}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.Region']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subregion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.Subregion']", 'null': 'True', 'blank': 'True'})
        },
        u'cities.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'population': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tld': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        u'cities.region': {
            'Meta': {'object_name': 'Region'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_std': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'cities.subregion': {
            'Meta': {'object_name': 'Subregion'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_std': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.Region']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'event.event': {
            'Meta': {'object_name': 'Event'},
            'audited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'authentication_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'comment_for_facebook': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 9, 5, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'cropping': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('ckeditor.fields.RichTextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'facebook_event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.FacebookEvent']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 9, 5, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'post_to_facebook': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price': ('django.db.models.fields.CharField', [], {'default': "'Free'", 'max_length': '40', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'tickets': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Venue']", 'null': 'True', 'blank': 'True'}),
            'venue_account_owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.VenueAccount']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'viewed_times': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'event.facebookevent': {
            'Meta': {'object_name': 'FacebookEvent'},
            'eid': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'event.singleevent': {
            'Meta': {'object_name': 'SingleEvent'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'single_events'", 'to': u"orm['event.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'event.venue': {
            'Meta': {'object_name': 'Venue'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.City']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Default Venue'", 'max_length': '250'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'street_number': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'suggested': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        }
    }

    complete_apps = ['advertising']