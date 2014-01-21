# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Links'
        db.create_table(u'vcb_links', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'vcb', ['Links'])

        # Deleting field 'MC3Activities.video_url'
        db.delete_column(u'vcb_mc3activities', 'video_url')

        # Adding M2M table for field video_urls on 'MC3Activities'
        m2m_table_name = db.shorten_name(u'vcb_mc3activities_video_urls')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mc3activities', models.ForeignKey(orm[u'vcb.mc3activities'], null=False)),
            ('links', models.ForeignKey(orm[u'vcb.links'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mc3activities_id', 'links_id'])


    def backwards(self, orm):
        # Deleting model 'Links'
        db.delete_table(u'vcb_links')

        # Adding field 'MC3Activities.video_url'
        db.add_column(u'vcb_mc3activities', 'video_url',
                      self.gf('django.db.models.fields.CharField')(default='http://www.google.com', max_length=300),
                      keep_default=False)

        # Removing M2M table for field video_urls on 'MC3Activities'
        db.delete_table(db.shorten_name(u'vcb_mc3activities_video_urls'))


    models = {
        u'vcb.classes': {
            'Meta': {'object_name': 'Classes'},
            'access_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '9'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'class_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
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
        u'vcb.links': {
            'Meta': {'object_name': 'Links'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '300'})
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