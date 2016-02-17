# Adaptor for Refraction Json action data


import funtool.adaptor

import funtool.state_collection
import funtool.state
import funtool.group

import json


def import_refraction_jsons(adaptor,state_collection, overriding_parameters=None,loggers=None):
    adaptor_parameters= funtool.adaptor.get_adaptor_parameters(adaptor, overriding_parameters)
    jsons_state_collection= _create_state_collection(_parsed_json(adaptor_parameters['data_location']))
    return funtool.state_collection.join_state_collections(state_collection, jsons_state_collection)

def _parsed_json(file_location): #original file is a series of concatenated json objects
    with open(file_location) as f:
        jsons_information= f.read()
    return json.loads( '[' + jsons_information.replace('}\n{','},{') + ']')


def _create_state_collection(all_user_data):
    state_collection= funtool.state_collection.StateCollection([],{})
    for user_data in all_user_data:
        state_collection= funtool.state_collection.join_state_collections(state_collection, _create_user_state_collection(user_data))
    return _add_level_id_groups(state_collection)        

def _create_user_state_collection(user_data):
    user_id= user_data['uid']
    user_group= funtool.group.Group('user_id',[],{},{ 'user_id': user_id },{} ) 
    state_collection= funtool.state_collection.StateCollection([],{})
    funtool.state_collection.add_group_to_grouping(state_collection, 'user_id', user_group, user_id)
    state_collection.groupings['level_instance_id']= {} #create empty grouping in case of no actions
    for (level_id, actions) in user_data['action'].items():
        level_group= funtool.group.Group('level_instance_id',[],{},{ 'level_instance_id': level_id, 'user_id': user_id },{} ) 
        funtool.state_collection.add_group_to_grouping(state_collection, 'level_instance_id', level_group, level_id)
        for action in actions:
            state= funtool.state.State(
                id= None,
                data= { 'action_detail': json.loads(action['a_detail']), 'action_id': action['aid'], 'log_timestamp': action['log_ts'], 'level_time': action['ts']},
                measures= {},
                meta= { 'move_id': action.get('log_id')},
                groupings= {})
            state_collection.states.append(state)
            funtool.group.add_state_to_group(level_group, state)
            funtool.group.add_state_to_group(user_group, state)
            
    for level in user_data.get('levels',[]):
        level_id= level.get('dqid')
        state_collection.groupings['level_instance_id'][level_id]= state_collection.groupings['level_instance_id'].get(
            level_id, 
            funtool.group.Group('level_instance_id',[],{},{ 'level_instance_id': level_id, 'user_id': user_id },{} ) )
        level_group= state_collection.groupings['level_instance_id'][level_id]
        level_group.meta['level_id']= level.get('qid')
        level_group.data['log_timestamp']= level.get('log_q_ts')
        level_group.data['level_detail']= level.get('q_detail')

    return state_collection 

def _add_level_id_groups(state_collection):
    state_collection.groupings['level_id']= state_collection.groupings.get('level_id',{})
    for state in state_collection.states:
        state_level_id= state.groupings['level_instance_id'][0].meta.get('level_id')
        state_collection.groupings['level_id'][state_level_id]= state_collection.groupings['level_id'].get(
            state_level_id, 
            funtool.group.Group('level_id',[],{},{ 'level_id': state_level_id },{}) )
        funtool.group.add_state_to_group(state_collection.groupings['level_id'][state_level_id], state)
    return state_collection
        
