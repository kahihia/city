# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'VenueProfile'
        db.create_table('venue_profile', (
            (u'venue_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['event.Venue'], unique=True, primary_key=True)),
            ('cv_phone', self.gf('django.db.models.fields.TextField')()),
            ('cv_fax', self.gf('django.db.models.fields.TextField')()),
            ('cv_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('cv_site', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('cv_fcb', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('cv_twt', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'venue_profile', ['VenueProfile'])

        # Adding M2M table for field cv_user on 'VenueProfile'
        db.create_table('venue_profile_cv_user', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('venueprofile', models.ForeignKey(orm[u'venue_profile.venueprofile'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique('venue_profile_cv_user', ['venueprofile_id', 'user_id'])


    def backwards(self, orm):
        
        # Deleting model 'VenueProfile'
        db.delete_table('venue_profile')

        # Removing M2M table for field cv_user on 'VenueProfile'
        db.delete_table('venue_profile_cv_user')


    models = {
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 5, 2, 57, 49, 446765)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 5, 2, 57, 49, 446174)'}),
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
        u'event.venue': {
            'Meta': {'object_name': 'Venue'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.City']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Default Venue'", 'max_length': '250'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        u'venue_profile.venueprofile': {
            'Meta': {'ordering': "['created_at']", 'object_name': 'VenueProfile', 'db_table': "'venue_profile'", '_ormbases': [u'event.Venue']},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cv_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'cv_fax': ('django.db.models.fields.TextField', [], {}),
            'cv_fcb': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'cv_phone': ('django.db.models.fields.TextField', [], {}),
            'cv_site': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'cv_twt': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'cv_user': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'venue_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['event.Venue']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['venue_profile']
