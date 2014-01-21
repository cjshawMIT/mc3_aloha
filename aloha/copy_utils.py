import pdb

from dlkit.services.learning import LearningManager
from dlkit.services.repository import RepositoryManager
#from dlkit.services.type_ import TypeManager
from dlkit.services.osid_errors import NotFound, IllegalState

# Modified Sept 17, 2013, cshaw
# to use id's instead of names (since names may be the same for
# copying a class to a new semester)
#def copy_bank(source_bank_name, destination_bank_name):
#
#    lm = LearningManager()
#    rm = RepositoryManager()
#
#    ##
#    # Check if source ObjectiveBank exists
#    source_bank = None
#    for bank in lm.objective_banks:
#        if bank.display_name.text == source_bank_name:
#            source_bank = bank
#            source_bank_repository = rm.get_repository(source_bank.ident)
#    if source_bank is None:
#        raise NotFound()
#
#    ##
#    # Check if destination ObjectiveBank exists
#    for bank in lm.objective_banks:
#        if bank.display_name.text == destination_bank_name:
#            raise IllegalState('bank named ' + destination_bank_name + ' already exists.')
#
#    ##
#    # Create new destination ObjectiveBank
#    bank_form = lm.get_objective_bank_form_for_create()
#    bank_form.display_name = destination_bank_name
#    bank_form.description = 'copy of ' + source_bank_name + ' objective bank for testing.'
#    destination_bank = lm.create_objective_bank(bank_form)
##
# And get related Repository
    #destination_bank_repository = rm.get_repository(destination_bank.ident)
def copy_bank(source_bank_id, destination_bank_id):
    lm = LearningManager()
    rm = RepositoryManager()
    
    source_bank = None
    for bank in lm.objective_banks:
        if bank.ident == source_bank_id:
            source_bank = bank
            source_bank_repository = rm.get_repository(source_bank.ident)
    if source_bank is None:
        raise NotFound()
            
    destination_bank = None
    for bank in lm.objective_banks:
        if bank.ident == destination_bank_id:
            destination_bank = bank
            destination_bank_repository = rm.get_repository(destination_bank.ident)
    if destination_bank is None:
        raise NotFound()


    ##
    # Copy all the Objectives
    objective_map = dict()
    for source_objective in source_bank.get_objectives():
        print "copying objective:", source_objective.display_name.text
        destination_objective = copy_objective_to_bank(source_objective, destination_bank)
        key = source_objective.ident.namespace + ':' + source_objective.ident.identifier + '@' + source_objective.ident.authority
        objective_map[key] = destination_objective.ident

    ##
    # Copy all Objective child relationships
    for source_objective in source_bank.get_objectives():
        print "copying children for:", source_objective.display_name.text
        for child_objective_id in source_bank.get_child_objective_ids(source_objective.ident):
            objective_key = source_objective.ident.namespace + ':' + source_objective.ident.identifier + '@' + source_objective.ident.authority
            child_key = child_objective_id.namespace + ':' + child_objective_id.identifier + '@' + child_objective_id.authority
            destination_bank.add_child_objective(objective_map[objective_key], objective_map[child_key])
    
    ##
    # Copy all Objective requisite relationships
    for source_objective in source_bank.get_objectives():
        print "copying pre-reqs for:", source_objective.display_name.text
        for req_objective in source_bank.get_requisite_objectives(source_objective.ident):
            objective_key = source_objective.ident.namespace + ':' + source_objective.ident.identifier + '@' + source_objective.ident.authority
            req_key = req_objective.ident.namespace + ':' + req_objective.ident.identifier + '@' + req_objective.ident.authority
            destination_bank.assign_objective_requisite(objective_map[objective_key], objective_map[req_key])
    
    ##
    # Copy all the Activities and Assets
    for source_activity in source_bank.get_activities():
        print "copying activity:", source_activity.display_name.text
        destination_activity = copy_activity_to_bank(source_activity, destination_bank, destination_bank_repository, objective_map)

            
def copy_objective_to_bank(source_objective, destination_bank):
    objective_form = destination_bank.get_objective_form_for_create()
    objective_form.display_name = source_objective.display_name.text
    objective_form.description = source_objective.description.text
    objective_form.genus_type = source_objective.genus_type
    if source_objective.has_assessment():
        objective_form.assessment = source_objective.assessment_id
    if source_objective.has_cognitive_process():
        objective_form.cognitive_process = source_objective.cognitive_process_id
    if source_objective.has_knowledge_category():
        objective_form.knowledge_category = source_objective.knowledge_category_id
    return destination_bank.create_objective(objective_form)

