# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Links.mimetype'
        db.delete_column(u'vcb_links', 'mimetype')

        # Adding field 'Links.vtype'
        db.add_column(u'vcb_links', 'vtype',
                      self.gf('django.db.models.fields.CharField')(default='mp4', max_length=50),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Links.mimetype'
        db.add_column(u'vcb_links', 'mimetype',
                      self.gf('django.db.models.fields.CharField')(default='mp4', max_length=50),
                      keep_default=False)

        # Deleting field 'Links.vtype'
        db.delete_column(u'vcb_links', 'vtype')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'vcb.classes': {
            'Meta': {'object_name': 'Classes'},
            'access_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '9'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'class_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'clicks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['vcb.Clicks']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'obj_bank_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'semester': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'vcb.classmc3map': {
            'Meta': {'object_name': 'ClassMC3Map'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mc3_objective_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'umbrella_class_id': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        u'vcb.classsessions': {
            'Meta': {'object_name': 'ClassSessions'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sequence_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'session_date': ('django.db.models.fields.DateField', [], {}),
            'session_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'umbrella_class_id': ('django.db.models.fields.CharField', [], {'max_length': '350'})
        },
        u'vcb.clicks': {
            'Meta': {'object_name': 'Clicks'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vcb.MC3Activities']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'vcb.links': {
            'Meta': {'object_name': 'Links'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'resolution_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '99'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'vtype': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'vcb.mc3activities': {
            'Meta': {'object_name': 'MC3Activities'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_view': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'mc3_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'mc3_objective_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'recorddate': ('django.db.models.fields.DateField', [], {}),
            'roughtime': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'sequence_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'speaker': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'techtvtime': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'techtvtimesecs': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'viddate': ('django.db.models.fields.DateField', [], {}),
            'video_urls': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['vcb.Links']", 'symmetrical': 'False'}),
            'views': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'vcb.mc3objectives': {
            'Meta': {'object_name': 'MC3Objectives'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mc3_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'obj_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sequence_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        u'vcb.objectiveparentmap': {
            'Meta': {'object_name': 'ObjectiveParentMap'},
            'child_mc3_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_mc3_id': ('django.db.models.fields.CharField', [], {'max_length': '350'})
        },
        u'vcb.sessionsmc3map': {
            'Meta': {'object_name': 'SessionsMC3Map'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mc3_activity_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vcb.ClassSessions']"})
        }
    }

    complete_apps = ['vcb']