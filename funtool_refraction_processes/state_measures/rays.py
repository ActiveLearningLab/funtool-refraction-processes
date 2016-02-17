# Functions to create rays for each action

import collections
import funtool.state_measure
import funtool_common_processes.reporters.to_repl
import hashlib

Ray= collections.namedtuple('Ray',['direction','origin','magnitude','piece_history'])

@funtool.state_measure.state_and_parameter_data
def full_rays(state,parameters):
    return _full_rays(state)

@funtool.state_measure.state_and_parameter_meta
def full_rays_hash(state,parameters):
    level_number= str(state.groupings['level_id'][0].meta['level_id'])
    piece_histories= ','.join(sorted([str(ray.piece_history) for ray in state.data['full_rays']]))
    return hashlib.sha1( (level_number+piece_histories).encode()).hexdigest() 

@funtool.state_measure.state_and_parameter_measure
def full_rays_depth(state,parameters):
    try:
        ray_depth= max([ len(ray.piece_history) - 2  for ray in state.data.get('full_rays',[]) ])
    except:
        ray_depth= None
    return  ray_depth

@funtool.state_measure.state_and_parameter_data
def full_operator_rays(state,parameters):
    return _full_operator_rays(state)

def _full_rays(state):
    rays= _source_rays(state)
    while any([ ray.direction for ray in rays ]):
        rays= _step_rays(state, rays)
    return rays

def _full_operator_rays(state):
    level_pieces= state.groupings['level_id'][0].data['pieces']
    return [ _full_operator_ray_history( ray, level_pieces ) for ray in state.data['full_rays'] ]


def _source_rays(state):
    source_rays= []
    for (piece_id,piece_details) in state.groupings['level_id'][0].data['pieces'].items():
        if piece_details['piece_type']== 'FGLaserSource':
            try:
                piece_location= next( loc for loc, pid in state.data['piece_locations'].items() if pid == piece_id  )
            except:
                # This should never happen but does because of errors in the game data
                lig= state.groupings['level_instance_id'][0]
                print('Error in Level Instance {} for User {}'.format(lig.meta.get('level_instance_id'), lig.meta.get('user_id')))
                continue
            ray_magnitude= _source_magnitude(piece_details)
            source_rays.append( Ray( piece_details['output_directions'][0],
                                piece_location,
                                ray_magnitude,
                                [ piece_id ]))
    return source_rays 


def _source_magnitude(piece_details):
    if piece_details.get('target_value'):
        return piece_details['target_value']['numerator']/piece_details['target_value']['denominator']
    else:
        return 1

def _step_rays(state, rays):
    new_rays= []
    for ray in rays:
        new_rays += _step_ray(state, ray)
    new_rays= _combine_adders(new_rays)
    return new_rays

def _step_ray(state, ray):
    new_rays= []
    if ray.direction == None:
        new_rays.append(ray)
    else:
        (next_piece, piece_location)= _next_piece(state,ray)
        if next_piece is None:
            piece_history= ray.piece_history.copy()
            piece_history.append(piece_location)
            new_rays.append(Ray(None, piece_location, ray.magnitude, piece_history ))
        else:
            new_rays+= _piece_rays(piece_location, next_piece, state.groupings['level_id'][0].data['pieces'][next_piece], ray)
    return new_rays

def _piece_rays(piece_location, piece_id, piece_details, ray):
    piece_history= ray.piece_history.copy()
    piece_history.append(piece_id)
    if _flip_direction(ray.direction) in piece_details['input_directions'] and len(piece_details['input_directions']) == 1:
        if piece_details['output_directions']:
            return [ Ray(
                        output_direction, 
                        piece_location, 
                        ray.magnitude/len(piece_details['output_directions']), 
                        piece_history)
                    for output_direction in piece_details['output_directions'] ]
        else:
            return [ Ray(
                        None, 
                        piece_location, 
                        ray.magnitude, 
                        piece_history) ]
    else:
        return [ Ray(
                    None, 
                    piece_location, 
                    ray.magnitude, 
                    piece_history) ]
        
def _combine_adders(rays): #TODO placeholder for combining adder rays
    return rays


def _next_piece(state, ray):
    ray_step= _ray_step(ray.direction)
    ray_position= ray.origin
    while ray_position[0] > -1 and ray_position[1] > -1 and ray_position[0] < 10 and ray_position[1] < 10 :
        ray_position= ( ray_position[0] + ray_step[0], ray_position[1] + ray_step[1] )
        step_piece= state.data.get('piece_locations',{}).get(ray_position)
        if step_piece:
            return ( step_piece, ray_position )
    return (None, ray_position)

def _ray_step(direction):
    return {
        "north": ( -1, 0 ),
        "east": ( 0, 1 ),
        "south": ( 1, 0 ),
        "west": ( 0 , -1 )
    }[direction]

def _flip_direction(direction):
    return {
        "north": "south",
        "east": "west",
        "south": "north",
        "west": "east"
    }[direction]

def _full_operator_ray_history( ray, level_pieces ):
    return [ _operator_representation( piece_id, level_pieces ) for piece_id in ray.piece_history ]

def _operator_representation(piece_id,level_pieces):
    if type(piece_id) is tuple:
        return ( '.', None )
    else:
        piece_details= level_pieces[piece_id]
        return {
            'FGLaserBlocker': ( ':', None ),
            'FGLaserDivider': _divider_representation( piece_details ),
            'FGLaserSink': ( '=', _piece_value( piece_details )), #TODO check input direction
            'FGLaserSource': ( '|', _piece_value( piece_details ))
        }.get(piece_details['piece_type'] , ( 'o' , None ))

def _piece_value( piece_details ):
    target_value= piece_details.get('target_value')
    if not (target_value is None):
        return int(target_value['numerator'])/int(target_value['denominator'])
    else:
        return None

def _divider_representation( piece_details ):
    if len(piece_details['output_directions']) == 1:
        return ( 'b', None )
    else:
        return ( '/', len(piece_details['output_directions']) )
 
