# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Snippet'
        db.delete_table(u'campaign_snippet')

        # Adding field 'Campaign.started_at'
        db.add_column(u'campaign_campaign', 'started_at',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'Campaign.completed'
        db.add_column(u'campaign_campaign', 'completed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Campaign.completed_at'
        db.add_column(u'campaign_campaign', 'completed_at',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'Snippet'
        db.create_table(u'campaign_snippet', (
            ('code', self.gf('django.db.models.fields.TextField')()),
            ('highlighted', self.gf('django.db.models.fields.TextField')()),
            ('style', self.gf('django.db.models.fields.CharField')(default='friendly', max_length=100)),
            ('language', self.gf('django.db.models.fields.CharField')(default='python', max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='snippets', to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('linenos', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('campaign', ['Snippet'])

        # Deleting field 'Campaign.started_at'
        db.delete_column(u'campaign_campaign', 'started_at')

        # Deleting field 'Campaign.completed'
        db.delete_column(u'campaign_campaign', 'completed')

        # Deleting field 'Campaign.completed_at'
        db.delete_column(u'campaign_campaign', 'completed_at')


    models = {
        u'campaign.campaign': {
            'Meta': {'ordering': "('-modified', '-created')", 'object_name': 'Campaign'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'completed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'recipient_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaign.RecipientGroup']"}),
            'recipient_index': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "'name'", 'overwrite': 'False'}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaign.Template']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        u'campaign.recipient': {
            'Meta': {'ordering': "('-modified', '-created')", 'object_name': 'Recipient'},
            'context': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaign.RecipientGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'phone': ('django.db.models.fields.IntegerField', [], {})
        },
        u'campaign.recipientgroup': {
            'Meta': {'ordering': "('-modified', '-created')", 'object_name': 'RecipientGroup'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "'name'", 'overwrite': 'False'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        u'campaign.template': {
            'Meta': {'ordering': "('-modified', '-created')", 'object_name': 'Template'},
            'context': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'sender': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "'name'", 'overwrite': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.TextField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        }
    }

    complete_apps = ['campaign']