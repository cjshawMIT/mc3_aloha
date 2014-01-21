# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Classes'
        db.create_table(u'vcb_classes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('class_name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('class_number', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('obj_bank_id', self.gf('django.db.models.fields.CharField')(max_length=350)),
            ('access_code', self.gf('django.db.models.fields.CharField')(max_length=9)),
        ))
        db.send_create_signal(u'vcb', ['Classes'])

        # Adding model 'ClassMC3Map'
        db.create_table(u'vcb_classmc3map', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('umbrella_class_id', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('mc3_objective_id', self.gf('django.db.models.fields.CharField')(max_length=350)),
        ))
        db.send_create_signal(u'vcb', ['ClassMC3Map'])

        # Adding model 'ClassSessions'
        db.create_table(u'vcb_classsessions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('umbrella_class_id', self.gf('django.db.models.fields.CharField')(max_length=350)),
            ('session_date', self.gf('django.db.models.fields.DateField')()),
            ('session_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('session_semester', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sequence_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'vcb', ['ClassSessions'])

        # Adding model 'SessionsMC3Map'
        db.create_table(u'vcb_sessionsmc3map', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vcb.ClassSessions'])),
            ('mc3_activity_id', self.gf('django.db.models.fields.CharField')(max_length=350)),
        ))
        db.send_create_signal(u'vcb', ['SessionsMC3Map'])

        # Adding model 'MC3Objectives'
        db.create_table(u'vcb_mc3objectives', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mc3_id', self.gf('django.db.models.fields.CharField')(max_length=350, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('obj_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sequence_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'vcb', ['MC3Objectives'])

        # Adding model 'ObjectiveParentMap'
        db.create_table(u'vcb_objectiveparentmap', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent_mc3_id', self.gf('django.db.models.fields.CharField')(max_length=350)),
            ('child_mc3_id', self.gf('django.db.models.fields.CharField')(max_length=350)),
        ))
        db.send_create_signal(u'vcb', ['ObjectiveParentMap'])

        # Adding model 'MC3Activities'
        db.create_table(u'vcb_mc3activities', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mc3_id', self.gf('django.db.models.fields.CharField')(max_length=350)),
            ('mc3_objective_id', self.gf('django.db.models.fields.CharField')(max_length=350)),
            ('video_url', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('viddate', self.gf('django.db.models.fields.DateField')()),
            ('recorddate', self.gf('django.db.models.fields.DateField')()),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('speaker', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('roughtime', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('techtvtime', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('techtvtimesecs', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('views', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('last_view', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'vcb', ['MC3Activities'])


    def backwards(self, orm):
        # Deleting model 'Classes'
        db.delete_table(u'vcb_classes')

        # Deleting model 'ClassMC3Map'
        db.delete_table(u'vcb_classmc3map')

        # Deleting model 'ClassSessions'
        db.delete_table(u'vcb_classsessions')

        # Deleting model 'SessionsMC3Map'
        db.delete_table(u'vcb_sessionsmc3map')

        # Deleting model 'MC3Objectives'
        db.delete_table(u'vcb_mc3objectives')

        # Deleting model 'ObjectiveParentMap'
        db.delete_table(u'vcb_objectiveparentmap')

        # Deleting model 'MC3Activities'
        db.delete_table(u'vcb_mc3activities')


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
            'mc3_id': ('django.db.models.fields.CharField', [], {'max_length': '350', 'null': 'True'}),
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