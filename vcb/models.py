import datetime
import json
import requests
import logging
import pdb
import inspect
import pickle

from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder

from dlkit.services.learning import LearningManager
from dlkit.services.repository import RepositoryManager
from dlkit.services.type_ import TypeManager
from dlkit.services.osid_errors import NotFound, IllegalState
from dlkit.primitives import Id

from django.contrib.auth.models import User

from dateutil import parser
#from mc3_learning_adapter_py.mc3_http import create_objective, update_objective_parentids, create_activityasset, create_objectivebank, get_activity, get_objective, get_all_activities, get_root_objectives, get_asset, get_objective_children, get_activities, get_assets, get_objective_bank, put_activity_extension, get_activity_extension
from vcb.vcb_utils import *
from vcb.copy_utils import copy_bank
"""
    Model to cover topics in each lecture / lab / recitation
    Data needs to be uploaded from a CSV file with columns equal
    to the data fields defined below
  
    classnum = lecture 2 / lab 3 / recitation 1, etc.
    sequence is the sequence number of the classtype (i.e. lecture 1, lab 4, etc.)
    branch = one of the four main concept categories
    speaker = class / section speaker on the video 
    
    =============
    updated jan 19, 2013, cshaw
    * removed auto_now_add=True from pub_date so that the user-specified
       date is saved in the database and is required (so videos are only
       shown after this date)
    * added was_published module
    =============
    updated feb 4, 2013, cshaw
    * added subbranch, classcode, topiccode columns per talk with Professors Kamrin and Reis
    =============
    updated feb 26, 2013 pwilkins
    * added recorddate field; the date that the video was originally recorded.
    =============
    updated jul 12, 2013 cshaw
    * complete refactored the database to try and match the MC3 model
    * makes it more relational, instead of CSV file-dump
    * 3 tables that will emulate MC3 (when integrating with MC3, we will have to automate
        some of the repeated requests to get the detailed info. For example, to get a video
        URL, in MC3 involves 3 or 4 calls to get Activity ID, then Asset ID, then AssetContentURL.
        Here, assume a single call to the model can return the URL)
        * These tables are Objectives (i.e. topics), Sub-Objectives (i.e. subbranch like Stress I), and Activities (i.e. video tags)
    * 2 tables that will be needed to store information outside of MC3, even after integration.
        * These tables are Class / Subjects (i.e. 2.002 or 3.032) and Class Session (i.e. Lecture 1,
            Lab 2). 
        * Subjects -> Objectives in MC3
        * Class session -> Activity in MC3, Subjects in Video Search Tool (VST)
    =============
    updated august 2013 cshaw
    * Connecting primarily to MC3, minimal local data stored
"""

class Clicks(models.Model):
    """
    Records tag clicking and links them to a class
    """
    user = models.ForeignKey(User)
    activity = models.ForeignKey('MC3Activities', related_name='activity')
    timestamp = models.DateTimeField('Click time', auto_now_add = True)
    
    def save(self, *args, **kwargs):
        """
        """   
        if not self.pk:
            self.timestamp = timezone.now()
        super(Clicks, self).save(*args, **kwargs)

