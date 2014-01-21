# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'MC3Objectives.mc3_id'
        db.alter_column(u'vcb_mc3objectives', 'mc3_id', self.gf('django.db.models.fields.CharField')(default=datetime.datetime(2013, 9, 16, 0, 0), max_length=350))

    def backwards(self, orm):

        # Changing field 'MC3Objectives.mc3_id'
        db.alter_column(u'vcb_mc3objectives', 'mc3_id', self.gf('django.db.models.fields.CharField')(max_length=350, null=True))

    models = {
        u'vcb.classes': {
            'Meta': {'object_name': 'Classes'},
            'access_code': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'class_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'obj_bank_id': ('django.db.models.fields.CharField', [], {'max_length': '350'})
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
            'sequence_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'session_date': ('django.db.models.fields.DateField', [], {}),
            'session_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'session_semester': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'umbrella_class_id': ('django.db.models.fields.CharField', [], {'max_length': '350'})
        },
        u'vcb.mc3activities': {
            'Meta': {'object_name': 'MC3Activities'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_view': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'mc3_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'mc3_objective_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'recorddate': ('django.db.models.fields.DateField', [], {}),
            'roughtime': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'speaker': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'techtvtime': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'techtvtimesecs': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'viddate': ('django.db.models.fields.DateField', [], {}),
            'video_url': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'views': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'vcb.mc3objectives': {
            'Meta': {'object_name': 'MC3Objectives'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mc3_id': ('django.db.models.fields.CharField', [], {'max_length': '350'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
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