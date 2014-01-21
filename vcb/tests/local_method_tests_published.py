import datetime
import json
import logging
import urllib
import pdb

from django.test import TestCase, Client
from django.utils import timezone
from django.http import HttpRequest
from django.conf import settings
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, resolve
from django.core.serializers.json import DjangoJSONEncoder
from dateutil import parser

from vcb.models import Classes, ClassMC3Map, ClassSessions, MC3Activities, MC3Objectives, SessionsMC3Map, ObjectiveParentMap
from vcb.views import index, register, success, dashboard
from vcb.test import str_to_unicode, clearMC3Bank, create_data, check_responses
from mc3_learning_adapter_py.mc3_http import create_objective, create_activity, clear_objective, clear_activity, create_activityasset, create_objectivebank, clear_asset, clear_objectivebank, get_all_objectives, get_all_activities, get_all_assets

class LocalMethodTestsPublished(TestCase):
    """
    To test method calls with local data that has been published
    """
    def setUp(self):
        """
        Create a dummy objective bank with a published set of activities
        """
        result = create_data(0, 0)
        self.new_class_session = result['new_class_session']
        self.new_obj = result['new_obj']
        self.new_sub_obj = result['new_sub_obj']
        self.new_activity = result['new_activity']
        self.new_sub_activity = result['new_sub_activity']
        self.new_session = result['new_session']
        self.new_sub_session_map = result['new_sub_session_map']
        self.new_class_mc3_map = result['new_class_mc3_map']
        self.new_sub_class_mc3_map = result['new_sub_class_mc3_map']
        self.original_mc3_bank_id = result['original_mc3_bank_id']
        
        self.obj_bank_id = self.new_class_session.obj_bank_id
    
    def tearDown(self):
        """
        Clean out all the objectives and activities in the bank we just created
        """
        bank_id = self.original_mc3_bank_id
        clearMC3Bank(bank_id)
	    
    def test_get_root_objectives_returns_right_information_for_staff_localdb(self):
        """
        get_objectives() should return a JSON-style object with all root objectives (with no parents)
        and activities for a class
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        response = json.loads(new_class_session.get_root_objectives())

        expected = [
        	{
        	    "bank": new_class_session.obj_bank_id,
        	    "children": [],
        	    "item_class": "objective",
        	    "item_id": new_obj.mc3_id,
        	    "name": new_obj.name[:35],
        	    "source": "local",
	        }
        ]
        
        self.assertEqual(response, expected, 
                msg="Get root objectives does not work for staff")
        
    def test_get_root_objectives_returns_right_information_for_students_localdb(self):
        """
        get_objectives() should return a JSON-style object with all root objectives (with no parents)
        and activities for a class
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        response = json.loads(new_class_session.get_root_objectives())

        expected = [
        	{
        	    "bank": new_class_session.obj_bank_id,
        	    "children": [],
        	    "item_class": "objective",
        	    "item_id": new_obj.mc3_id,
        	    "name": new_obj.name[:35],
        	    "source": "local",
	        }
        ]
       
        self.assertEqual(response, expected,
                msg="Get root objectives does not work for students")
        
    def test_get_sessions_returns_right_information_for_staff_localdb(self):
            """
            get_sessions() should return a JSON-style object with all sessions
            for a class
            """
            new_class_session = self.new_class_session
            new_obj = self.new_obj
            new_sub_obj = self.new_sub_obj
            new_activity = self.new_activity
            new_sub_activity = self.new_sub_activity
            new_session = self.new_session
            
            is_staff = True
            
            response = json.loads(new_class_session.get_sessions(is_staff))
    
            expected = [
            	{
	            	'bank':new_class_session.obj_bank_id,
	            	'children': [],
	            	'item_class': 'session',
	            	'item_id': new_session.id,
	            	'name': new_session.session_name
    	        }
            ]
            
            expected = str_to_unicode(expected)
            
            self.assertEqual(response, expected, 
                    msg="Get sessions does not match for staff")

    def test_get_sessions_returns_right_information_for_students_localdb(self):
        """
        get_sessions() should return a JSON-style object with all sessions
        for a class
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        is_staff = False
        
        response = json.loads(new_class_session.get_sessions(is_staff))

        expected = [
        	{
            	'bank':new_class_session.obj_bank_id,
            	'children': [],
            	'item_class': 'session',
            	'item_id': new_session.id,
            	'name': new_session.session_name
	        }
        ]
        
        expected = str_to_unicode(expected)
        
        self.assertEqual(response, expected, 
                msg="Get Sessions doesn't return right info for students")
    
    def test_get_activities_returns_right_information_for_staff_localdb(self):
        """
        for the class sessions, get_activities needs to return all the activities linked
        to that objective
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        bank = self.obj_bank_id
        is_staff = True
        
        response = json.loads(new_session.get_activities(bank,is_staff))

        expected = [
        	{
	        	'bank': bank,
	        	'class_date': new_activity.viddate,
	        	'item_class': 'asset',
	        	'name': new_activity.subject[:35],
	        	'objective': new_obj.name,
	        	'rec_date': new_activity.recorddate,
	        	'source': 'local',
	        	'speaker': new_activity.speaker,
	        	'subobjective': '',
	        	'item_id': new_activity.mc3_id,
	        	'timestamp': new_activity.techtvtimesecs,
	        	'urls': new_activity.video_urls.all().values_list('url', flat=True),
	        	'views': new_activity.views,
	        },
	        {
	        	'bank': bank,
	        	'class_date': new_sub_activity.viddate,
	        	'item_class': 'asset',
	        	'name': new_sub_activity.subject[:35],
	        	'objective': new_sub_obj.name,
	        	'rec_date': new_sub_activity.recorddate,
	        	'source': 'local',
	        	'speaker': new_sub_activity.speaker,
	        	'subobjective': '',
	        	'item_id': new_sub_activity.mc3_id,
	        	'timestamp': new_sub_activity.techtvtimesecs,
	        	'urls': new_sub_activity.video_urls.all().values_list('url', flat=True),
	        	'views': new_sub_activity.views,
	        }
        ]
        
        expected = str_to_unicode(expected)
        
        check_responses(self, response, expected)
        
    def test_get_activities_returns_right_information_for_students_localdb(self):
        """
        for the class sessions, get_activities needs to return all the activities linked
        to that objective
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        bank = self.obj_bank_id
        is_staff = False
        
        response = json.loads(new_session.get_activities(bank,is_staff))

        expected = [
        	{
	        	'bank': bank,
	        	'class_date': new_activity.viddate,
	        	'item_class': 'asset',
	        	'name': new_activity.subject[:35],
	        	'objective': new_obj.name,
	        	'rec_date': new_activity.recorddate,
	        	'source': 'local',
	        	'speaker': new_activity.speaker,
	        	'subobjective': '',
	        	'item_id': new_activity.mc3_id,
	        	'timestamp': new_activity.techtvtimesecs,
	        	'urls': new_activity.video_urls.all().values_list('url', flat=True),
	        	'views': new_activity.views,
	        },
	        {
	        	'bank': bank,
	        	'class_date': new_sub_activity.viddate,
	        	'item_class': 'asset',
	        	'name': new_sub_activity.subject[:35],
	        	'objective': new_sub_obj.name,
	        	'rec_date': new_sub_activity.recorddate,
	        	'source': 'local',
	        	'speaker': new_sub_activity.speaker,
	        	'subobjective': '',
	        	'item_id': new_sub_activity.mc3_id,
	        	'timestamp': new_sub_activity.techtvtimesecs,
	        	'urls': new_sub_activity.video_urls.all().values_list('url', flat=True),
	        	'views': new_sub_activity.views,
	        }
        ]
        
        expected = str_to_unicode(expected)
        
        check_responses(self, response, expected)

    def test_get_children_returns_right_information_for_staff_localdb(self):
        """
        for the objectives, get_children needs to return all the children linked
        to that objective
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        bank = self.obj_bank_id
        is_staff = True
        
        response = json.loads(new_obj.get_children(bank,is_staff))

        expected = [
        	{
        		'bank': bank,
        		'children': [],
        		'item_class': 'objective',
        		'item_id': new_sub_obj.mc3_id,
        		'name': new_sub_obj.name[:35],
        		'source': 'local',
        	},
            {
        		'bank': bank,
        		'class_date': new_activity.viddate,
        		'item_class': 'asset',
        		'name': new_activity.subject[:35],
        		'objective': new_obj.name,
        		'rec_date': new_activity.recorddate,
        		'source': 'local',
        		'speaker': new_activity.speaker,
        		'subobjective': '',
        		'item_id': new_activity.mc3_id,
        		'timestamp':new_activity.techtvtimesecs,
        		'urls': new_activity.video_urls.all().values_list('url', flat=True),
        		'views': new_activity.views,
	        }
        ]
        
        expected = str_to_unicode(expected)
        
        check_responses(self, response, expected)

    def test_get_children_returns_right_information_for_students_localdb(self):
        """
        for the objectives, get_children needs to return all the children linked
        to that objective
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        bank = self.obj_bank_id
        is_staff = False
        
        response = json.loads(new_obj.get_children(bank,is_staff))

        expected = [
        	{
        		'bank': bank,
        		'children': [],
        		'item_class': 'objective',
        		'item_id': new_sub_obj.mc3_id,
        		'name': new_sub_obj.name[:35],
        		'source': 'local',
        	},
            {
        		'bank': bank,
        		'class_date': new_activity.viddate,
        		'item_class': 'asset',
        		'name': new_activity.subject[:35],
        		'objective': new_obj.name,
        		'rec_date': new_activity.recorddate,
        		'source': 'local',
        		'speaker': new_activity.speaker,
        		'subobjective': '',
        		'item_id': new_activity.mc3_id,
        		'timestamp':new_activity.techtvtimesecs,
        		'urls': new_activity.video_urls.all().values_list('url', flat=True),
        		'views': new_activity.views,
	        }
        ]
        
        expected = str_to_unicode(expected)
        
        check_responses(self, response, expected)

    def test_search_activities_returns_right_information_for_staff_localdb_query_exists(self):
        """
        for a video query with a published date, staff should see results
        if the query term matches something in the database
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        query = 'sub'
        is_staff = True
        
        response = json.loads(new_class_session.search_activities(query, is_staff))

        expected = [{
        	'id': new_sub_activity.mc3_id,
        	'label': new_sub_activity.subject
        }]
        
        self.assertEqual(response, expected, 
                msg="Staff does not see matching activity search")
                

    def test_search_activities_returns_right_information_for_staff_localdb_query_not_exists(self):
        """
        for a video query with a published date, staff should see no results
        if the query term does not match anything in the database
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        query = 'junk'
        is_staff = True
        
        response = json.loads(new_class_session.search_activities(query, is_staff))

        expected = []
        
        self.assertEqual(response, expected, 
                msg="Staff sees non-matching activities on published search")


    def test_search_activities_returns_right_information_for_students_localdb_query_exists(self):
        """
        for a video query with a published date, students should see results
        if the query term matches something in the database
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        query = 'sub'
        is_staff = False
        
        response = json.loads(new_class_session.search_activities(query, is_staff))

        expected = [{
        	'id': new_sub_activity.mc3_id,
        	'label': new_sub_activity.subject
        }]

        self.assertEqual(response, expected, 
                msg="Students do not see matching activities on published search")
                
    def test_search_activities_returns_right_information_for_students_localdb_query_not_exists(self):
        """
        for a video query with a published date, students should see no results
        when the query term does not match anything in the database
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        query = 'junk'
        is_staff = False
        
        response = json.loads(new_class_session.search_activities(query, is_staff))

        expected = []
        
        self.assertEqual(response, expected, 
                msg="Student sees non-matching activities on published search")


    def test_recently_viewed_returns_right_information_for_staff_localdb(self):
        """
        When checking the recently viewed list, staff should see published videos
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        is_staff = True
        
        response = json.loads(new_class_session.viewed_recently(is_staff))

        expected = [{
        	'id': new_activity.mc3_id,
        	'subject': new_activity.subject,
        	'views': new_activity.views
            },
            {
        	'id': new_sub_activity.mc3_id,
        	'subject': new_sub_activity.subject,
        	'views': new_sub_activity.views
        }]
        
        self.assertEqual(response, expected, 
                msg="Staff does not see published activities on recently viewed list")

    def test_recently_viewed_returns_right_information_for_students_localdb(self):
        """
        When checking the recently viewed list, students should not see unpublished videos
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        is_staff = False
        
        response = json.loads(new_class_session.viewed_recently(is_staff))

        expected = [{
        	'id': new_activity.mc3_id,
        	'subject': new_activity.subject,
        	'views': new_activity.views
            },
            {
        	'id': new_sub_activity.mc3_id,
        	'subject': new_sub_activity.subject,
        	'views': new_sub_activity.views
        }]
        
        self.assertEqual(response, expected, 
                msg="Students don't see published activities on recently viewed list")
    
    def test_get_full_name_returns_name_and_number_localdb(self):
        """
        The get_full_name method for classes returns the class name and number
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        
        response = new_class_session.get_full_name()

        expected = {
        	'class_name': new_class_session.class_name,
        	'class_number': new_class_session.class_number,
        	'semester': new_class_session.semester
        }
        
        self.assertEqual(response, expected, 
                msg="Local db does not return full class name and number")

    def test_can_copy_class_localdb(self):
        """
        copying an entire class works
        """
        new_class_session = self.new_class_session
        new_obj = self.new_obj
        new_sub_obj = self.new_sub_obj
        new_activity = self.new_activity
        new_sub_activity = self.new_sub_activity
        new_session = self.new_session
        new_mc3_map = self.new_class_mc3_map
        
        second_class_session = Classes(  
                class_name = 'test class 2', 
                class_number = '1.002',
                obj_bank_id = 'second_fake_mc3_id',
                semester = 'Fall 2013'
        )
        second_class_session.save()
        second_mc3_bank_id = second_class_session.obj_bank_id[:]
        
        copy_success = new_class_session.copy_to(second_mc3_bank_id)
        
        self.assertTrue(copy_success)
        
        second_class_id = int(second_class_session.id)

        second_class_mc3_map = ClassMC3Map.objects.get(umbrella_class_id = second_class_id)
        second_class_root = MC3Objectives.objects.get(mc3_id = second_class_mc3_map.mc3_objective_id)
        second_class_parent_map = ObjectiveParentMap.objects.get(parent_mc3_id = second_class_root.mc3_id)
        second_class_child = MC3Objectives.objects.get(mc3_id = second_class_parent_map.child_mc3_id)
        
        self.assertEqual(
                int(second_class_mc3_map.umbrella_class_id),
                second_class_id)
        self.assertEqual(
                second_class_root.name,
                new_obj.name)
        self.assertEqual(
                second_class_root.obj_type,
                new_obj.obj_type)
        self.assertEqual(
                second_class_root.sequence_order,
                new_obj.sequence_order)
        self.assertEqual(
                second_class_child.name,
                new_sub_obj.name) 
        self.assertEqual(
                second_class_child.obj_type,
                new_sub_obj.obj_type)
        self.assertEqual(
                second_class_child.sequence_order,
                new_sub_obj.sequence_order) 
    
        second_class_session = ClassSessions.objects.get(umbrella_class_id = second_class_id)
        second_class_activity = MC3Activities.objects.get(mc3_objective_id = second_class_root.mc3_id)
        second_class_sub_act = MC3Activities.objects.get(mc3_objective_id = second_class_child.mc3_id)
        
        self.assertEqual(
                int(second_class_session.umbrella_class_id),
                second_class_id)
        self.assertEqual(
                second_class_session.session_date,
                parser.parse(new_session.session_date).date())
        self.assertEqual(
                second_class_session.session_name,
                new_session.session_name)
        self.assertEqual(
                second_class_session.sequence_order,
                int(new_session.sequence_order))
        
        self.assertEqual(
                second_class_activity.subject,
                new_activity.subject)
        
        first_urls = new_activity.video_urls.all()
        second_urls = second_class_activity.video_urls.all()
        
        self.assertEqual(
                len(first_urls),
                len(second_urls))

        for index, url in enumerate(first_urls):
            self.assertEqual(
                    url,
                    second_urls[index])

        self.assertEqual(
                second_class_activity.viddate,
                parser.parse(new_activity.viddate).date())
        self.assertEqual(
                second_class_activity.recorddate,
                parser.parse(new_activity.recorddate).date())
        self.assertEqual(
                second_class_activity.speaker,
                new_activity.speaker)
        self.assertEqual(
                second_class_activity.roughtime,
                new_activity.roughtime)
        self.assertEqual(
                second_class_activity.techtvtime,
                new_activity.techtvtime)
        self.assertEqual(
                second_class_activity.techtvtimesecs,
                new_activity.techtvtimesecs)
        self.assertEqual(
                second_class_activity.pub_date,
                new_activity.pub_date.replace(microsecond=0))
        self.assertEqual(
                second_class_activity.views,
                0)
                
        self.assertEqual(
                second_class_sub_act.subject,
                new_sub_activity.subject)
                
        first_sub_urls = new_sub_activity.video_urls.all()
        second_sub_urls = second_class_sub_act.video_urls.all()
        
        self.assertEqual(
                len(first_sub_urls),
                len(second_sub_urls))

        for index, url in enumerate(first_sub_urls):
            self.assertEqual(
                    url,
                    second_sub_urls[index])

        self.assertEqual(
                second_class_sub_act.viddate,
                parser.parse(new_sub_activity.viddate).date())
        self.assertEqual(
                second_class_sub_act.recorddate,
                parser.parse(new_sub_activity.recorddate).date())
        self.assertEqual(
                second_class_sub_act.speaker,
                new_sub_activity.speaker)
        self.assertEqual(
                second_class_sub_act.roughtime,
                new_sub_activity.roughtime)
        self.assertEqual(
                second_class_sub_act.techtvtime,
                new_sub_activity.techtvtime)
        self.assertEqual(
                second_class_sub_act.techtvtimesecs,
                new_sub_activity.techtvtimesecs)
        self.assertEqual(
                second_class_sub_act.pub_date,
                new_sub_activity.pub_date.replace(microsecond=0))
        self.assertEqual(
                second_class_sub_act.views,
                0)
        
