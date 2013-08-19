# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Feedback.type'
        db.add_column(u'feedback_feedback', 'type', self.gf('django.db.models.fields.CharField')(default='contact', max_length=10), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Feedback.type'
        db.delete_column(u'feedback_feedback', 'type')


    models = {
        u'feedback.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'comments': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'contact'", 'max_length': '10'})
        }
    }

    complete_apps = ['feedback']
