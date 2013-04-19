# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AccountReminding'
        db.create_table(u'accounts_accountreminding', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Account'])),
            ('eventDay', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.SingleEvent'])),
            ('notification_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('done', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'accounts', ['AccountReminding'])


    def backwards(self, orm):
        # Deleting model 'AccountReminding'
        db.delete_table(u'accounts_accountreminding')


    models = {
        u'accounts.account': {
            'Meta': {'object_name': 'Account'},
            'about_me': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_open_graph': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'in_the_loop_days_before_event': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'in_the_loop_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'in_the_loop_hours_before_event': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'in_the_loop_on_week_day': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'in_the_loop_on_week_day_at_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'in_the_loop_phonenumber': ('phonenumber_field.modelfields.PhoneNumberField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'in_the_loop_with_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'in_the_loop_with_sms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_the_loop_with_website': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'registered'", 'max_length': '15'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_days_before_event': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'reminder_events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['event.SingleEvent']", 'null': 'True', 'blank': 'True'}),
            'reminder_hours_before_event': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_on_week_day': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'reminder_on_week_day_at_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_phonenumber': ('phonenumber_field.modelfields.PhoneNumberField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reminder_time_before_event': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_with_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reminder_with_sms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reminder_with_website': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'my_profile'", 'unique': 'True', 'to': u"orm['auth.User']"}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Venue']", 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'website_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'accounts.accountreminding': {
            'Meta': {'object_name': 'AccountReminding'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']"}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'eventDay': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.SingleEvent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification_time': ('django.db.models.fields.DateTimeField', [], {})
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
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 18, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'cropping': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 18, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.CharField', [], {'default': "'Free'", 'max_length': '40', 'blank': 'True'}),
            'search_index': ('djorm_pgfulltext.fields.VectorField', [], {'default': "''", 'null': 'True', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'tickets': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Venue']", 'null': 'True', 'blank': 'True'}),
            'viewed_times': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'event.singleevent': {
            'Meta': {'object_name': 'SingleEvent'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'single_events'", 'to': u"orm['event.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'search_index': ('djorm_pgfulltext.fields.VectorField', [], {'default': "''", 'null': 'True', 'db_index': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'event.venue': {
            'Meta': {'object_name': 'Venue'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.City']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Default Venue'", 'max_length': '250'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
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

    complete_apps = ['accounts']