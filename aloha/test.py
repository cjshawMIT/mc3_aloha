import datetime
import json
import logging
import urllib
import pickle
import pdb

from django.test import TestCase, Client
from django.utils import timezone
from django.http import HttpRequest
from django.conf import settings
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, resolve
from django.core.serializers.json import DjangoJSONEncoder

from vcb.models import Classes, ClassMC3Map, ClassSessions, MC3Activities, MC3Objectives, SessionsMC3Map, ObjectiveParentMap, Links
from vcb.views import index, register, success, dashboard
from mc3_learning_adapter_py.mc3_http import create_objective, create_activity, clear_objective, clear_activity, create_activityasset, create_objectivebank, clear_asset, clear_objectivebank, get_all_objectives, get_all_activities, get_all_assets

def create_data(pdays, tdays, local=True, class_name='test class', class_number='1.001', access_code='1.001xxx', semester='Spring 2012'):
    """
    Creates an activity with the passed parameters
    days = offset for last view (negative = past, positive = future)
    Saves it locally
    """
    new_class_session, class_created = Classes.objects.get_or_create(  
            class_name = class_name, 
            class_number = class_number,
            access_code = access_code,
            semester = semester
    )
    
    original_mc3_bank_id = new_class_session.obj_bank_id[:]
    
#    clearMC3Bank(original_mc3_bank_id)
    
    if local:
        new_class_session.obj_bank_id = 'not_real_mc3_id'
        new_class_session.save()
    
    new_obj = MC3Objectives(
            name = 'learning objective' 
    )
    new_obj.save(new_class_session.obj_bank_id)
    parent_id = new_obj.mc3_id
    new_sub_obj = MC3Objectives( 
            name = 'sub learning objective', 
    )
    new_sub_obj.save(new_class_session.obj_bank_id)
    
    new_parent_map = ObjectiveParentMap(
            parent_mc3_id = parent_id,
            child_mc3_id = new_sub_obj.mc3_id
    )
    
    new_parent_map.save(new_class_session.obj_bank_id)
    
    new_session, session_created = ClassSessions.objects.get_or_create(
            umbrella_class_id = new_class_session.id, 
            session_date = '2012-01-02', 
            session_name = 'Lecture 0',
            sequence_order = '1'
    )
    
    new_activity = MC3Activities(
            mc3_objective_id = parent_id,
            viddate = '2012-01-01', 
            recorddate = '2012-01-01', 
            subject = 'test activity', 
            speaker = 'no speaker', 
            roughtime = '0:00:00', 
            techtvtime = '0:00:00', 
            techtvtimesecs = 0, 
            views = 0, 
            pub_date = (timezone.now() + datetime.timedelta(pdays)),
            last_view = (timezone.now() + datetime.timedelta(tdays)) 
    )
    
    new_activity.save(new_class_session.obj_bank_id, new_obj.mc3_id, new_session.session_name)
    
    newlink, created = Links.objects.get_or_create(
        vtype = 'mp4',
        url = 'https://dcb8la7bjdmk9.cloudfront.net/VCB_Sandbox/mp4/17595.mp4'
    )
    
    new_activity.video_urls.add(newlink)
    sub_parent_id = new_sub_obj.mc3_id
    new_sub_activity = MC3Activities(
            mc3_objective_id = sub_parent_id,
            viddate = '2012-02-02', 
            recorddate = '2012-02-02', 
            subject = 'test sub activity', 
            speaker = 'no speaker', 
            roughtime = '0:00:00', 
            techtvtime = '0:00:00', 
            techtvtimesecs = 2, 
            views = 0, 
            pub_date = (timezone.now() + datetime.timedelta(pdays)),
            last_view = (timezone.now() + datetime.timedelta(tdays)) 
    )
    new_sub_activity.save(new_class_session.obj_bank_id, new_sub_obj.mc3_id, new_session.session_name)
    
    newlink, created = Links.objects.get_or_create(
        vtype = 'mp4',
        url = 'https://d1wneppl4b6zoy.cloudfront.net/spring2012/mp4/19447.mp4'
    )
    
    new_sub_activity.video_urls.add(newlink)
    
    new_session_map, session_map_created = SessionsMC3Map.objects.get_or_create(
            session_id = new_session.id, 
            mc3_activity_id = new_activity.mc3_id
    )
    new_sub_session_map, sub_session_map_created = SessionsMC3Map.objects.get_or_create(
            session_id = new_session.id, 
            mc3_activity_id = new_sub_activity.mc3_id
    )
    new_class_mc3_map, class_map_created = ClassMC3Map.objects.get_or_create( 
            umbrella_class_id = new_class_session.id, 
            mc3_objective_id = new_obj.mc3_id
    )

