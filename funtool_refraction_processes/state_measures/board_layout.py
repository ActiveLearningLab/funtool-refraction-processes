# Functions to layout pieces for each action

import funtool.state_measure

@funtool.state_measure.analysis_collection_and_parameter_data
def piece_locations(analysis_collection, measure_parameters):
    if analysis_collection.states_dict.get('previous') is None:
        level_group= analysis_collection.state.groupings.get('level_id',[])
        if not level_group:
            return {}
        else:
            return level_group[0].data['initial_layout']
    else:
        previous_locations= analysis_collection.states_dict['previous'].data.get('piece_locations',{})
        return _new_piece_locations(previous_locations, analysis_collection.state)

def _new_piece_locations(initial_pieces,state):
    new_pieces= initial_pieces.copy()
    if state.data.get('action_id'):
        if state.data.get('action_id') == 1: #place event
            action_index= state.data.get('action_detail',{}).get('index')
            piece_id= state.data.get('action_detail',{}).get('id')
            level_groups= state.groupings.get('level_id')
            if action_index and piece_id and level_groups and level_groups[0].data['pieces'].get(piece_id):
                new_pieces[(action_index//10,action_index%10)]= piece_id
        if state.data.get('action_id') == 3: #remove from board
            piece_id= state.data.get('action_detail',{}).get('id')
            if piece_id in initial_pieces.values():
                matched_locations= [ location for location,initial_id in initial_pieces.items() if initial_id == piece_id ]
                if len(matched_locations) == 1:
                    new_pieces.pop(matched_locations[0])
                else:
                    print('Error in layout of {}'.format(state.groupings.get('level_id').meta['level_id']) )
    return new_pieces

def _action_ids_and_names(): #Reference for action type
    return [(1, 'MANIP_PLACED_GRID'),
         (2, 'MANIP_PLACED_PAGE'),
         (3, 'MANIP_PICKUP'),
         (4, 'MAGNIFY'),
         (5, 'PAGE_NEXT'),
         (6, 'PAGE_PREVIOUS'),
         (7, 'TUTORIAL_STARTED'),
         (8, 'TUTORIAL_ADVANCED'),
         (9, 'COIN_GET_EVENT'),
         (10, 'RESET_EVENT'),
         (11, 'TUTORIAL_UF_NEXT_BUTTON'),
         (12, 'TUTORIAL_UF_PREV_BUTTON'),
         (13, 'TUTORIAL_UF_EXIT_BUTTON'),
         (14, 'TUTORIAL_DEL_NEXT_BUTTON'),
         (15, 'TUTORIAL_DEL_PREV_BUTTON'),
         (16, 'TUTORIAL_HELP_BUTTON'),
         (17, 'TUTORIAL_DEL_OK_BUTTON'),
         (18, 'TUTORIAL_UF_START'),
         (20, 'WIN_EVENT'),
         (30, 'KONGREGATE_USER_INFO'),
         (31, 'KONGREGATE_POINTS'),
         (32, 'free'),
         (40, 'HINT_DISPLAYED'),
         (41, 'HINT_OK_BUTTON'),
         (42, 'HINT_INCORRECT_PIECE_DIRECTION'),
         (43, 'HINT_SPLIT_IN_TWO'),
         (44, 'HINT_WONT_SPLIT_TWICE'),
         (45, 'HINT_INCORRECT_FACTORIZATION'),
         (46, 'HINT_BUTTON'),
         (47, 'HINT_EARNED'),
         (48, 'HINT_REACTIVE_FIRED'),
         (49, 'HINT_TIMER_UP'),
         (50, 'START_OVER'),
         (51, 'CONTINUE_SAVED_GAME'),
         (52, 'NEW_GAME'),
         (53, 'GRADE_QUESTION_RESPONSE'),
         (54, 'GRADE_QUESTION_OK_BUTTON'),
         (55, 'GRADE_QUESTION_CANCEL_BUTTON'),
         (56, 'START_OVER_OK_BUTTON'),
         (57, 'START_OVER_CANCEL_BUTTON'),
         (60, 'HINT_X_BUTTON'),
         (61, 'HINT_NOTIFICATION_X_BUTTON'),
         (62, 'HINT_ORB_DEACTIVATED'),
         (63, 'INCORRECT_SINK_DIRECTIONALITY'),
         (64, 'HINT_ORB_CLICK'),
         (100, 'EDITOR_PIECE_CREATED_FROM_BIN'),
         (101, 'EDITOR_HELD_PIECE_DESTROYED'),
         (102, 'EDITOR_HELD_PIECE_PLACED'),
         (103, 'EDITOR_PIECE_PICKED_UP'),
         (104, 'EDITOR_GRID_PIECE_CREATED'),
         (105, 'EDITOR_GRID_PIECE_DESTROYED'),
         (106, 'EDITOR_TEST_SESSION_INITIATED'),
         (200, 'TEST_ANSWER'),
         (201, 'SURVEY_ANSWER'),
         (202, 'TEST_SELECT'),
         (203, 'TEST_DESELECT'),
         (204, 'TEST_BUTTON'),
         (205, 'TEST_PICKUP'),
         (206, 'TEST_PLACED'),
         (207, 'TEST_START_QUESTION')]
