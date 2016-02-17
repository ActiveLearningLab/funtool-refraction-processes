# Process to add level data from XML files to groups or states

import funtool.adaptor

import funtool.state_collection
import funtool.state
import funtool.group

import xml.etree.ElementTree as ET

def import_level_information(adaptor,state_collection, overriding_parameters=None,loggers=None):
    adaptor_parameters= funtool.adaptor.get_adaptor_parameters(adaptor, overriding_parameters)
    parsed_levels= _parse_levels_file(adaptor_parameters['data_location'])
    for (level_id,level_group) in state_collection.groupings.get('level_id',{}).items():
        level_dict= next( (parsed_level for parsed_level in parsed_levels if parsed_level['level_id'] == level_id ), None )
        if level_dict:
            level_group.data['pieces']=level_dict['pieces']
            level_group.data['initial_layout']=level_dict['initial_layout']
    return state_collection 

def _parse_levels_file(file_path):
    return [ _parse_level(file_level) for file_level in ET.parse(file_path).getroot().findall('.//pipesLevel') ]

def _parse_level(level_node):
    level_object={}
    level_object['level_id']= int(level_node.attrib.get('qid'))
    level_object['pieces']= _ordered_pieces(level_node.findall('./laserObject'))
    level_object['initial_layout']= _layout_pieces(level_object['pieces'])
    return level_object

def _ordered_pieces(laser_object_nodes):
    piece_ordering= [
        "FGLaserSource", 
        "FGLaserSink", 
        "FGLaserModifier", 
        "FGLaserDivider", 
        "FGLaserRecombiner", 
        "FGLaserSubtractor", 
        "FGLaserBlocker", 
        "FGCoin"]
    ordered_pieces=[]
    pieces= [ _parse_laser_object(laser_object_node) for laser_object_node in laser_object_nodes ]
    for piece_type in piece_ordering:
        for piece in pieces:
            if piece.get('piece_type') == piece_type:
                ordered_pieces.append(piece)
    return { index:piece for (index,piece) in enumerate(ordered_pieces) }

def _parse_laser_object(laser_object_node):
    laser_object={}
    laser_object['piece_type']= laser_object_node.find('./className').text
    laser_object['input_directions']= [ in_dir.text.lower() for in_dir in laser_object_node.findall('./inputDirection')]
    laser_object['output_directions']= [ out_dir.text.lower() for out_dir in laser_object_node.findall('./outputDirection')]
    if not laser_object_node.find('./targetValue') is None:  # A node without children evaluates to False but not None
        tv_node= laser_object_node.find('./targetValue')
        laser_object['target_value']= { 'numerator':int(tv_node.find('./num').text), 'denominator':int(tv_node.find('./denom').text)}
    if not laser_object_node.find('./index') is None:
        laser_object['index']= int(laser_object_node.find('./index').text)
    return laser_object

def _layout_pieces(pieces):
    return { (piece['index']//10,piece['index']%10):piece_id for (piece_id,piece) in pieces.items() if not _is_moveable(piece) }
    

def _is_moveable(piece):
    moveable_types= ["FGLaserModifier", "FGLaserDivider", "FGLaserRecombiner", "FGLaserSubtractor", "FGCoin"]
    return piece['piece_type'] in moveable_types