def copy_activity_to_bank(source_activity, destination_bank, destination_bank_repository, objective_map):
    source_objective_id = source_activity.get_objective_id()
    key = source_objective_id.namespace + ':' + source_objective_id.identifier + '@' + source_objective_id.authority
    activity_form = destination_bank.get_activity_form_for_create(objective_map[key])
    activity_form.display_name = source_activity.display_name.text
    activity_form.description = source_activity.description.text
    activity_form.genus_type = source_activity.genus_type
    if source_activity.is_asset_based_activity():
        asset_id_list = []
        for source_asset in source_activity.get_assets():
            asset_id_list.append(copy_asset_to_bank_repository(source_asset, destination_bank_repository).ident)
        activity_form.assets = asset_id_list
    if source_activity.is_course_based_activity():
        pass
    if source_activity.is_assessment_based_activity():
        pass
    print activity_form._my_map
    return destination_bank.create_activity(activity_form)

def copy_asset_to_bank_repository(source_asset, destination_bank_repository):
    asset_form = destination_bank_repository.get_asset_form_for_create()
    asset_form.display_name = source_asset.display_name.text
    asset_form.description = source_asset.description.text
    asset_form.genus_type = source_asset.genus_type
    asset_form.title = source_asset.title.text
    asset_form.public_domain = source_asset.is_public_domain()
    asset_form.copyright = source_asset.copyright.text
    asset_form.distribute_verbatim = source_asset.can_distribute_verbatim()
    asset_form.distribute_alterations = source_asset.can_distribute_alterations()
    asset_form.distribute_compositions = source_asset.can_distribute_compositions()
    asset_form.source = source_asset.source_id
    provider_links = []
    for i in source_asset.provider_link_ids:
        provider_links.append(i)
    asset_form.provider_links = provider_links
#    asset_form.created_date = source_asset.created_date
    asset_form.published = source_asset.is_published()
#    asset_form.published_date = source_asset.published_date
    asset_form.principal_credit_string = source_asset.principal_credit_string.text
    asset_form.composition_id = source_asset.composition_id
    destination_asset = destination_bank_repository.create_asset(asset_form)
    for source_asset_content in source_asset.get_asset_contents():
        copy_asset_content(source_asset_content, destination_asset.ident, destination_bank_repository)
    return destination_asset

def copy_asset_content(source_asset_content, destination_asset_id, destination_bank_repository):
    asset_content_form = destination_bank_repository.get_asset_content_form_for_create(destination_asset_id)
    asset_content_form.display_name = source_asset_content.display_name.text
    asset_content_form.description = source_asset_content.description.text
    asset_content_form.genus_type = source_asset_content.genus_type
#    asset_content_form.data = source_asset_content.data
    asset_content_form.url = source_asset_content.url
#    for t in source_asset_content.get_accessibility_types():
#        asset_content_form.add_accessibility_type(t)
    destination_bank_repository.create_asset_content(asset_content_form)

def delete_bank_by_name(bank_name):
    lm = LearningManager()
    bank_id = None
    for bank in lm.objective_banks:
        if bank.display_name.text == bank_name:
            bank_id = bank.ident
    if bank_id is None:
        raise NotFound()
    clear_bank(bank_id)
    lm.delete_objective_bank(bank_id)

def clear_bank(bank_id):
    lm = LearningManager()
    rm = RepositoryManager()
    bank = lm.get_objective_bank(bank_id)
    repository = rm.get_repository(bank_id)
    delete_all_objectives(bank)
    delete_all_assets(repository)

def delete_all_objectives(bank):
    for objective in bank.get_objectives():
        print "deleting objective:", objective.display_name.text
        delete_objective(objective.ident, bank)

def delete_all_assets(repository):
    for asset in repository.get_assets():
        print "deleting asset:", asset.display_name.text
        repository.delete_asset(asset.ident)

def delete_objective(objective_id, bank):
    for activity in bank.get_activities_for_objective(objective_id):
        print "    deleting activity:", activity.display_name.text
        bank.delete_activity(activity.ident)
    bank.delete_objective(objective_id)

