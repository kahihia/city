# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Directory'
        db.create_table(u'elfinder_directory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='dirs', null=True, to=orm['elfinder.Directory'])),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['elfinder.FileCollection'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'elfinder', ['Directory'])

        # Adding unique constraint on 'Directory', fields ['name', 'parent']
        db.create_unique(u'elfinder_directory', ['name', 'parent_id'])

        # Adding model 'FileCollection'
        db.create_table(u'elfinder_filecollection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'elfinder', ['FileCollection'])

        # Adding model 'File'
        db.create_table(u'elfinder_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='files', null=True, to=orm['elfinder.Directory'])),
            ('content', self.gf('django.db.models.fields.TextField')(max_length=2048, blank=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['elfinder.FileCollection'])),
        ))
        db.send_create_signal(u'elfinder', ['File'])

        # Adding unique constraint on 'File', fields ['name', 'parent']
        db.create_unique(u'elfinder_file', ['name', 'parent_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'File', fields ['name', 'parent']
        db.delete_unique(u'elfinder_file', ['name', 'parent_id'])

        # Removing unique constraint on 'Directory', fields ['name', 'parent']
        db.delete_unique(u'elfinder_directory', ['name', 'parent_id'])

        # Deleting model 'Directory'
        db.delete_table(u'elfinder_directory')

        # Deleting model 'FileCollection'
        db.delete_table(u'elfinder_filecollection')

        # Deleting model 'File'
        db.delete_table(u'elfinder_file')


    models = {
        u'elfinder.directory': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'Directory'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['elfinder.FileCollection']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'dirs'", 'null': 'True', 'to': u"orm['elfinder.Directory']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'elfinder.file': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'File'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['elfinder.FileCollection']"}),
            'content': ('django.db.models.fields.TextField', [], {'max_length': '2048', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'files'", 'null': 'True', 'to': u"orm['elfinder.Directory']"})
        },
        u'elfinder.filecollection': {
            'Meta': {'object_name': 'FileCollection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['elfinder']