#    new_sub_class_mc3_map, sub_class_map_created = ClassMC3Map.objects.get_or_create( 
#            umbrella_class_id = new_class_session.id, 
#            mc3_objective_id = new_sub_obj.mc3_id
#    )
    new_sub_class_mc3_map = ''

    result = { 
    	"new_class_session": new_class_session, 
    	"new_obj": new_obj, 
    	"new_sub_obj": new_sub_obj,
    	"new_parent_map": new_parent_map,
    	"new_activity": new_activity, 
    	"new_sub_activity": new_sub_activity,
    	"new_session": new_session,
    	"new_session_map": new_session_map,
    	"new_sub_session_map": new_sub_session_map,
    	"new_class_mc3_map": new_class_mc3_map,
    	"new_sub_class_mc3_map": new_sub_class_mc3_map,
    	"original_mc3_bank_id": original_mc3_bank_id
    }
    
    return result

def check_responses(self, response, expected):
    """
    Check each object in list against another object
    """
    self.assertEqual(
        len(response),
        len(expected))
    
    for index, obj in enumerate(response):
        for key, value in obj.iteritems():
            expected_obj = expected[index]
            if key == 'urls':
                for index2, url in enumerate(value):
                    # URL is usually a string
                    # But in some functions (for display), it returns as
                    # an object with a label attribute, too.
                    # Just check the url portion
                    if isinstance(url, basestring):
                        self.assertEqual(url, expected_obj[key][index2])
                    else:
                        self.assertEqual(url['url'], expected_obj[key][index2])
            else:
                self.assertEqual(value, expected_obj[key])
    

def clearMC3Bank(bank_id):
    """
    Clears out an objective bank plus its objectives and activities
    """
    try:
        clean_bank_id = pickle.loads(bank_id.encode('latin1').replace('%0A','\n')).identifier
    except:
        clean_bank_id = bank_id
        
    # First the assets
    assets = get_all_assets(clean_bank_id)
    try:
        assets = json.loads(assets)
        for asset in assets:
    	    clear_asset(asset['id'], clean_bank_id)
    except:
        pass
    	
    # Then the activities
    activities = get_all_activities(clean_bank_id)
    try:
        activities = json.loads(activities)
        for activity in activities:
    	    clear_activity(activity['id'], clean_bank_id)
    except:
        pass
    	
    # Next the objectives
    objectives = get_all_objectives(clean_bank_id)
    try:
        objectives = json.loads(objectives)
        for objective in objectives:
    	    clear_objective(objective['id'], clean_bank_id)
    except:
        pass
    	
    # Finally the bank itself
    clear_objectivebank(clean_bank_id)

def str_to_unicode(object):
    """
    Convert a list of dicts from str key / value to unicode key / value
    """
    new_wrapper = []
    for inner_object in object:
        new_obj = {}
        for key, attribute in inner_object.iteritems():
            new_key = unicode(key)
            if isinstance(attribute, basestring):
                new_attr = unicode(attribute)
            else:
	            new_attr = attribute
            new_obj[new_key] = new_attr
        new_wrapper.append(new_obj)
    return new_wrapper


class HomepageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        """
        make sure that /vcb/ brings up index.html
        """
        found = resolve('/vcb/')
        self.assertEqual(found.func, index)
    
    def test_home_page_returns_html(self):
        """
        make sure the home page is html
        """
        request = HttpRequest()
        response = index(request)
        expected_page = render_to_string('vcb/index.html')
        self.assertTrue(response.content.decode(), expected_page)
        
class RegistrationTest(TestCase):
    def test_registration_url_resolves_to_registration_view(self):
        """
        make sure that /vcb/register brings up register.html
        """
        found = resolve('/vcb/register/')
        self.assertEqual(found.func, register)
        
    def test_register_page_returns_html(self):
        """
        make sure the registration page is html
        """
        request = HttpRequest()
        response = register(request)
        expected_page = render_to_string('vcb/register.html')
        self.assertTrue(response.content.decode(), expected_page)

    def test_success_page_can_save_a_POST_request(self):
        """
        make sure the registration success page will accept POST requests
        """
        c = Client()
        response = c.post('/vcb/success/',{
            'fname': 'A',
            'lname': 'Student',
            'email': 'me@name.com',
            'passwd': 'password',
            'conpasswd': 'password',
        })
        
        self.assertRedirects(response, '/vcb/dashboard/')

class DashboardTest(TestCase):
    def test_dashboard_url_resolves_to_dashboard_view(self):
        """
        make sure that /vcb/dashboard brings up dashboard.html
        """
        found = resolve('/vcb/dashboard/')
        self.assertEqual(found.func, dashboard)
        
 
