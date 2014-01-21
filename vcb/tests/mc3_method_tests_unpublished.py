import datetime
import json
import logging
import urllib

from django.test import TestCase, Client
from django.utils import timezone
from django.http import HttpRequest
from django.conf import settings
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, resolve
from django.core.serializers.json import DjangoJSONEncoder

from vcb.models import Classes, ClassMC3Map, ClassSessions, MC3Activities, MC3Objectives, SessionsMC3Map, ObjectiveParentMap
from vcb.views import index, register, success, dashboard
from vcb.test import str_to_unicode, clearMC3Bank, create_data, check_responses
from mc3_learning_adapter_py.mc3_http import create_objective, create_activity, clear_objective, clear_activity, create_activityasset, create_objectivebank, clear_asset, clear_objectivebank, get_all_objectives, get_all_activities, get_all_assets

class MC3MethodTestsUnpublished(TestCase):
    """
    To test method calls with MC3 data that has not been published
    """
    def setUp(self):
        """
        Create a dummy objective bank with a publish-in-the-future set of activities
        """
        result = create_data(1, 0, False)
        self.new_class_session = result['new_class_session']
        self.new_obj = result['new_obj']
        self.new_sub_obj = result['new_sub_obj']
        self.new_activity = result['new_activity']
        self.new_sub_activity = result['new_sub_activity']
        self.new_session = result['new_session']
        self.original_mc3_bank_id = result['original_mc3_bank_id']
        
        self.obj_bank_id = self.new_class_session.obj_bank_id
    
    def tearDown(self):
        """
        Clean out all the objectives and activities in the bank we just created
        """
        bank_id = self.original_mc3_bank_id
        clearMC3Bank(bank_id)
	    
    def test_get_root_objectives_returns_right_information_for_staff_mc3_future(self):
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
        	    "source": "mc3",
	        }
        ]
        
        expected = str_to_unicode(expected)

        check_responses(self, response, expected)
        
    def test_get_root_objectives_returns_right_information_for_students_mc3_future(self):
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
        	    "source": "mc3",
	        }
        ]
        
        
        expected = str_to_unicode(expected)
       
        check_responses(self, response, expected)
    
    def test_get_activities_returns_right_information_for_staff_mc3_future(self):
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
        # Most of this information is blank until MC3 gets extended asset information
        # Test will fail!
        expected = [
        	{
	        	'bank': bank,
	        	'class_date': new_activity.viddate,
	        	'item_class': 'asset',
	        	'name': new_activity.subject[:35],
	        	'objective': new_obj.name,
	        	'rec_date': new_activity.recorddate,
	        	'source': 'mc3',
	        	'speaker': new_activity.speaker,
	        	'subobjective': '',
	        	'item_id': new_activity.mc3_id.replace('\n','%0A'),
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
	        	'source': 'mc3',
	        	'speaker': new_sub_activity.speaker,
	        	'subobjective': '',
	        	'item_id': new_sub_activity.mc3_id.replace('\n','%0A'),
	        	'timestamp': new_sub_activity.techtvtimesecs,
	        	'urls': new_sub_activity.video_urls.all().values_list('url', flat=True),
	        	'views': new_sub_activity.views,
	        }
        ]
        
        expected = str_to_unicode(expected)

        check_responses(self, response, expected)
        
    def test_get_activities_returns_right_information_for_students_mc3_future(self):
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

        # Most of this information is blank until MC3 gets extended asset information
        # Test will fail!
        expected = []
        
        expected = str_to_unicode(expected)
        
        check_responses(self, response, expected)

    def test_get_children_returns_right_information_for_staff_mc3_future(self):
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

        # The activity information will be wrong until MC3 gets extended asset data
        # This test will fail!
        expected = [
        	{
        		'bank': bank,
        		'children': [],
        		'item_class': 'objective',
        		'item_id': new_sub_obj.mc3_id,
        		'name': new_sub_obj.name[:35],
        		'source': 'mc3',
        	},
            {
        		'bank': bank,
        		'class_date': new_activity.viddate,
        		'item_class': 'asset',
        		'name': new_activity.subject[:35],
        		'objective': new_obj.name,
        		'rec_date': new_activity.recorddate,
        		'source': 'mc3',
        		'speaker': new_activity.speaker,
        		'subobjective': '',
        		'item_id': new_activity.mc3_id.replace('\n','%0A'),
        		'timestamp':new_activity.techtvtimesecs,
        		'urls': new_activity.video_urls.all().values_list('url', flat=True),
        		'views': new_activity.views,
	        }
        ]
        
        expected = str_to_unicode(expected)
        
        check_responses(self, response, expected)

    def test_get_children_returns_right_information_for_students_mc3_future(self):
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
        # The activity information will be wrong until MC3 gets extended asset data
        # This test will fail!
        expected = [
        	{
        		'bank': bank,
        		'children': [],
        		'item_class': 'objective',
        		'item_id': new_sub_obj.mc3_id,
        		'name': new_sub_obj.name[:35],
        		'source': 'mc3',
        	}
        ]
        
        expected = str_to_unicode(expected)

        check_responses(self, response, expected)

    def test_search_activities_returns_right_information_for_staff_mc3_query_exists_future(self):
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
        	'id': new_sub_activity.mc3_id.replace('\n','%0A'),
        	'label': new_sub_activity.subject
        }]
        
        expected = str_to_unicode(expected)
        
        self.assertEqual(response, expected, 
                msg="Staff does not see matching activity search")
                

    def test_search_activities_returns_right_information_for_staff_mc3_query_not_exists_future(self):
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
                msg="Staff sees non-matching activities on unpublished search")


    def test_search_activities_returns_right_information_for_students_mc3_query_exists_future(self):
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

        expected = []

        expected = str_to_unicode(expected)

        self.assertEqual(response, expected, 
                msg="Students do see matching activities on unpublished search")
                
    def test_search_activities_returns_right_information_for_students_mc3_query_not_exists_future(self):
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
        
        expected = str_to_unicode(expected)
        
        self.assertEqual(response, expected, 
                msg="Student sees non-matching activities on unpublished search")


    def test_recently_viewed_returns_right_information_for_staff_mc3_future(self):
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
        
        # The activity information will be wrong until MC3 gets extended asset data
        # This test will fail!

        expected = [{
        	'id': new_activity.mc3_id.replace('\n','%0A'),
        	'subject': new_activity.subject,
        	'views': new_activity.views
            },
            {
        	'id': new_sub_activity.mc3_id.replace('\n','%0A'),
        	'subject': new_sub_activity.subject,
        	'views': new_sub_activity.views
        }]
        
        expected = str_to_unicode(expected)
        
        self.assertEqual(response, expected, 
                msg="Staff does not see unpublished activities on recently viewed list")

    def test_recently_viewed_returns_right_information_for_students_mc3_future(self):
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

        # The activity information will be wrong until MC3 gets extended asset data
        # This test will fail!

        expected = []
        
        expected = str_to_unicode(expected)
        
        self.assertEqual(response, expected, 
                msg="Students see unpublished activities on recently viewed list")

    def test_get_sessions_returns_right_information_for_staff_mc3_future(self):
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

    def test_get_sessions_returns_right_information_for_students_mc3_future(self):
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
    