class Contacts(models.Model):
    """
    Class contacts / instructors
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    role = models.CharField(max_length=100)

class Classes(models.Model):
    """
    This is a lookup table that identifies which classes are available in the system
    This allows users to select and view videos from multiple classes, i.e. 2.002 or 3.032
    
    Updates:
    * Sept 5, 2013, cshaw
        * Added access code--students can sign up for 1 class, when they type in the
             access code on registration
    * Sept 16, 2013, cshaw
        * Moved semesters to here to get classes with multiple semesters...
    * Sept 17, 2013, cshaw
        * Added copy_to method
        * Replace all newlines in pickled IDs with %0A so they can be passed in the URL
            http://stackoverflow.com/questions/3871729/transmitting-newline-character-n
    Issues:
    """
    allow_download = models.BooleanField(default=False)
    allow_sharing = models.BooleanField(default=False)
    allow_transcripts = models.BooleanField(default=False)
    access_code = models.CharField(max_length = 9, unique = True)
    class_name = models.CharField(max_length = 150)
    class_number = models.CharField(max_length = 10)
    clicks = models.ManyToManyField(Clicks, blank=True)
    contacts = models.ManyToManyField(Contacts, blank=True)
    is_active = models.BooleanField(default=True)
    obj_bank_id = models.CharField(max_length = 350) # MC3 Bank ID
    semester = models.CharField(max_length = 100)
    
    def copy_to(self, new_class_id):
        """
        Copy the self class to the new class, including all activities, objectives, etc.
        """
        try:
            # do this on MC3 first
            source_id = pickle.loads(self.obj_bank_id.encode('latin1'))
            destination_id = pickle.loads(new_class_id.encode('latin1'))
            local_new_class = Classes.objects.get(obj_bank_id = new_class_id)
            local_new_class_id = local_new_class.id
#            copy_bank(source_id, destination_id)
            
            destination_bank = set_obj_bank(new_class_id)
            
            roots = source_bank.get_root_objectives()
            
            for obj in roots:
                new_map = ClassMC3Map.objects.create(
                        umbrella_class_id = local_new_class_id,
                        mc3_objective_id = pickle.dumps(obj.ident).decode('latin1')
                )
                obj_children = source_bank.get_child_objectives(obj_result.ident)
                
            original_sessions = ClassSessions.objects.filter(umbrella_class_id = self.id)
            for session in original_sessions:
                new_session = ClassSessions.objects.create(
                        umbrella_class_id = local_new_class_id,
                        session_date = session.session_date,
                        session_name = session.session_name,
                        sequence_order = session.sequence_order
                )
            logging.info('Copied class ' + str(self.id) + ' to ' + str(local_new_class_id) + ' on MC3')
        except:
            pass
            
        # Then do this locally
        try:
            # First copy the objectives from ClassMC3Map
            original_mc3map = ClassMC3Map.objects.filter(umbrella_class_id = self.id)
            local_new_class = Classes.objects.get(obj_bank_id = new_class_id)
            local_new_class_id = local_new_class.id
            # push list pairs [old_id, new_id]. This will be needed for the ObjectiveParentMap?
            obj_id_map = {}
            obj_parent_ids = []
            for obj in original_mc3map:
                objective = MC3Objectives.objects.get(mc3_id = obj.mc3_objective_id)
                
                new_obj = MC3Objectives(
                        name = objective.name,
                        obj_type = objective.obj_type,
                        sequence_order = objective.sequence_order
                )
                
                new_obj.save(new_class_id)
                
                new_map = ClassMC3Map.objects.create(
                        umbrella_class_id = local_new_class_id,
                        mc3_objective_id = new_obj.mc3_id
                )
                
                obj_id_map[objective.mc3_id] = new_obj.mc3_id
                obj_parent_ids.append(objective.mc3_id)
            
            def find_children(parent_mc3_id):
                children = ObjectiveParentMap.objects.filter(parent_mc3_id = parent_mc3_id)
                return children
            
            while True:
                if len(obj_parent_ids) <= 0:
                    break
                else:
                    parent_mc3_id = obj_parent_ids.pop()
                    children = find_children(parent_mc3_id)
                    for child in children:
                        try:
                            child_obj = MC3Objectives.objects.get(mc3_id = child.child_mc3_id, is_active = True)
                            if child_obj:
                                obj_parent_ids.append(child_obj.mc3_id)
                                
                                new_child = MC3Objectives(
                                        name = child_obj.name,
                                        obj_type = child_obj.obj_type,
                                        sequence_order = child_obj.sequence_order
                                )
                                
                                new_child.save(new_class_id)
                                
                                obj_id_map[child.child_mc3_id] = new_child.mc3_id
                                
                                new_map = ObjectiveParentMap(
                                        parent_mc3_id = obj_id_map[parent_mc3_id],
                                        child_mc3_id = obj_id_map[child.child_mc3_id]
                                )
                                
                                new_map.save(new_class_id)
                        except:
                            pass
            
            # now find the activities associated with the old objectives
            act_id_map = {}
            for old_mc3_id, new_mc3_id in obj_id_map.iteritems():
                try:
                    activities = MC3Activities.objects.filter(mc3_objective_id = old_mc3_id, is_active = True)
                    for activity in activities:
                        new_act = MC3Activities(
                                mc3_objective_id = new_mc3_id,
                                viddate = activity.viddate,
                                recorddate = activity.recorddate,
                                subject = activity.subject,
                                speaker = activity.speaker,
                                roughtime = activity.roughtime,
                                techtvtime = activity.techtvtime,
                                techtvtimesecs = activity.techtvtimesecs,
                                views = 0,
                                pub_date = activity.pub_date,
                                sequence_order = activity.sequence_order
                        )
                        
                        # don't know session name yet?
                        new_act.save(new_class_id, new_mc3_id, '')
                        
                        urls = activity.video_urls.all().order_by('resolution_order')
                        for url in urls:
                            new_act.video_urls.add(url)
                        
                        act_id_map[activity.mc3_id] = new_act.mc3_id
                except:
                    pass
            
            # Then class sessions from ClassSessions
            try:
                original_sessions = ClassSessions.objects.filter(umbrella_class_id = self.id, is_active = True)
                for session in original_sessions:
                    new_session = ClassSessions.objects.create(
                            umbrella_class_id = local_new_class_id,
                            session_date = session.session_date,
                            session_name = session.session_name,
                            sequence_order = session.sequence_order
                    )
                    
                    old_sessions = SessionsMC3Map.objects.filter(session_id = session.id)
                    
                    for old_act in old_sessions:
                        new_act_id = act_id_map[old_act.mc3_activity_id]
                        new_session_map = SessionsMC3Map.objects.create(
                                session = new_session,
                                mc3_activity_id = new_act_id
                        )
                    
                logging.info('Copied class ' + str(self.id) + ' to ' + str(local_new_class_id))
                success = True
            except:
                success = False
        except:
            logging.info('Problem copying class ' + str(self.id) + ' to ' + str(new_class_id))
            success = False
        return success
        
    def get_full_name(self):
        """
        Returns the class's full name and number in an object
        """
        try:
            source_bank = set_obj_bank(self.obj_bank_id)
#            mc3_result = get_objective_bank(self.obj_bank_id)
#            json_result = json.loads(mc3_result)
            
            name = source_bank.display_name.text.split(',')[0]
            number = source_bank.description.text
            
            # For the semester, get from extension record
            clean_bank_id = pickle.loads(self.obj_bank_id.encode('latin1')).identifier
            extension = get_extension(clean_bank_id, clean_bank_id, 'bank')
            semester = extension['semester']
        except:
            name = self.class_name
            number = self.class_number
            semester = self.semester
            
        return {'class_name':name, 'class_number':number, 'semester': semester}
        
    def get_root_objectives(self):
        """
        Gets all the topic-level objectives for an MC3 objective bank
        Updated Jul 31, 2013, to just get the root objectives
        """		
        all_objs = []
        try:
            raise Exception('MC3 linkage not fully functional. Trying local db.')
            source_bank = set_obj_bank(self.obj_bank_id)
            result = source_bank.get_root_objectives()

            if len(result) > 0:
                for obj in result:
                    fullname = obj.display_name.text
                    displayname = truncate_name(fullname)
                    obj_id = pickle.dumps(obj.get_id()).decode('latin1')
                    tmp_obj = {
                        'bank': self.obj_bank_id,
                        'children': [],
                        'item_class': 'objective',
                        'item_id': obj_id,
                        'name': displayname,
                        'source': 'mc3',
                        }
                    
                    if displayname != fullname:
                        tmp_obj['title'] = fullname
                    all_objs.append(tmp_obj)
            else:
                raise Exception('No results from MC3. Trying local db.')
                
        except:
            mc3_objectives = ClassMC3Map.objects.filter(umbrella_class_id = self.id).values_list('mc3_objective_id', flat = True)
            result = []
            try:
                objs = MC3Objectives.objects.filter(
                        mc3_id__in = mc3_objectives, 
                        is_active = True).order_by('sequence_order')
                for obj in objs:
                    fullname = obj.name
                    displayname = truncate_name(fullname)
                    tmp_obj = {
                        'bank': self.obj_bank_id,
                        'children': [],
                        'item_class': 'objective',
                        'item_id': obj.mc3_id,
                        'name': displayname,
                        'source': 'local',
                        }
                    if displayname != fullname:
                        tmp_obj['title'] = fullname
                    all_objs.append(tmp_obj)
            except:
                pass
        return json.dumps(all_objs, cls=DjangoJSONEncoder) 
    
    def get_entire_class(self, sort_method, is_staff=False):
        """
        Gets an entire class, with full names
        Displays either by topic or by session (sort_method)
        """		
        all_objs = []
        try:
            # Pass on MC3 for now...not totally functional with the rest
            # of the site or authorization, anyways
            source_bank = set_obj_bank(self.obj_bank_id)
            result = source_bank.get_root_objectives()
            
            raise Exception('MC3 not fully supported. Using local db.')
            
            if len(result) > 0:
                for obj in result:
                    fullname = obj.display_name.text
                    displayname = fullname
                    obj_id = pickle.dumps(obj.get_id()).decode('latin1')
                    tmp_obj = {
                        'bank': self.obj_bank_id,
                        'children': [],
                        'fullname': fullname,
                        'item_class': 'objective',
                        'item_id': obj_id,
                        'name': displayname,
                        'source': 'mc3',
                        }
                    
                    if displayname != fullname:
                        tmp_obj['title'] = fullname
                    all_objs.append(tmp_obj)
        except:
            def find_children(obj_bank, parent, is_staff):
                """
                Recursively attach the children of the parent
                Objectives plus activities
                """
                objs_list = []
                tmp = json.loads(parent.get_children(obj_bank, is_staff))
                for child in tmp:
                    if child['item_class'] == 'objective':
                        try:
                            tmp_id = pickle.loads(child['item_id'].encode('latin1'))
                            if isinstance(tmp_id, Id):
                                child_id = child['item_id']
                            else:
                                child_id = str(child['item_id'])
                        except:
                            child_id = str(child['item_id'])
                        try:
                            child_handle = MC3Objectives.objects.get(mc3_id = child_id, is_active = True)
                            if child_handle:
                                child['children'] += find_children(obj_bank, child_handle, is_staff)
                                logging.info('Adding to tmp: ' + child['name'])
                        except:
                            pass
                objs_list += tmp
                logging.info('Length of objs_list: ' + str(len(objs_list)))
                return objs_list
            
            if sort_method == 'topics':
                mc3_objectives = json.loads(self.get_root_objectives())
                for mc3_objective in mc3_objectives:
                    try:
                        tmp_id = pickle.loads(mc3_objective['item_id'].encode('latin1'))
                        if isinstance(tmp_id, Id):
                            obj_id = mc3_objective['item_id']
                        else:
                            obj_id = str(mc3_objective['item_id'])
                    except:
                        obj_id = str(mc3_objective['item_id'])
                    try:
                        obj_handle = MC3Objectives.objects.get(mc3_id = obj_id, is_active = True)     
                        if obj_handle:
                            tmp = {
                                'bank': self.obj_bank_id,
                                'children': [],
                                'fullname': obj_handle.name,
                                'item_class': 'objective',
                                'item_id': obj_handle.mc3_id,
                                'name': obj_handle.name,
                                'source': 'local',
                            }           
                            tmp['children'] += find_children(self.obj_bank_id, obj_handle, is_staff)
                            all_objs.append(tmp)
                    except:
                        pass
            else:
                pass 
        finally:
            logging.info('Returning from get_entire_class: ' + json.dumps(all_objs))
            return json.dumps(all_objs, cls=DjangoJSONEncoder) 

    def get_sessions(self, is_class_staff=False):
        """
        Looks up the class's sessions in MC3, using the ClassSessions model
        Returns a JSON-formatted object with sessions, activities
        ==============
        Updates
        ==============
        August 6, 2013. Cshaw
        * Modified so uses MC3 for activities, not local database. Returns the list of
            activities
        """
        sessions = []
        
        try:
            umbrella_sessions = ClassSessions.objects.filter(umbrella_class_id = self.id, is_active = True).order_by('sequence_order', 'session_date')
            for ses in umbrella_sessions:
                fullname = ses.session_name
                displayname = truncate_name(fullname)
                
                tmp_ses = {}
                tmp_ses = {
                    'bank':self.obj_bank_id,
                    'children': [],
                    'item_class': 'session',
                    'item_id': ses.id,
                    'name': displayname,
                    }
                if displayname != fullname:
                    tmp_ses['title'] = fullname
                    
                sessions.append(tmp_ses)
        except:
            pass
            
        return json.dumps(sessions, cls=DjangoJSONEncoder)	

    def get_management_data(self):
        """
        Get management data for a class
        """
        data = {
            'allow_download': self.allow_download,
            'allow_sharing': self.allow_sharing,
            'allow_transcripts': self.allow_transcripts,
            'contacts': []
        }
        contacts = self.contacts.all()
        data['contacts'] = flatten_contacts_list(contacts)
        return data

    def viewed_recently(self, user):
        """
        Looks up video tags that were viewed in the last 7 days and have been published
        """
        recently_viewed_videos = []
        is_class_staff = user.is_staff
        try:
            user_clicks = self.clicks.filter(
                user = user
            )
            mc3_acts_list = []
            for click in user_clicks:
                mc3_acts_list.append(click.activity.mc3_id)
            # umbrella_sessions_list = ClassSessions.objects.filter(
            #         umbrella_class_id = self.id,
            #         is_active = True
            #         ).values_list('id', flat = True)
            # mc3_acts_list = SessionsMC3Map.objects.filter(
            #         session_id__in =
            #         umbrella_sessions_list
            #         ).values_list('mc3_activity_id', flat = True)
            try:
                raise Exception('MC3 linkage not fully functional. Trying local db.')
                clean_bank_id = pickle.loads(self.obj_bank_id.encode('latin1')).identifier
                source_bank = set_obj_bank(self.obj_bank_id)
    #            activities = get_all_activities(self.obj_bank_id)
    #            json_result = json.loads(activities)
                activities = source_bank.get_activities()
                
                # sort activities in descending order of views
                act_metadata = []
                for activity in activities:
                    act_id_raw = pickle.dumps(activity.get_id()).decode('latin1')
                    act_id = activity.get_id().identifier
    
                    extension = get_extension(act_id, clean_bank_id, "activity")
                    views = int(extension['views'])
                    act_data = {
                        'views': views,
                        'id': act_id_raw,
                        'subject': activity.display_name.text
                    }
                    act_metadata.append(act_data)
                
                sorted_acts = sorted(act_metadata, key=lambda k: k['views'], reverse=True)
                
                num_recent = 0
    
                for activity in sorted_acts:
                    clean_act_id = pickle.loads(activity['id'].encode('latin1')).identifier
                    extension = get_extension(clean_act_id, clean_bank_id, "activity")
                    if is_class_staff:
                        video_data = {
                            'id': activity['id'].replace('\n', '%0A'),
                            'subject': activity['subject'],
                            'views': activity['views']
                            }
                        recently_viewed_videos.append(video_data)
                        if num_recent >= 10:
                            break
                    else:
                        pub_date = extension['pub_date']
                        pub_date = parser.parse(pub_date)
                        if pub_date <= timezone.now():
                            video_data = {
                                'id': activity['id'].replace('\n', '%0A'),
                                'subject': activity['subject'],
                                'views': activity['views']
                                }
                            recently_viewed_videos.append(video_data)
                            if num_recent >= 10:
                                break
                    num_recent += 1
            except:
                try:
                    if is_class_staff:
                        mc3_acts = MC3Activities.objects.filter(
                                mc3_id__in = mc3_acts_list,
                                is_active = True
                                ).order_by('-last_view')[:10]
                    else:
                        mc3_acts = MC3Activities.objects.filter(
                                mc3_id__in=mc3_acts_list,
                                pub_date__lte=timezone.now(),
                                is_active = True
                                ).order_by('-last_view')[:10]

                    for activity in mc3_acts:
                        # this makes an assumption that there is only one session associated
                        #   per activity...makes sense conceptually, but could be different
                        #   in the future, which means this might have to change to a .filter()
                        video_data = {
                            'id': activity.mc3_id,
                            'subject': activity.subject,
                            'views': len(self.clicks.filter(
                                user=user,
                                activity=activity
                            ))
                            }
                        recently_viewed_videos.append(video_data)
                except:
                    pass
        except:
            pass
        return json.dumps(recently_viewed_videos, cls=DjangoJSONEncoder)
    
    def search_activities(self, query_string, is_class_staff=False):
        """
        Searches all videos / activities associated with a class
        """
        results = []
        logging.info('Attempting to get MC3 data for class ' + self.class_name)
        try:
            raise Exception('MC3 linkage not fully functional. Trying local db.')
            source_bank = set_obj_bank(self.obj_bank_id)
            source_repository = set_asset_rep(self.obj_bank_id)
            clean_bank_id = pickle.loads(self.obj_bank_id.encode('latin1')).identifier
            # get the ones stored on MC3
            activities = source_bank.get_activities()
#            activities = get_all_activities(self.obj_bank_id)
#            result = json.loads(activities)
            
            logging.info('Attempted to get MC3 data for class ' + 
                    self.class_name + '. Results are: ' + json.dumps(result) 
                    )
            
            related_asset_ids = []
            
            # first match the activity description -> text against the query term. If it
            #    is present, then include the asset id in a new array (max 10) to
            #    to do a second GET request on...
            for activity in activities:
                act_desc = activity.display_name.text + ' ' + \
                        activity.description.text
                if is_class_staff:
                    if query_string.lower() in act_desc.lower():
                        related_asset_ids.append(activity['assetIds'][0])
                        if (len(related_asset_ids) >= 10):
                            break
                else:
                    if query_string.lower() in act_desc.lower():
                        activity_id = activity.get_id().identifier
                        
                        extension = get_extension(activity_id, clean_bank_id, "activity")
                        
                        pub_date = extension['pub_date']
                        pub_date = parser.parse(pub_date)
                        if pub_date <= timezone.now():
                            if query_string.lower() in act_desc.lower():
                                related_asset_ids.append(activity.asset_ids[0])
                                if (len(related_asset_ids) >= 10):
                                    break
                    
            for asset_bean in related_asset_ids:
                asset_id = asset_bean['asset_id']
                activity_id = asset_bean['activity_id']
                
                asset_result = source_repository.get_asset(asset_id)
                
#                asset_r = get_asset(asset_id, self.obj_bank_id)
#                asset_result = json.loads(asset_r)
                # Assume only 0 for now
                asset_contents = asset_result.get_asset_contents().next()
                fullname = asset_contents.display_name.text
                displayname = truncate_name(fullname)
                
                tmp_result = {
                    'id': activity_id.replace('\n', '%0A'),
                    'label': displayname,
                    }
                results.append(tmp_result)
        except:
            # get the ones stored locally
            try:
                umbrella_sessions_list = ClassSessions.objects.filter(
                        umbrella_class_id = self.id,
                        is_active = True
                        ).values_list('id', flat = True)
                mc3_acts_list = SessionsMC3Map.objects.filter( 
                        session_id__in = umbrella_sessions_list
                        ).values_list('mc3_activity_id', flat = True)
                if is_class_staff:
                    mc3_acts = MC3Activities.objects.filter(
                            subject__icontains = query_string, 
                            mc3_id__in = mc3_acts_list,
                            is_active = True
                            ).order_by('-views')[:10]
                else:
                    mc3_acts = MC3Activities.objects.filter(
                            subject__icontains = query_string, 
                            mc3_id__in = mc3_acts_list,
                            pub_date__lte = timezone.now() ,
                            is_active = True
                            ).order_by('-views')[:10]
                
                for act in mc3_acts:
                    fullname = act.subject
                    displayname = truncate_name(fullname)
                    tmp_result = {
                        'id': act.mc3_id.replace('\n', '%0A'),
                        'label': displayname
                        }
                    results.append(tmp_result)
            except:
                pass
                                        
        return json.dumps(results, cls=DjangoJSONEncoder)	

    def save(self, *args, **kwargs):
        """
        Override this to also add new objective banks into MC3
        """            
        if not self.pk:
            logging.info('Succesfully created local class.')
            if not self.access_code:
                self.access_code = self.class_number + id_generator(3)
            try:
                raise Exception('MC3 linkage not fully functional. Using local db.')
                lm = LearningManager()
                bank_form = lm.get_objective_bank_form_for_create()
                bank_form.display_name = self.class_name + ', ' + self.semester
                bank_form.description = self.class_number
                new_bank = lm.create_objective_bank(bank_form)
                
#                mc3_result = create_objectivebank(bank_bean)
#                json_result = json.loads(mc3_result)
                new_bank_id = pickle.dumps(new_bank.get_id()).decode('latin1')
                self.obj_bank_id = new_bank_id
                
                logging.info('Succesfully created MC3 Objective Bank. ' +
                        'With ID ' + new_bank_id)
                
                # Bank's semester goes into extension record
                try:    
                    clean_bank_id = pickle.loads(self.obj_bank_id.encode('latin1')).identifier
                    
                    extension = {
                        'semester': self.semester
                    }
                                     
                    mc3_result = put_extension(extension, clean_bank_id, clean_bank_id, "bank")
                    json_result = json.loads(mc3_result)
                    
                    logging.info('Successfully saved extension data for ' + \
                            self.class_name + ', ' + self.semester + \
                            ' in MC3 bank ' + self.obj_bank_id)
                except:
                    logging.info('Failed to save extension data for ' + \
                            self.class_name + ', ' + self.semester + \
                            ' in MC3 bank ' + self.obj_bank_id)
            except:
                self.obj_bank_id = id_generator()
                logging.info('Could not create a class. MC3 error. \
                        Objective bank not created')
            finally:
                # If an MC3 ID object is passed in, json it
                if isinstance(self.obj_bank_id, Id):
                    self.obj_bank_id = pickle.dumps(self.obj_bank_id).decode('latin1')
                super(Classes, self).save(*args, **kwargs)
        else:
            try:
                clean_bank_id = pickle.loads(self.obj_bank_id.encode('latin1')).identifier
                extension = get_extension_raw(clean_bank_id, clean_bank_id, "bank")
                
                records = extension['recordProperties']
                for record in records:
                    if record['displayName']['text'] == 'semester':
                        record['value'] = self.semester
                
                mc3_result = put_extension_raw(extension, clean_bank_id, clean_bank_id, "bank")
                json_result = json.loads(mc3_result)
                
                logging.info('Successfully updated extension data for ' + \
                        'MC3 bank ' + self.obj_bank_id)
            except:
                logging.info('Failed to update extension data for ' + \
                        'MC3 bank ' + self.obj_bank_id)
           
            # If an MC3 ID object is passed in, json it
            if isinstance(self.obj_bank_id, Id):
                self.obj_bank_id = pickle.dumps(self.obj_bank_id).decode('latin1')
            super(Classes, self).save(*args, **kwargs)

class ClassMC3Map(models.Model):
    """
    Aggregates multiple concepts from MC3 into a single "class" structure.
    Tied to the Classes model as a many-to-many relationship
    """
    # Should only be the Django ID, not MC3 id
    umbrella_class_id = models.CharField(max_length = 1000) 	
    mc3_objective_id = models.CharField(max_length = 350)
    
    def save(self, *args, **kwargs):
        """
        Override the save method to json the mc3_objective_id
        """
        # If an MC3 ID object is passed in, json it
        if isinstance(self.mc3_objective_id, Id):
            self.mc3_objective_id = pickle.dumps(self.mc3_objective_id).decode('latin1')
        super(ClassMC3Map, self).save(*args, **kwargs)

class ClassSessions(models.Model):
    """
    Data to be kept outside of MC3. Links activities to class sessions, like Lecture 1 or Lab 2.
    Needs to link to the Classes model as well as MC3 Activities.
    """
    
    umbrella_class_id = models.CharField(max_length = 350)
    session_date = models.DateField('session date')
    session_name = models.CharField(max_length = 50)
    sequence_order = models.PositiveSmallIntegerField(default = 0)
    is_active = models.BooleanField(default=True)
    
    def get_activities(self, bank, is_class_staff=False):
        """
        method that gets the activities for a class session
        """       
        activities = []
        mc3_acts = SessionsMC3Map.objects.filter(session = self.id).order_by('id')
        
        
        for activity in mc3_acts:
            # this makes an assumption that there is only one session associated
            #   per activity...makes sense conceptually, but could be different
            #   in the future, which means this might have to change to a .filter()
            # now search MC3 for details of each activity
            # need to check for pub_date??
            mc3_id = activity.mc3_activity_id
            addActivity = False
            try:
                mc3_unpickled = pickle.loads(mc3_id.encode('latin1'))
                clean_bank_id = pickle.loads(bank.encode('latin1')).identifier
                mc3_identifier = mc3_unpickled.identifier
                extension = get_extension(mc3_identifier, clean_bank_id, "activity")
                
                pub_date = extension['pub_date']
                pub_date = parser.parse(pub_date)

                if is_class_staff:
                    publish = True
                else:
                    if pub_date <= timezone.now():
                        publish = True
                    else:
                        publish = False

                if publish == True:
                    source_bank = set_obj_bank(bank)
                    act_result = source_bank.get_activity(mc3_unpickled)
                    
#                    mc3_results = get_activity(mc3_id, bank)
#                    json_results = json.loads(mc3_results)
                    objective = act_result.objective_id
                    
                    obj_result = source_bank.get_objective(objective)
                    
#                    mc3_objective = get_objective(objective, bank)
#                    json_objective = json.loads(mc3_objective)
#                    
                    fullname = act_result.display_name.text
                    displayname = truncate_name(fullname)
                    
                    asset_result = act_result.get_assets()
#                    asset_r = get_assets(mc3_id, bank)
#                    asset_result = json.loads(asset_r)
                    
                    for asset in asset_result:
                        # Assume only 0 for now
                        asset_contents = asset.get_asset_contents().next()
                        asset_url = asset_contents.url
                        tmp_activity = {
                            'bank': bank,
                            'class_date': extension['viddate'],
                            'item_class': 'asset',
                            'item_id': mc3_id.replace('\n', '%0A'),
                            'name': displayname,
                            'objective': obj_result.display_name.text,
                            'rec_date': extension['recorddate'],
                            'source': 'mc3',
                            'speaker': extension['speaker'],
                            'subobjective': '',
                            'timestamp': int(extension['techtvtimesecs']),
                            'urls': [asset_url],
                            'views': int(extension['views'])					
                            }
                        if displayname != fullname:
                            tmp_activity['title'] = fullname
                        addActivity = True
                else:
                    addActivity = False
            except:
                try:
                    local_results = MC3Activities.objects.get(mc3_id = mc3_id, is_active = True)
                    if not is_class_staff and local_results.pub_date > timezone.now():
                        # do nothing for students if the publication date is in the future
                        addActivity = False
                    else:
                        objective = MC3Objectives.objects.get(
                                mc3_id = local_results.mc3_objective_id,
                                is_active = True 
                                )
                        
                        fullname = local_results.subject
                        displayname = truncate_name(fullname)
                        tmp_activity = {
                            'bank': bank,
                            'class_date': local_results.viddate,
                            'item_class': 'asset',
                            'item_id': local_results.mc3_id,
                            'name': displayname,
                            'objective': objective.name,
                            'rec_date': local_results.recorddate,
                            'source': 'local',
                            'speaker': local_results.speaker,
                            'subobjective': '',
                            'timestamp': local_results.techtvtimesecs,
                            'urls': [],
                            'views': local_results.views,
                            }
                        for url in local_results.video_urls.all().order_by('resolution_order'):
                            tmp_activity['urls'].append(url.url)
                            
                        if displayname != fullname:
                            tmp_activity['title'] = fullname
                        addActivity = True
                except:
                    pass
            if addActivity:    
                activities.append(tmp_activity)
                            
        return json.dumps(activities, cls=DjangoJSONEncoder)	 
    
class SessionsMC3Map(models.Model):
    """
    Aggregates multiple concepts from MC3 into a single "class" structure.
    Tied to the Classes model as a many-to-many relationship
    """
    
    session = models.ForeignKey(ClassSessions)
    mc3_activity_id = models.CharField(max_length = 350)
    
    def save(self, *args, **kwargs):
        """
        Override the save method to json the mc3_activity_id
        """
        # If an MC3 ID object is passed in, json it
        if isinstance(self.mc3_activity_id, Id):
            self.mc3_activity_id = pickle.dumps(self.mc3_activity_id).decode('latin1')
        super(SessionsMC3Map, self).save(*args, **kwargs)
    
class MC3Objectives(models.Model):
    """
    Used temporarily to emulate the MC3 service. This will include learning objectives (aka topics
    in pre-MC3 terminology). Things like "3D Continuum Mechanics"
    Tied to the classes, class sessions (both non-MC3) and subobjectives, activities (MC3)
    """
    
    mc3_id = models.CharField(max_length = 350)
    name = models.CharField(max_length = 500)
    obj_type = models.CharField(max_length = 100)
    sequence_order = models.PositiveSmallIntegerField(default = 0)
    is_active = models.BooleanField(default=True)
    
    def get_children(self, bank_id, is_class_staff=False):
        """
        Returns the children of this objective--child objectives plus activities
        """
        children = []
        try:
            # Check children first
            logging.info(self.mc3_id)

            source_bank = set_obj_bank(bank_id)
            mc3_unpickled = pickle.loads(self.mc3_id.encode('latin1'))
            
            obj_result = source_bank.get_objective(mc3_unpickled)
            obj_children = source_bank.get_child_objectives(obj_result.ident)
            
#            r = get_objective_children(self.mc3_id, bank_id)
#            logging.info(r)
#            result = json.loads(r)
            if len(obj_children) > 0:
                for child in obj_children:
                    fullname = child.display_name.text
                    displayname = truncate_name(fullname)
                    child_type = child.genus_type
                    child_mc3_id = pickle.dumps(child.get_id()).decode('latin1')
                    tmp_obj = {
                        'bank': bank_id,
                        'children': [],
                        'fullname': fullname,
                        'item_class': 'objective',
                        'item_id': child_mc3_id,
                        'name': displayname,
                        'source': 'mc3',
                    }
                    if displayname != fullname:
                        tmp_obj['title'] = fullname
                    children.append(tmp_obj)
                    # get or create each objective locally, just so there is a local backup...
                    try:
                        objective_handle = MC3Objectives.objects.get(mc3_id = child_mc3_id, is_active = True)
                    except:
                        # Since this node doesn't exist locally, it must be an MC3 node.
                        # So get the name and type from MC3, then store it locally before
                        # calling get_children
                        objective_handle = MC3Objectives(
                            name = fullname,
                            obj_type = child_type,
                            mc3_id = child_mc3_id
                        )
                        
                        objective_handle.save(bank_id)
                        new_parent_map = ObjectiveParentMap(
                            parent_mc3_id = self.mc3_id,
                            child_mc3_id = child_mc3_id
                        )
                        
                        new_parent_map.save(bank_id)
            else:
                raise Exception('No children in MC3. Try local db.')
                    
            # now check assets...have to find activities first then drill down into assets
            logging.info('now here at the activity level')
            
            act_result = source_bank.get_activities_for_objective(obj_result.ident)
            
#            r = get_activities(self.mc3_id, bank_id)
#            logging.info(r)
#            result = json.loads(r)
            
            for activity in act_result:
                activity_id = pickle.dumps(activity.ident).decode('latin1')
                clean_bank_id = pickle.loads(bank_id.encode('latin1')).identifier
                fullname = activity.display_name.text
                displayname = truncate_name(fullname)

                act_identifier = activity.ident.identifier

                extension = get_extension(act_identifier, clean_bank_id, "activity") 
                logging.info(extension)
            
                # only move forward if extension record has values...
                # otherwise will just error out
                try:
                    pub_date = extension['pub_date']
                    pub_date = parser.parse(pub_date)
                    
                    if is_class_staff:
                        publish = True
                    else:
                        if pub_date <= timezone.now():
                            publish = True
                        else:
                            publish = False
                    
                    if publish == True:
    #                    asset_r = get_assets(activity_id, bank_id)
    #                    asset_result = json.loads(asset_r)
    
                        asset_result = activity.get_assets()
                        
    #                    mc3_objective = get_objective(self.mc3_id, bank_id)
    #                    json_objective = json.loads(mc3_objective)
                        
                        for asset in asset_result:
                            # Assume only 0 for now
                            asset_contents = asset.get_asset_contents().next()
                            asset_url = asset_contents.url
                            tmp_act = {
                                'bank': bank_id,
                                'class_date': extension['viddate'],
                                'fullname': fullname,
                                'item_class': 'asset',
                                'item_id': activity_id.replace('\n', '%0A'),
                                'name': displayname,
                                'objective': obj_result.display_name.text,
                                'rec_date': extension['recorddate'],
                                'source': 'mc3',
                                'speaker': extension['speaker'],
                                'subobjective': '',
                                'timestamp': int(extension['techtvtimesecs']),
                                'urls': [asset_url],
                                'views': int(extension['views']),
                            }
                            if displayname != fullname:
                                tmp_act['title'] = fullname
                            children.append(tmp_act)
                            logging.info('Appended activity to the return value')
                            # get or create each activity locally, just so there is a local backup...
                            try:
                                activity_handle = MC3Activities.objects.get(mc3_id = activity_id, is_active = True)
                            except:
                                # Since this node doesn't exist locally, it must be an MC3 activity.
                                # So get the name and type from MC3, then store it locally
                                new_activity = MC3Activities(
                                    mc3_id = activity_id,
                                    last_view = extension['last_view'],
                                    mc3_objective_id = self.mc3_id, 
                                    pub_date = pub_date,
                                    recorddate = extension['recorddate'],
                                    speaker = extension['speaker'], 
                                    subject = fullname,
                                    techtvtimesecs = int(extension['techtvtimesecs']),
                                    viddate = extension['viddate'],
                                    views = int(extension['views']),
                                )
                                
                                new_activity.save(bank_id, self.mc3_id, extension['session_name'])
                                logging.info('Saved the new extension record for ' + fullname)
                                
                                if asset_url.find('.m3u8') >= 0:
                                    vtype = 'hls'
                                elif asset_url.find('.mp4') >= 0:
                                    vtype = 'mp4'
                                else:
                                    vtype = 'generic video'
                                    
                                newlink, created = Links.objects.get_or_create(
                                    vtype = vtype,
                                    url = asset_url
                                )
                                
                                new_activity.video_urls.add(newlink)
                                
                                umbrella_class = Classes.objects.get(obj_bank_id = bank_id)
                                 
                                new_session, ses_created = ClassSessions.objects.get_or_create( 
                                        umbrella_class_id = int(umbrella_class.id), 
                                        session_date = extension['viddate'], 
                                        session_name = extension['session_name'] 
                                )
                                new_session_id = new_session.id
                                new_mc3_map, map_created = SessionsMC3Map.objects.get_or_create( 
                                        session_id = int(new_session_id), 
                                        mc3_activity_id = new_activity.mc3_id 
                                )
                                if ses_created:
                                    logging.info('Succesfully created a new Class Session '
                                            + new_session.session_name + ' in local database')
                                else:
                                    logging.info('Class Session ' + new_session.session_name + 
                                            ' already exists in local database')
                                    
                                if map_created:
                                    logging.info('Successfully mapped activity ' + 
                                            ' to ' + new_session.session_name + ' in local database')
                                else:
                                    logging.info('Failed to map activity ' + 
                                            ' to ' + new_session.session_name + ' in local database')                        
                    else:
                        pass
                except:
                    pass
        except:
            # check local database if MC3 fails for any reason
            try:
                children_list = ObjectiveParentMap.objects.filter(
                        parent_mc3_id = self.mc3_id
                        ).values_list('child_mc3_id', flat = True)
                
                children_objectives = MC3Objectives.objects.filter(
                        mc3_id__in = children_list,
                        is_active = True).order_by('sequence_order')
                for child in children_objectives:
                    fullname = child.name
                    displayname = truncate_name(fullname)
                    tmp_obj = {
                        'bank': bank_id,
                        'children': [],
                        'fullname': fullname,
                        'item_class': 'objective',
                        'item_id': child.mc3_id,
                        'name': displayname,
                        'source': 'local',
                    }
                    if displayname != fullname:
                        tmp_obj['title'] = fullname
                    children.append(tmp_obj)
                
                # now check the activities for any that are directly attached to this objective
                try:
                    if is_class_staff:
                        children_activities = MC3Activities.objects.filter(
                                mc3_objective_id = self.mc3_id,
                                is_active = True
                        ).order_by('sequence_order','recorddate','techtvtimesecs')
                    else:
                        children_activities = MC3Activities.objects.filter( 
                                mc3_objective_id = self.mc3_id, 
                                pub_date__lte=timezone.now(),
                                is_active = True
                        ).order_by('sequence_order','recorddate','techtvtimesecs')
                        
                    for child in children_activities:
                        fullname = child.subject
                        displayname = truncate_name(fullname)
                        tmp_act = {
                            'bank': bank_id,
                            'class_date': child.viddate,
                            'fullname': fullname,
                            'item_class': 'asset',
                            'item_id': child.mc3_id,
                            'name': displayname,
                            'objective': self.name,
                            'rec_date': child.recorddate,
                            'source': 'local',
                            'speaker': child.speaker,
                            'subobjective': '',
                            'timestamp':child.techtvtimesecs,
                            'urls': [],
                            'views': child.views,
                        }
                        
                        for url in child.video_urls.all().order_by('resolution_order'):
                            tmp_obj = {
                                'url': url.url,
                                'label': url.label
                            }
                            tmp_act['urls'].append(tmp_obj)
                        
                        if displayname != fullname:
                            tmp_act['title'] = fullname
                        children.append(tmp_act)
                except:
                    pass
            except:
                pass

        return json.dumps(children, cls=DjangoJSONEncoder) 
    
    def save(self, bankId, *args, **kwargs):
        """
        Override this to also save things in MC3
        """
        if not self.pk:
            logging.info('Successfully created a new local objective. ' +
                    ' in bank ' + bankId)
            if not self.mc3_id:         	
                try:
                    source_bank = set_obj_bank(bankId)
                    obj_form = source_bank.get_objective_form_for_create()
                    obj_form.display_name = self.name
                    obj_form.description = self.name
                    new_obj = source_bank.create_objective(obj_form)
#                    mc3_result = create_objective(objective_bean, bankId)
#                    json_result = json.loads(mc3_result)
                    new_id = pickle.dumps(new_obj.get_id()).decode('latin1')
                    self.mc3_id = new_id
                    logging.info('Successfully created new objective named ' +
                            self.name + ' in MC3 bank ' + bankId)	
                except:
                    self.mc3_id = id_generator()
                    logging.info('Failed to create new objective named ' +
                            self.name + ' in MC3 bank ' + bankId)	
                finally:
                    # If an MC3 ID object is passed in, json it
                    if isinstance(self.mc3_id, Id):
                        self.mc3_id = pickle.dumps(self.mc3_id).decode('latin1')
                    
                    super(MC3Objectives, self).save(*args, **kwargs)
            else:
                # If an MC3 ID object is passed in, json it
                if isinstance(self.mc3_id, Id):
                    self.mc3_id = pickle.dumps(self.mc3_id).decode('latin1')
                
                super(MC3Objectives, self).save(*args, **kwargs)
        else:
            # If an MC3 ID object is passed in, json it
            if isinstance(self.mc3_id, Id):
                self.mc3_id = pickle.dumps(self.mc3_id).decode('latin1')
            
            super(MC3Objectives, self).save(*args, **kwargs)

class ObjectiveParentMap(models.Model):
    """
    Mapping of objectives to parent objectives
    """
    parent_mc3_id = models.CharField(max_length = 350)
    child_mc3_id = models.CharField(max_length = 350)
    
    def save(self, bankId, *args, **kwargs):
        """
        Override this to also save things in MC3
        """   
        if not self.pk:
            try:
                source_bank = set_obj_bank(bankId)
                child_id_unpickled = pickle.loads(self.child_mc3_id.encode('latin1'))
                parent_id_unpickled = pickle.loads(self.parent_mc3_id.encode('latin1'))
                source_bank.add_child_objective(parent_id_unpickled, child_id_unpickled)
#                parent_id = self.parent_mc3_id
#                parent_result = update_objective_parentids(
#                        {'ids':parent_id}, 
#                        self.child_mc3_id, 
#                        bankId
#                )
#                parent_json = json.loads(parent_result)
                
                logging.info('Successfully linked it on MC3 to parent ID ' + self.parent_mc3_id)
            except:
                logging.info('Failed to link it on MC3 to parent ID ')
            finally:
                # If an MC3 ID object is passed in, json it
                if isinstance(self.parent_mc3_id, Id):
                    self.parent_mc3_id = pickle.dumps(self.parent_mc3_id).decode('latin1')
                
                # If an MC3 ID object is passed in, json it
                if isinstance(self.child_mc3_id, Id):
                    self.child_mc3_id = pickle.dumps(self.child_mc3_id).decode('latin1')
                 
                super(ObjectiveParentMap, self).save(*args, **kwargs)
        else:
            # If an MC3 ID object is passed in, json it
            if isinstance(self.parent_mc3_id, Id):
                self.parent_mc3_id = pickle.dumps(self.parent_mc3_id).decode('latin1')
            
            # If an MC3 ID object is passed in, json it
            if isinstance(self.child_mc3_id, Id):
                self.child_mc3_id = pickle.dumps(self.child_mc3_id).decode('latin1')
             
            super(ObjectiveParentMap, self).save(*args, **kwargs)

class Links(models.Model):
    """
    Video url links
    """
    vtype = models.CharField(max_length = 50)
    url = models.CharField(max_length = 300)
    label = models.CharField(max_length = 15, null = True)
    resolution_order = models.PositiveSmallIntegerField(default = 99)
    
    def save(self, *args, **kwargs):
        """
        """
        if not self.pk:
            if not self.resolution_order:
                if type == 'hls':
                    self.resolution_order = 1
                elif type == 'mp4':
                    if label == '1080p':
                        self.resolution_order = 2
                    elif label == '480p':
                        self.resolution_order = 3
                    elif label == '320x240':
                        self.resolution_order = 4
                    else:
                        self.resolution_order = 10
                else:
                    self.resolution_order = 99

        super(Links, self).save(*args, **kwargs)

class Transcripts(models.Model):
    """
    Probably should merge this with Links at some point,
    since they are both URLs...
    """
    url = models.CharField(max_length = 300)
    language = models.CharField(max_length = 10, default="en-US")

class MC3Activities(models.Model):
    """
    Time-tagged asset that includes metadata. So would include video URL, timetag, description, speaker, date of video
    Tied to subobjectives (MC3) and class sessions (VST)
    """
    is_active = models.BooleanField(default=True)
    last_view = models.DateTimeField('last viewed date', auto_now_add = True)
    mc3_id = models.CharField(max_length = 350)
    mc3_objective_id = models.CharField(max_length = 350)
    pub_date = models.DateTimeField('date published')
    recorddate = models.DateField('record date')
    roughtime = models.CharField(max_length = 10, null = True)
    sequence_order = models.PositiveSmallIntegerField(default = 0)
    speaker = models.CharField(max_length = 100, null = True)
    subject = models.CharField(max_length = 300)
    techtvtime = models.CharField(max_length = 10, null = True)
    techtvtimesecs = models.PositiveSmallIntegerField(default = 0)
    transcripts = models.ManyToManyField(Transcripts)
    viddate = models.DateField('video date')
    video_urls = models.ManyToManyField(Links)
    views = models.PositiveIntegerField(default = 0, editable = False)
     
    def __unicode__(self):
        return self.subject

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date < now 

    def was_viewed_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=7) <= self.last_view < now

    def save(self, bankId, parentId, sessionName, *args, **kwargs):
        """
        Custom save module to take care of pub_date auto timestamp
        from stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add
        =============
        updated jan 19, 2013, cshaw
        * only updates last_view, not pub_date (pub_date required now
           to accomodate request that videos only be shown past a 
           specified date)
        updated aug 15, 2013, cshaw
        * added MC3 tie-in
        updated sept 3, 2013, cshaw
        * added MC3 extension data
        updated sept 11, 2013, cshaw
        * tried adding in dlkit
        """   
        if not self.pk:
            self.last_view = timezone.now()
            
            if not self.mc3_id:             
                try:
                    source_bank = set_obj_bank(bankId)
                    source_repository = set_asset_rep(bankId)
                    
                    parentId = pickle.loads(parentId.encode('latin1'))
                    
                    act_form = source_bank.get_activity_form_for_create(parentId)
                    act_form.display_name = self.subject
                    act_form.description = self.subject
                    act_form.genus_type = TypeManager().get_type(**{
                            'namespace': 'mc3-activity',
                            'identifier': 'mc3.learning.activity.asset.based',
                            'authority': 'MIT-OEIT'
                    }) #'mc3-activity%3Amc3.learning.activity.asset.based%40MIT-OEIT'
                    asset_id_list = []
                    
                    # Create the asset to add into the asset_id_list
                    asset_form = source_repository.get_asset_form_for_create()
                    asset_form.display_name = self.subject
                    asset_form.description = self.subject
                    asset_form.genus_type = TypeManager().get_type(**{
                           'namespace': 'mc3-asset',
                           'identifier': 'mc3.learning.asset.url',
                           'authority': 'MIT-OEIT' 
                    }) #'mc3-asset%3Amc3.learning.asset.url%40MIT-OEIT'
                    new_asset = source_repository.create_asset(asset_form)
                    
                    # Now create the asset content for this asset
                    asset_content_form = source_repository.get_asset_content_form_for_create(new_asset.ident)
                    asset_content_form.display_name = self.subject
                    asset_content_form.description = self.subject
                    asset_content_form.url = self.video_urls[0].url # THIS WILL BREAK
                    asset_content_form.genus_type = TypeManager().get_type(**{
                            'namespace': 'mc3-asset-content',
                            'identifier': 'mc3.learning.asset.content.unknown',
                            'authority': 'MIT-OEIT'
                    }) # 'mc3-asset-content%3Amc3.learning.asset.content.unknown%40MIT-OEIT'
                    new_content = source_repository.create_asset_content(asset_content_form)
                    
                    asset_id_list.append(new_asset.ident)
                    act_form.assets = asset_id_list
                    new_act = source_bank.create_activity(act_form)
                    
#                    mc3_result = create_activityasset(activityasset_bean, bankId)
#                    json_result = json.loads(mc3_result)
                    
                    new_id = pickle.dumps(new_act.get_id()).decode('latin1')
                    self.mc3_id = new_id
                    
                    logging.info('Successfully created a new Activity/Asset ' + \
                            self.subject + ' in MC3 bank ' + bankId)

                    try: 
                        ext_id = pickle.loads(new_id.encode('latin1')).identifier
                        clean_bank_id = pickle.loads(bankId.encode('latin1')).identifier
                        
                        extension = {
                            'viddate': self.viddate,
                            'recorddate': self.recorddate,
                            'speaker': self.speaker,
                            'roughtime': self.roughtime,
                            'techtvtime': self.techtvtime,
                            'techtvtimesecs': self.techtvtimesecs,
                            'views': self.views,
                            'pub_date': self.pub_date,
                            'last_view': self.last_view,
                            'session_name': sessionName
                        }
                     
                        mc3_result = put_extension(extension, ext_id, clean_bank_id, "activity")
                        json_result = json.loads(mc3_result)
                        
                        logging.info('Successfully saved extension data for ' + \
                                self.subject + ' in MC3 bank ' + bankId)
                    except:
                        logging.info('Failed to save extension data for ' + \
                                self.subject + ' in MC3 bank ' + bankId)
                except:
                    self.mc3_id = id_generator()
                    logging.info('Failed to create a new Activity/Asset ' + \
                            self.subject + ' in MC3 bank ' + bankId + '. Local ID is: ' + \
                            self.mc3_id)
                finally:  
                    # If an MC3 ID object is passed in, json it
                    if isinstance(self.mc3_id, Id):
                        self.mc3_id = pickle.dumps(self.mc3_id).decode('latin1')
                    
                    # If an MC3 ID object is passed in, json it
                    if isinstance(self.mc3_objective_id, Id):
                        self.mc3_objective_id = pickle.dumps(self.mc3_objective_id).decode('latin1')     
                    super(MC3Activities, self).save(*args, **kwargs)
            else:
                # If an MC3 ID object is passed in, json it
                if isinstance(self.mc3_id, Id):
                    self.mc3_id = pickle.dumps(self.mc3_id).decode('latin1')
                
                # If an MC3 ID object is passed in, json it
                if isinstance(self.mc3_objective_id, Id):
                    self.mc3_objective_id = pickle.dumps(self.mc3_objective_id).decode('latin1')
                super(MC3Activities, self).save(*args, **kwargs)
        else:
            self.last_view = timezone.now()
            try:
                act_id = pickle.loads(self.mc3_id.encode('latin1'))
                ext_id = act_id.identifier
                clean_bank_id = pickle.loads(bankId.encode('latin1')).identifier
                extension = get_extension_raw(ext_id, clean_bank_id, "activity")
                
                records = extension['recordProperties']
                for record in records:
                    if record['displayName']['text'] == 'views':
                        record['value'] = self.views
                    elif record['displayName']['text'] == 'last_view':
                        record['value'] = self.last_view
                
                mc3_result = put_extension_raw(extension, ext_id, clean_bank_id, "activity")
                json_result = json.loads(mc3_result)
                
                logging.info('Successfully updated extension data for ' + \
                        self.subject + ' in MC3 bank ' + bankId)
            except:
                logging.info('Failed to update extension data for ' + \
                        self.subject + ' in MC3 bank ' + bankId)
                        
            # If an MC3 ID object is passed in, json it
            if isinstance(self.mc3_id, Id):
                self.mc3_id = pickle.dumps(self.mc3_id).decode('latin1')
            
            # If an MC3 ID object is passed in, json it
            if isinstance(self.mc3_objective_id, Id):
                self.mc3_objective_id = pickle.dumps(self.mc3_objective_id).decode('latin1')
            super(MC3Activities, self).save(*args, **kwargs)

def set_obj_bank(bank_id):
    """
    Returns the objective bank that fits the given parameter
    """
    lm = LearningManager()
    try:
        tmp_obj_bank = pickle.loads(bank_id.encode('latin1'))
    except:
        tmp_obj_bank = bank_id
    if isinstance(tmp_obj_bank, Id):
        for bank in lm.objective_banks:
            if bank.ident == tmp_obj_bank:
                source_bank = bank
        return source_bank
    else:
        return None

def set_asset_rep(bank_id):
    """
    Returns the repository manager that fits the given parameter
    """
    lm = LearningManager()
    rm = RepositoryManager()
    tmp_obj_bank = pickle.loads(bank_id.encode('latin1'))
    if isinstance(tmp_obj_bank, Id):
        for bank in lm.objective_banks:
            if bank.ident == tmp_obj_bank:
                source_bank = bank
                source_repository = rm.get_repository(source_bank.ident)
        return source_repository
    else:
        return None

def decode_bank_id(instance, **kwargs):
    """ 
    Override the "get" type methods by unpickling the objective bank id for Classes model
    """
    try:
        tmp_obj_bank = pickle.loads(instance.obj_bank_id.encode('latin1'))
        if inspect.isclass(tmp_obj_bank):
            instance.obj_bank_id = tmp_obj_bank
    except:
        pass

def decode_mc3_objective_id(instance, **kwargs):
    """
    Override the "get" type methods for ClassMC3Map
    """
    try:
        tmp_mc3_obj = pickle.loads(instance.mc3_objective_id.encode('latin1'))
        if inspect.isclass(tmp_mc3_obj):
            instance.mc3_objective_id = tmp_mc3_obj
    except:
        pass

def decode_mc3_activity_id(instance, **kwargs):
    """
    Override the "get" type methods for SessionsMC3Map
    """
    try:
        tmp_mc3_act = pickle.loads(instance.mc3_activity_id.encode('latin1'))
        if inspect.isclass(tmp_mc3_act):
            instance.mc3_activity_id = tmp_mc3_act
    except:
        pass

def decode_mc3_id(instance, **kwargs):
    """
    Override the "get" type methods for MC3Objectives
    """
    try:
        tmp_mc3_id = pickle.loads(instance.mc3_id.encode('latin1'))
        if inspect.isclass(tmp_mc3_id):
            instance.mc3_id = tmp_mc3_id
    except:
        pass

def decode_parent_child_mc3_ids(instance, **kwargs):
    """
    Override the "get" type methods for ObjectiveParentMap
    """
    try:
        tmp_parent = pickle.loads(instance.parent_mc3_id.encode('latin1'))
        if inspect.isclass(tmp_parent):
            instance.parent_mc3_id = tmp_parent
    except:
        pass
    
    try:
        tmp_child = pickle.loads(instance.child_mc3_id.encode('latin1'))
        if inspect.isclass(tmp_child):
            instance.child_mc3_id = tmp_child
    except:
        pass

def decode_mc3_and_objective_ids(instance, **kwargs):
    """
    Override the "get" type methods for MC3Activities
    """
    try:
        tmp_mc3_id = pickle.loads(instance.mc3_id.encode('latin1'))
        if inspect.isclass(tmp_mc3_id):
            instance.mc3_id = tmp_mc3_id
    except:
        pass
    
    try:
        tmp_mc3_obj = pickle.loads(instance.mc3_objective_id.encode('latin1'))
        if inspect.isclass(tmp_mc3_obj):
            instance.mc3_objective_id = tmp_mc3_obj
    except:
        pass
            
models.signals.post_init.connect(decode_bank_id, Classes)
models.signals.post_init.connect(decode_mc3_objective_id, ClassMC3Map)
models.signals.post_init.connect(decode_mc3_activity_id, SessionsMC3Map)
models.signals.post_init.connect(decode_mc3_id, MC3Objectives)
models.signals.post_init.connect(decode_parent_child_mc3_ids, ObjectiveParentMap)
models.signals.post_init.connect(decode_mc3_and_objective_ids, MC3Activities)
