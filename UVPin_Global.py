import math
from functools import partial
import maya.cmds as cmds #type: ignore
import maya.mel as mel #type: ignore

# UVPin Global
# Maya 2024-2026+ | 1.0.0
# Julien Rogar ( https://github.com/JulienRogar/UVPinGlobal )


# --- Variables ---
global_win_instances = []
global_win_count = 0
# --- Variables ---

class UVPin_Global_Window():
    def __init__( self, multi_windows=True, keep_win_pref=False, tab=1 ):
        """
        UVPin_Global\n
        ### Parameters:\n
        'multi_windows' (bool): Create a new window instance of the tool\n
        'keep_win_pref' (bool): Keep window preferences as position or size\n
          Note: If multiple windows, each one will have it's own window preferences saved following their incremented name\n
        'tab' (int): Define which tab to show after creating the window ( 1:Create UVPin, 2:Display UVPin )
        """
        # --- Variables ---
        self.WINDOW = None
        self.SELF_IDX = _Get_WindowIdx( self, multi_windows )
        SELF_IDX = self.SELF_IDX
        self.WIN_NAME = f"UVPin_Global_{SELF_IDX}"
        self.WIN_TITLE = f"UVPin Global - 1.0.0 - [Maya 2024+]"
        self.WIN_SIZE_WH = (821,684)
        self.WIN_SIZEABLE = True
        self.WIN_KEEP_PREF = keep_win_pref

        self.THEME = {
            'main_back':(0.26, 0.26, 0.26),
            'crt':{
                'crt_clmn_back':(0.2, 0.2, 0.2),
                'pick_back_off':(0.17, 0.17, 0.17),
                'pick_back_on':(0.27, 0.27, 0.27),
                'uvpTxt_new':'yellowgreen',
                'uvpTxt_existing':'orange',
                'attrwin_size_wh':(300,500),
                'attrwin_keep_pref':True,
                'attrwin_txt_main':'silver',
                'attrwin_txt_high':'yellowgreen',
                'attrwin_bttn_back':(0.18, 0.28, 0),
                'attrwin_bttnHigh_back':(0.37, 0.32, 0),
                'attrwin_bttnLocked_back':(0.15, 0.15, 0.15),
                'attrwin_txt_empty':'firebrick',
                'main_option_back':(0.15, 0.15, 0.15),
                'extra_option_back':(0, 0, 0),
                'mirror_sel_back':(0.28, 0.13, 0.13),
                'crt_bttn_back':(0.15, 0.15, 0.15)
            },
            'disp':{
                'tb_uvpBttn_back_off':(0.2, 0.2, 0.2),
                'tb_uvpBttn_back_on':(0.3, 0.3, 0.3),
                'tb_sep_back':(0.3, 0.3, 0.3),
                'tb_uvpName_None':'darkred',
                'tb_uvpName_Found':'green',
                'pb_back':(0.3, 0.3, 0.3),
                'pb_field_back':(0.2, 0.2, 0.2),
                'pb_bttn_back':(0.27, 0.27, 0.27),
                'scrla_back':(0.15, 0.15, 0.15),

                'uvp_back':(0.2, 0.2, 0.2),
                'uvp_delete_back':(0.3, 0.12, 0.12),
                'uvp_name_back':(0.215, 0.215, 0.215),
                'uvp_sep_back':(0.13, 0.13, 0.13),
                'uvp_out_back':(0.18, 0.18, 0.18),
                'uvp_out_None_back':(0.11, 0.11, 0.11),
                'uvp_out_Connected_back':(0.9, 0.9, 0.5),
                'uvp_out_sep':(0.9, 0.9, 0.9)
            },
            'done_txt':'yellowgreen',
            'cancel_txt':'darkorange'
        }

        self.ui_items = [ {}, {}, None ] #Create/Display/Main tab
        self.ui_data = (
            { #Create tab
                'uvpin':None, 'uvpin_new':True,
                'geo':'None', 'geo_orig':'None', 'geo_defo':'None', 'geo_type':None,
                'obj':1, 'obj_off':None, 'obj_off_type':1, 'obj_off_ref':None,
                'match':1, 'match_extra':None, #(float, float), str or bool
                'start_idx':0,
                'mirror':False,
                'mirror_name_type':1, 'mirror_name_source':"L_", 'mirror_name_target':"R_",
                'mirror_axis':0, 'mirror_direction':-1, 'mirror_space':None,
                'mirror_bhv':2,
                'mirror_offmtd':2
            },
            { #Display tab
                'uvpin':None,
                'page_current':1, 'page_count':1,
                'item_per_page':20, 'item_count':0,
                'break_co_safety':True, 'compact_idx':None
            }
        )
        self.callback_hook = None
        self.pick_sel = None
        self.pick_selData = None
        self.pick_ui = None
        self.pick_job = None
        self.attrwin = None
        # --- Variables ---

        # --- UI ---
        Build_Window( self, SELF_IDX, tab )
        # --- UI ---

#region --- Functions ---
#region - * General *
# Utility
def _Get_WindowIdx( self, multi_windows:bool ): #Return incremented class windows count
    """ Return incremented class windows count """
    global global_win_instances #Declare as global variables to not get replaced by function-local variable with value assignement
    global global_win_count

    idx = 0
    if multi_windows:
        #Look for existing unused index in the global_win_instances list to recycle
        overwrite_none = False
        for c_instance in global_win_instances:
            if c_instance is None:
                overwrite_none = True
                break
            idx+=1
        
        if overwrite_none: # Recycle index
            global_win_instances[idx] = self
        else: # Create new index
            idx = global_win_count
            global_win_count = idx + 1
            global_win_instances.append(self)
    else:
        idx = 0
        if global_win_count == 0: # Create index 0
            global_win_count = 1
            global_win_instances.append(self)
        else: # Overwrite index 0
            old_count = global_win_count
            global_win_instances[idx] = None
            # Create or overwrite index 0 which has been cleared by window's close command
            if global_win_count == 0:
                global_win_count = 1
                global_win_instances.append(self)
            else:
                global_win_count = old_count
                global_win_instances[idx] = self
    return idx

def _Get_Instance( self_idx:int ): #Return class instance object from index as UI commands can't seem to store class instance objects
    """ Return class instance object from index as UI commands can't seem to store class instance objects """
    return global_win_instances[self_idx]

def _Filter_Selection( limit_type ): #Filter selection and return it and the result type
    """
    Filter selection and return it and the result type (0:empty, 1:no match, 2:match all, 3:match last)\n
    ### Parameters:\n
    'limit_type': (str/list/tuple): Types(s) accepted
    """
    sel = cmds.ls( selection=True, showType=True )
    if sel != []:
        if type(limit_type) is str:
            limit_type = [limit_type]
        
        #Separate objects and their showType
        sel_len = len(sel)
        i = 0
        i2 = 0
        t_sel = [[],[]]
        while i < sel_len:
            t_sel[i2].append( sel[i] )
            i2 = 1 if i2 == 0 else 0
            i+=1
        sel = t_sel
        t_sel = None

        #Get how many selection match limit_type
        match_type = 0
        for sel_type in sel[1]:
            if sel_type in limit_type:
                match_type+=1
        
        if match_type == len(sel[1]): #If every selected object match the limit_type
            return sel[0], 2
        elif sel[1][-1] in limit_type: #If last object matches limit_type
            return [sel[0][-1]], 3
        return sel[0], 1
    return sel, 0

def _Split_NodeAttr( node_path:str, return_both=False, return_attr_found=False ): #Split node and attribute from a string that may contain a node and attribute
    """
    Split node and attribute from a string that may contain a node and attribute\n
    ### Parameters:\n
    'node_path' (str): Object name, can include an attribute\n
    'return_both' (bool): Also return the attribute found with the node\n
    'return_attr_found' (bool): Return a bool, True if the string leads to a node and it's attribute, else False
    ### Return:\n
    node(str) without attr, else node(str) if exists, else None\n
    'return_attr_found': True if found else False\n
    return_both: [ node(str), attr(str) ] if found else node(str)
    """
    node = node_path
    trials = node_path.count('.') + 1
    i = 1
    while i < trials:
        node = node.rsplit('.',i) #Split incrementally
        
        attr = '' #Regroup split parts into a string
        for suffix in node[1:]:
            attr = f"{attr}.{suffix}"
        attr = attr[1:]
        attr_query = attr.rsplit('[')[0] if attr.endswith(']') else attr #Ends with multi attribute index, remove it so attributeQuery works
        
        node = node[0]
        if cmds.objExists( node ):
            if return_both and cmds.attributeQuery( attr_query, node=node, exists=True ): #If the attribute also exists on the node or not looking for the attribute too anyway
                if return_attr_found:
                    return True
                return [ node, attr ]
            else:
                return node
        i+=1
    if return_attr_found:
        return False
    if cmds.objExists( node_path ):
        return node_path
    return None

def _Get_TypeMatchGeo( attr_type:str, node_path=None ): #Check if the type match geometry classification
    """
    Check if the type match geometry classification\n
    ### Parameters:\n
    'attr_type' (str): Attribute's type\n
    'node_path' (str): Attribute's path (node.attr)\n
    ### Return:\n
    True if matching geometry classification/type, else False
    """
    if node_path is not None:
        found = False
        try:
            cmds.getAttr( node_path, type=True, silent=True )
            found = True
        except ValueError:
            return False
        except RuntimeError: #Attribute not found by getAttr
            return False
        except Exception as exception_info:
            cmds.warning( f"[ISSUE:] Unexpected exception while trying to get the type of '{node_path}' (Exception '{exception_info}', type {type(exception_info)})", noContext=True )
            return False
        if found:
            attr_type = cmds.getAttr( node_path, type=True, silent=True )

    if attr_type == 'geometry':
        return True
    attr_class = cmds.getClassification( attr_type ) #Try with Maya's classfication if type isn't enough
    if attr_class is not None and 'geometry' in attr_class[0]:
        return True
    return False

def _Clear_Transform( node:str, extra_attr=None ): #Reset transform values on node
    """
    Reset transform values on node\n
    ### Parameters:\n
    'node' (str): Node name\n
    'extra_attr' (None/list): Include these attributes
    """
    if extra_attr is None:
        transf = ('translate','rotate','scale','shear')
    else:
        transf = ['translate','rotate','scale','shear']
        transf.extend(extra_attr)
        transf = tuple(transf)
    axes = ('X','Y','Z')
    for c_transf in transf:
        for axis in axes:
            if cmds.attributeQuery( f'{c_transf}{axis}', node=node, exists=True ) and cmds.getAttr( f'{node}.{c_transf}{axis}', settable=True ):
                if c_transf == 'scale':
                    cmds.setAttr( f'{node}.{c_transf}{axis}', 1 )
                else:
                    cmds.setAttr( f'{node}.{c_transf}{axis}', 0 )

def _Clear_OffsetParentMatrix( node:str ): #Reset offsetParentMatrix on node
    """
    Reset offsetParentMatrix on node\n
    ### Parameters:\n
    Node name(str)\n
    """
    cmds.setAttr( f'{node}.offsetParentMatrix', 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, type='matrix' )

def _Create_Parent( node:str, hide_joint=False, force_transform=False ): #Create matching object parent
    """
    Create matching object parent\n
    ### Parameters:\n
    'node' (str): Object node name to create a parent above\n
    'hide_joint' (bool): If True and node is a joint, new_parent will have joint visual hidden\n
    'force_transform' (bool): If True, new_parent will be transform regardeless of node's type\n
    ### Return:\n
    new_parent(str)
    """
    parent_type = 'transform'
    parent_suffix = 'offset'
    is_joint = False
    if cmds.nodeType( node ) == 'joint' and not force_transform:
        parent_type = 'joint'
        parent_suffix = 'orig'
        is_joint = True
    
    node_parent = cmds.listRelatives( node, parent=True, fullPath=True )
    new_parent = None
    if node_parent is None: #Hasn't already a parent, create new parent in world
        new_parent = cmds.createNode( parent_type, name=f"{node}_{parent_suffix}", skipSelect=True )
    else: #Has already a parent, create new parent under existing parent
        new_parent = cmds.createNode( parent_type, name=f"{node}_{parent_suffix}", parent=node_parent[0], skipSelect=True )
    
    cmds.parent( node, new_parent, relative=True )
    #Make sure node is at default values under new parent
    if is_joint:
        _Clear_Transform( node, ('jointOrient',) )
        if hide_joint:
            cmds.setAttr( f'{new_parent}.drawStyle', 2 )
    else:
        _Clear_Transform( node )
    return new_parent

def _Remove_Dupli_Suffix( duplicate:str, original:str ): #Remove duplicate suffix from duplicated object name
    """
    Remove duplicate suffix from duplicated object name\n
      Note: Function doesn't support clean rename for duplicate names ending with a number above 9\n
      if not every numbers starting by 1 are already ending objects of same name\n
    ### Parameters:\n
    'duplicate' (str): Duplicated object's name\n
    'original' (str): Original object's name\n
    ### Return:\n
    name (str)
    """
    if duplicate[-1] != original[-1]:
        if len(duplicate) > len(original): #A suffix has been added
            return duplicate[:-1]
        else: #Name must ends with a number that has been incremented instead of adding a suffix, replace original's end number
            return f"{duplicate[:-1]}{original[-1]}"
    else:
        return duplicate

def _Split_FullPath( path:str ): #Split object full path
    """
    Split object full path\n
    ### Parameters:\n
    'path' (str): Object's fullPath\n
    ### Return:\n
    ( before(str), object(str) )
      Note if nothing before object, 'before' is an empty string
    """
    path = path.rsplit('|',1)
    if len(path) == 1:
        path.insert( 0, '' )
    else:
        path[0] = f"{path[0]}|"
    return tuple(path)

# UI
def _Clear_WindowClose( self_idx:int, cmd_idx ): #Clear window closeCommand by replacing it with a print command instead
    """
    Clear window closeCommand by replacing it with a print command instead\n
    ### Parameters:\n
    'self_idx' (int): class object index in global_win_instances\n
    'cmd_idx' (int/str): window closeCommand, int ( 0:Empty ) else str
    """
    cmd = None
    if type(cmd_idx) == int:
        if cmd_idx == 0:
            cmd = partial(_Empty)
        else:
            cmds.warning( f"Unknown _Clear_WindowClose 'cmd_idx': {cmd_idx}" )
    else:
        cmd = cmd_idx
    
    if self_idx > global_win_count:
        cmds.error( f"[ISSUE]: Instance index {self_idx} out of range!", noContext=True )
    cmds.window( global_win_instances[self_idx].WIN_NAME, edit=True, closeCommand=cmd )
    _Pick_Cancel( None, self_idx )

def _Empty(): #Empty function for _Clear_WindowClose()
    """ Empty function for _Clear_WindowClose() """
    pass

def _Build_PickerBttn( parent:str, height:int, field:tuple, sep_width, bttn:tuple, image='colorPickCursor.png' ): #Create a picker button and return it
    """
    Create a picker button and return it\n
    ### Parameters:\n
    'parent' (str): Parent layout name\n
    'height' (int): Height for both elements\n
    'field' (tuple): If not None, text field UI settings ( width(int), defaultText(str), editable(bool), command(str), annotation(str), statusBarMessage(str), backgroundColor(list), dragCallbackCommand(str) )\n
    'sep_width' (None/int): If not None, create separator too at said width\n
    'bttn' (tuple): Button field UI settings ( command(str), annotation(str), statusBarMessage(str), backgroundColor(list), customSize(width, height), dragCallbackCommand(str) )\n
    'image' (str): Bttn image\n
    ### Return:\n
    -If 'field' is None: 'symbolBttn'\n
    -If 'field' is not None: 'txtField', 'symbolBttn'
    """
    txtField = None
    if field is not None:
        if len(field) == 8:
            txtField = cmds.textField(
                height=height, width=field[0],
                editable=field[2], text=field[1],
                changeCommand=field[3], dragCallback=field[7],
                annotation=field[4], statusBarMessage=field[5],
                backgroundColor=field[6],
                parent=parent
            )
        else:
            txtField = cmds.textField(
                height=height, width=field[0],
                editable=field[2], text=field[1],
                changeCommand=field[3],
                annotation=field[4], statusBarMessage=field[5],
                backgroundColor=field[6],
                parent=parent
            )
    if sep_width is not None:
        cmds.separator( height=height, width=sep_width, style='none', parent=parent )
    bttn_wh = (height, height) if len(bttn) == 4 or bttn[4] is None else bttn[4]
    if len(bttn) == 6:
        symbolBttn = cmds.symbolButton(
            height=bttn_wh[1], width=bttn_wh[0],
            image=image, command=bttn[0], dragCallback=bttn[5],
            annotation=bttn[1], statusBarMessage=bttn[2],
            backgroundColor=bttn[3],
            parent=parent
        )
    else:
        symbolBttn = cmds.symbolButton(
            height=bttn_wh[1], width=bttn_wh[0],
            image=image, command=bttn[0],
            annotation=bttn[1], statusBarMessage=bttn[2],
            backgroundColor=bttn[3],
            parent=parent
        )
    if txtField is not None:
        return txtField, symbolBttn
    return symbolBttn

def _Pick_Init( self_idx:int, pick_count:int, result_command, ui_set:str, limit_type=None, skip_deselect=True, ae_check=False, any_sel=False, partial_empty=None ): #Let user pick something
    """
    Let user pick something\n
    ### Parameters:\n
    'self_idx' (int): class object index in global_win_instances\n
    'pick_count' (int): Number of items to pick\n
    'result_command' (function): Command to call once object(s) picked\n
    'ui_set' (str): Call self.pick_ui preset (0:(crt)uvp_picker, 1:(crt)geo_picker, 10:(crt)geoOrig_picker, 11:(crt)geoDefo_picker, 2:(disp)uvp_picker, 3:(crt)match other, 4:(crt)mirror_space)\n
    'limit_type' (None/tuple): If not None, test if already selecting an object of this type and limit picker selection\n
    'skip_deselect' (bool): Don't deselect last item picked\n
    'ae_check' (bool): If limit_type set and existing selection doesn't match, look at current attribute editor tab\n
    'any_sel' (bool): If True return any already selected object regardless of their type\n
    'partial_empty' (bool): Extra 'False' argument from partial() when function call includes argument(s)
    """
    self = _Get_Instance( self_idx )

    if self.callback_hook != None:
        cmds.warning( f"[ISSUE]: A picking is already ongoing. To cancel current picking please select any object or node", noContext=True )
        return
    
    #Set self.pick_selData to store extra informations about the picking context
    if ui_set == 1: #Create - global geometry
        self.pick_selData = 0
    elif ui_set == 10: #Create - original geometry
        self.pick_selData = 1
    elif ui_set == 11: #Crete - deformed geometry
        self.pick_selData = 2

    #Test if not already selecting uvPin
    if any_sel:
        sel = cmds.ls( selection=True, objectsOnly=True )
        if sel != []:
            self.pick_sel = sel
            self.callback_hook = 'picking' #Set a callback hook so not skipped by function
            result_command( self_idx, True )
            return
    if limit_type is not None:
        if type(limit_type) == str:
            limit_type = (limit_type,)

        sel = cmds.ls( selection=True, showType=True )
        found = False
        if sel != []:
            sel, sel_type = _Filter_Selection( limit_type )
            if sel_type == 2 or sel_type == 3:
                found = True
        
        if not found and ae_check:
            sel = mel.eval( '$gAECurrentTab = $gAECurrentTab' )
            if sel != '' and cmds.nodeType( sel ) in limit_type:
                sel = [sel]
                found = True
        
        if found:
            self.pick_sel = sel
            self.callback_hook = 'picking' #Set a callback hook so not skipped by function
            result_command( self_idx, True )
            return
    
    if ui_set == 0:
        self.pick_ui = ( self.ui_items[0]['uvp_picker_symbBttn'], self.THEME['crt']['pick_back_on'], self.THEME['crt']['pick_back_off'] )
    elif ui_set == 1:
        self.pick_ui = ( self.ui_items[0]['geo_picker_symbBttn'], self.THEME['crt']['pick_back_on'], self.THEME['crt']['pick_back_off'] )
    elif ui_set == 10:
        self.pick_ui = ( self.ui_items[0]['geoOrig_picker_symbBttn'], self.THEME['crt']['pick_back_on'], self.THEME['crt']['pick_back_off'] )
    elif ui_set == 11:
        self.pick_ui = ( self.ui_items[0]['geoDefo_picker_symbBttn'], self.THEME['crt']['pick_back_on'], self.THEME['crt']['pick_back_off'] )
    elif ui_set == 2:
        self.pick_ui = ( self.ui_items[1]['uvp_picker_symbBttn'], self.THEME['disp']['tb_uvpBttn_back_on'], self.THEME['disp']['tb_uvpBttn_back_off'] )
    elif ui_set == 3:
        self.pick_ui = ( self.ui_items[0]['match_extra_ui'][1], self.THEME['crt']['pick_back_on'], self.THEME['crt']['pick_back_off'] )
    elif ui_set == 4:
        self.pick_ui = ( self.ui_items[0]['mirror_space_picker_symbBttn'], self.THEME['crt']['pick_back_on'], self.THEME['crt']['pick_back_off'] )
    #Prepare callback for end function
    cmds.callbacks( addCallback=result_command, hook='picking', owner='UVPin_Global'  )
    self.callback_hook = 'picking'
    #Start picking
    _Pick_Selection( self_idx, pick_count, limit_type, skip_deselect )

def _Pick_Init_Callback( self_idx:int, pick_count:int, result_command, ui_set:str, limit_type=None, skip_deselect=True, ae_check=False, any_sel=False,    drgCllBck_drgCtrl=None, drgCllBck_x=None, drgCllBck_y=None, drgCllBck_mod=None ):
    """
    Let user pick something\n
    ### Parameters:\n
    'self_idx' (int): class object index in global_win_instances\n
    'pick_count' (int): Number of items to pick\n
    'result_command' (function): Command to call once object(s) picked\n
    'ui_set' (str): Call self.pick_ui preset (0:(crt)uvp_picker, 1:(crt)geo_picker, 10:(crt)geoOrig_picker, 11:(crt)geoDefo_picker, 2:(disp)uvp_picker, 3:(crt)match other, 4:(crt)mirror_space)\n
    'limit_type' (None/tuple): If not None, test if already selecting an object of this type and limit picker selection\n
    'skip_deselect' (bool): Don't deselect last item picked\n
    'ae_check' (bool): If limit_type set and existing selection doesn't match, look at current attribute editor tab\n
    'any_sel' (bool): If True return any already selected object regardless of their type\n
    'drgCllbck...' parameters required when using a function object in a Maya UI dragCallback argument
    """
    _Pick_Init( self_idx, pick_count, result_command, ui_set, limit_type, skip_deselect, ae_check, any_sel )

def _Pick_Selection( self_idx:int, pick_count_target=1, limit_type=None, skip_deselect=False, _looping=False, _pick_count=0 ): #Start a selection picker
    """
    Start a selection picker\n
    ### Parameters:\n
    'pick_count_target' (int): Amount of selection expected to pick\n
    'limit_type' (str/list): Type(s) to limit selection from\n
    'skip_deselect' (bool): Skip deselecting after picking\n
    '_looping' (bool): Internal, used by the script to call a new pick until target selection count without recreating values\n
    '_pick_count' (int): Internal, used by the script to maintain selection count value\n
    ### Also requires to set values for:\n
    'self.callback_hook' (str): callback hook name\n
    'self.pick_ui' (tuple): ( symbolBttn, backgroundColorHighlight, backgroundColorDefault )
    """
    self = _Get_Instance( self_idx )

    if not _looping: #Init picker
        cmds.symbolButton( self.pick_ui[0], edit=True, backgroundColor=self.pick_ui[1] ) #Highlight picker UI
        cmds.select( clear=True )
        if pick_count_target > 1:
            self.pick_sel = []
    
    limit_type = f"'{limit_type}'" if type(limit_type) == str else limit_type
    self.pick_job = cmds.scriptJob( #Check next selection
        runOnce=True,
        event=['SelectionChanged',partial(_Pick_Selection_Extract, self_idx, _pick_count, pick_count_target, limit_type, skip_deselect)], #Note: Not conditionTrue 'SomethingSelect' as it seems to require deselection to count again as True
        protected=True, parent=self.WINDOW
    )

def _Pick_Selection_Extract( self_idx:int, pick_count:int, pick_count_target:int, limit_type, skip_deselect ): #Called after selecting while running _Pick_Selection()
    """ Called after selecting while running _Pick_Selection() """
    self = _Get_Instance( self_idx )

    self.pick_job = None
    sel = None
    if limit_type is not None:
        sel, sel_type = _Filter_Selection( limit_type )

        if sel_type == 0:
            cmds.warning( f"[ISSUE]: Selection empty!", noContext=True )
        elif sel_type == 1:
            cmds.warning( f"[ISSUE]: {sel} do{'es' if len(sel) < 2 else ''}n't match {'type' if type(limit_type) is str else 'types'} '{limit_type}' !", noContext=True )
            sel = []
    else:
        sel = cmds.ls( selection=True )
    
    if sel != []:
        if pick_count_target > 1:
            self.pick_sel.append(sel)
        else:
            self.pick_sel = sel
        if not skip_deselect:
            cmds.select( clear=True )
    
    pick_count += 1
    if pick_count >= pick_count_target: #Picking done, clear data, reselect old selection and call end function via it's callback
        call_hook = f'{self.callback_hook}'
        cmds.symbolButton( self.pick_ui[0], edit=True, backgroundColor=self.pick_ui[2] )
        cmds.callbacks( self_idx, executeCallbacks=True, hook=call_hook ) #Call end function
        cmds.callbacks( clearCallbacks=True, hook=call_hook, owner='UVPin_Global' )
    else:
        _Pick_Selection( self_idx, pick_count_target, limit_type, skip_deselect, True, pick_count ) #Continue picking

def _Pick_Cancel( self, self_idx:int ): #Stop picking
    """ Stop picking """
    self = _Get_Instance( self_idx )
    if self.callback_hook is None:
        return
    if self.pick_job is not None and cmds.scriptJob( exists=self.pick_job ):
        cmds.scriptJob( kill=self.pick_job, force=True )
    cmds.callbacks( clearCallbacks=True, owner='UVPin_Global' )
    self.callback_hook = None
    self.pick_sel = None
    self.pick_selData = None
    self.pick_ui = None
    cmds.inViewMessage( message="<font color=darkorange>Picking cancelled!</font color>", position="botCenter", fade=True, fadeOutTime=300 )
    print( "[INFO]: Picking cancelled!" )

def _Clear_Layout( name:str ): #Clear a layout's content
    """ Clear a layout's content """
    children = cmds.layout( name, query=True, childArray=True )
    if children is not None:
        cmds.deleteUI( children )

def _Build_AttrWindow( self, self_idx:int, node:str, attr_list:list, ui_data:tuple ): #Build new window to list attribute buttons
    """
    Build new window to list attribute buttons\n
    ### Parameters:\n
    'node' (str): Attributes' node name\n
    'attr_list' (list): List of attributes to build the UI for, [ ( attr(str), (function, self_idx(int), command_str(str), ...) ) ]\n
        'command_str' tags replaced at build: \<node>, \<attr>\n
    'ui_data' (tuple): Extra data for UI utility ( selectInfoTxt(str), classification(str), advicedAttr(set) )
    """
    if self is None:
        self = _Get_Instance( self_idx )
    
    # --- Variables ---
    WIN_NAME = f"{self.WIN_NAME}_AttrWindow"
    WIN_TITLE = f"Output attribute"

    # --- UI ---
    #Close old window at same name if exists
    if cmds.window( WIN_NAME, exists=True ):
        cmds.deleteUI( WIN_NAME, window=True )
    if not self.THEME['crt']['attrwin_keep_pref'] and cmds.windowPref( WIN_NAME, exists=True ):
        cmds.windowPref( WIN_NAME, remove=True )
    
    #Create new window
    cmds.window(
        WIN_NAME,
        title=WIN_TITLE,
        widthHeight=self.THEME['crt']['attrwin_size_wh'],
        sizeable=True,
        backgroundColor=self.THEME['main_back']
    )

    main_formLyt = cmds.formLayout()
    info_txtLyt = cmds.columnLayout(
        height=40,
        adjustableColumn=True,
        parent=main_formLyt
    )
    cmds.text( height=20, label=f"<font size=4><font color={self.THEME['crt']['attrwin_txt_main']}>Select {ui_data[0]}</font>", align='center', parent=info_txtLyt )
    cmds.text( height=20, label=f"<font size=4><font color={self.THEME['crt']['attrwin_txt_main']}>for '<font color={self.THEME['crt']['attrwin_txt_high']}>{node}<font color={self.THEME['crt']['attrwin_txt_main']}>'</font>", align='center', parent=info_txtLyt )
    scrollLyt = cmds.scrollLayout(
        height=1,
        childResizable=True, verticalScrollBarAlwaysVisible=True,
        backgroundColor=self.THEME['crt']['crt_clmn_back'],
        parent=main_formLyt
    )
    self.attrwin = WIN_NAME
    #Build attribute button
    if len(attr_list) == 0:
        cmds.separator( height=10, style='none', parent=scrollLyt )
        cmds.text( height=25, label=f"<font size=4><font color={self.THEME['crt']['attrwin_txt_empty']}>No attribute found matching type or classification</font>", align='center', parent=scrollLyt )
        cmds.text( height=25, label=f"<font size=4><font color={self.THEME['crt']['attrwin_txt_empty']}>'{ui_data[1]}'</font>", align='center', parent=scrollLyt )
    else:
        has_advice = True if len(ui_data) == 3 else False
        for attr in attr_list:
            cmds.separator( height=5, style='none', parent=scrollLyt )
            
            cmd_str = attr[1][2].replace('<node>', node).replace('<attr>', attr[0]).replace('<winname>', WIN_NAME)
            bttn_cmd = partial( attr[1][0], attr[1][1], cmd_str, *attr[1][3:] ) #Function, self_idx, cmd_str, *args
            if cmds.getAttr( f'{node}.{attr[0]}', lock=True ): #Locked
                cmds.button( height=25, label=attr[0], command=bttn_cmd, annotation="Locked attribute", statusBarMessage="Locked attribute", backgroundColor=self.THEME['crt']['attrwin_bttnLocked_back'], parent=scrollLyt )
            else:
                if has_advice:
                    if attr[0] in ui_data[2]:
                        cmds.button( height=25, label=attr[0], command=bttn_cmd, backgroundColor=self.THEME['crt']['attrwin_bttnHigh_back'], annotation="Default attribute advice", statusBarMessage="Default attribute advice", parent=scrollLyt )
                    else:
                        cmds.button( height=25, label=attr[0], command=bttn_cmd, backgroundColor=self.THEME['crt']['attrwin_bttn_back'], parent=scrollLyt )
                else:
                    cmds.button( height=25, label=attr[0], command=bttn_cmd, backgroundColor=self.THEME['crt']['attrwin_bttn_back'], parent=scrollLyt )
    
    cmds.formLayout(
        main_formLyt, edit=True,
        attachForm=(
            (info_txtLyt, 'top', 0), (info_txtLyt, 'left', 5), (info_txtLyt, 'right', 5),
            (scrollLyt, 'top', 40), (scrollLyt, 'left', 5), (scrollLyt, 'right', 5), (scrollLyt, 'bottom', 5)
        )
    )
    cmds.showWindow()

def _Build_PopupUI( parent:str, items:tuple, return_pop=False ): #Build popup UI (right-click menu)
    """
    Build popup UI (right-click menu)\n
    ### Parameters:\n
    'parent' (str): Parent's path\n
    'items' (tuple): List of UI items names\n
      Note: Start item with 'div' to set as divider item\n
    'return_pop' (bool): If True, return popupMenu path\n
    """
    pop = cmds.popupMenu(
        button=3,
        parent=parent
    )
    for item in items:
        if item[0].startswith('div'): #Is divider item
            long = True if len(item) > 1 and item[1] else False
            cmds.menuItem(
                divider=True, dividerLabel=item[0][4:], longDivider=long,
                parent=pop
            )
        else: #Is button item
            cmds.menuItem(
                label=item[0],
                command=item[1],
                parent=pop
            )
    if return_pop:
        return pop

def _Build_RadioBttnLine( parent:str, line_label, dimensions:tuple, options:list, default_option:int, return_lyt=False, extra_lyt_columns=0 ): #Create a custom line of radio button(s) and return the radio collection
    """
    Create a custom line of radio button(s) and return the radio collection\n
    ### Parameters:\n
    'parent' (str): Parent layout name\n
    'line_label' (str/tuple): Label for the line, if tuple ( label(str), annotation(str), statusBarMessage(str) )\n
    'dimensions' (tuple): ( rowHeight(int), lineOffset(int), optionsMargin(int) buttonLabelMargin(int), interOptionMargin(int) )\n
    'options' (list): Option item -> [optionName, onCommand]\n
    'default_option' (int): Default option selected\n
    'return_lyt' (bool): Also return the main line rowLayout\n
    'extra_lyt_columns' (int): Extra columns space on the main line rowLayout\n
    ### Return:\n
    'rad_coll' or 'radcoll', 'rowLyt'
    """
    rowLyt = cmds.rowLayout( #Line layout
        height=dimensions[0],
        numberOfColumns=(len(options)*4) +2 +extra_lyt_columns,
        parent=parent
    )
    if dimensions[1] != 0:
        cmds.separator( height=dimensions[0], width=dimensions[1], style='none', parent=rowLyt )
    if type(line_label) == str:
        cmds.text( #Line label
            height=dimensions[0],
            label=line_label,
            parent=rowLyt
        )
    else:
        cmds.text( #Line label
            height=dimensions[0],
            label=line_label[0], annotation=line_label[1], statusBarMessage=line_label[2],
            parent=rowLyt
        )
    
    cmds.separator( height=dimensions[0], width=dimensions[2], style='none', parent=rowLyt )
    rad_coll = cmds.radioCollection( parent=rowLyt )
    rad_coll_items = []
    options_len = len(options)
    
    i = 0
    last_idx = options_len-1
    while i < options_len:
        i_radBttn = cmds.radioButton( #Button
            height=dimensions[0], width=14,
            label='', collection=rad_coll, select=True if i == default_option else False,
            onCommand=options[i][1],
            parent=rowLyt
        )
        rad_coll_items.append( i_radBttn )
        cmds.separator( height=dimensions[0], width=dimensions[3], style='none', parent=rowLyt )
        cmds.text( #Option label
            height=dimensions[0],
            label=options[i][0],
            parent=rowLyt
        )
        if i != last_idx: #Between options separator
            cmds.separator( height=dimensions[0], width=dimensions[4], style='none', parent=rowLyt )
        i+=1
    
    if return_lyt:
        return rad_coll, rowLyt
    return rad_coll

def _Build_IntField( parent:str, height:int, field:tuple, sep_width:int, bttns:tuple, background_color:list ): #Create an intField with up and down arrow buttons
    """
    Create an intField with up and down arrow buttons\n
    ### Parameters:\n
    'parent' (str): Parent layout name\n
    'height' (int): Height for both elements\n
    'field' (tuple): ( width(int), editable(bool), change_command(str), value(int), min_value(None/int), max_value(None/int), annotation(str), statusBarMessage(str) )\n
    'sep_width' (None/int): If not None, create separator too at said width\n
    'bttns' (tuple): ( size(int), top_offset(int), down_offset(int), command_up(str), command_down(str) )\n
    'background_color' (list): Maya UI backgroundColor\n
    ### Return:\n
    'intFieldCtrl'
    """
    intFieldCtrl = None
    if field[4] is None and field[5] is None: #No min max value
        intFieldCtrl = cmds.intField(
            height=height, width=field[0],
            editable=field[1], changeCommand=field[2], value=field[3],
            annotation=field[6], statusBarMessage=field[7],
            backgroundColor=background_color,
            parent=parent
        )
    elif field[5] is None: #min
        intFieldCtrl = cmds.intField(
            height=height, width=field[0],
            editable=field[1], changeCommand=field[2], value=field[3], minValue=field[4],
            annotation=field[6], statusBarMessage=field[7],
            backgroundColor=background_color,
            parent=parent
        )
    else: #min max
        intFieldCtrl = cmds.intField(
            height=height, width=field[0],
            editable=field[1], changeCommand=field[2], value=field[3], minValue=field[4], maxValue=field[5],
            annotation=field[6], statusBarMessage=field[7],
            backgroundColor=background_color,
            parent=parent
        )
    
    if sep_width is not None:
        cmds.separator( height=height, width=sep_width, style='none', parent=parent )
    
    bttns_clmnLyt = cmds.rowColumnLayout(
        height=height+bttns[1], width=bttns[0]+2,
        numberOfRows=2, rowAttach=( (1, 'top', 0), (2, 'top', bttns[2]*2) ),
        parent=parent
    )
    cmds.symbolButton(
        height=bttns[0], width=bttns[0],
        image='moveUVUp.png', command=bttns[3],
        backgroundColor=background_color,
        parent=bttns_clmnLyt
    )
    cmds.symbolButton(
        height=bttns[0], width=bttns[0],
        image='moveUVDown.png', command=bttns[4],
        backgroundColor=background_color,
        parent=bttns_clmnLyt
    )
    return intFieldCtrl
#endregion - * General *

#region - * UI/Features *
def _Select_Callback( self_idx, select_idx:int,    drgCllBck_drgCtrl=None, drgCllBck_x=None, drgCllBck_y=None, drgCllBck_mod=None ): #Select node/object from data
    """
    Select node/object from data\n
    ### Parameters:\n
    'select_idx' (int): Data idx ( CREATE 0:uvPin, 1:geo, 2:geo_orig, 3:geo_defo, 4:match_other, 5:mirror_space | DISPLAY 10:uvPin )\n
    'drgCllbck...': parameters required when using a function object in a Maya UI dragCallback argument
    """
    self = _Get_Instance( self_idx )
    node = None
    if select_idx == 0:
        node = self.ui_data[0]['uvpin']
    if select_idx == 1:
        node = self.ui_data[0]['geo']
    if select_idx == 2:
        node = self.ui_data[0]['geo_orig']
        if node is not None:
            node = _Split_NodeAttr( node )
    if select_idx == 3:
        node = self.ui_data[0]['geo_defo']
        if node is not None:
            node = _Split_NodeAttr( node )
    if select_idx == 4:
        node = self.ui_data[0]['match_extra']
        if node is not None:
            node = _Split_NodeAttr( node )
    if select_idx == 5:
        node = self.ui_data[0]['mirror_space']
        if node is not None:
            node = _Split_NodeAttr( node )
    if select_idx == 10:
        node = self.ui_data[1]['uvpin']
    
    if node is not None and node != 'None':
        if cmds.objExists( node ):
            cmds.select( node, replace=True )
        else:
            cmds.warning( f"[ISSUE]: '{node}' not found!", noContext=True )
    cmds.setFocus( '' ) #Remove focus from window

def _Tab_Change( self_idx:int, partial_empty=None ): #Apply changes specific to tabs
    """ Apply changes specific to tabs """
    self = _Get_Instance( self_idx )

    #c_tab = cmds.tabLayout( self.ui_items[2], query=True, selectTabIndex=True )
    cmds.setFocus('')
    _Pick_Cancel( self, self_idx )
#endregion - * UI/Features *

#region - ** Tab Create **
# uvPin
def _Pick_UVPIN_Done_CRT( self_idx, skip_check=False ): #End function for uvPin pick
    """ End function for uvPin pick """
    self_idx = int(self_idx)
    self = _Get_Instance( self_idx )
    if self.callback_hook is not None: #Prevent function called twice
        self.callback_hook = None
    else:
        return
    
    if skip_check or (self.pick_sel != [] and self.pick_sel != None):
        _Set_UVPIN( self, self_idx, True, self.pick_sel[-1] )
    self.pick_sel = None
    self.pick_selData = None
    self.pick_ui = None

def _Set_UVPIN( self, self_idx:int, pick=False, node_name=None, from_reload=False, partial_empty=None ): #Set uvPin value from textField and picker
    """
    Set uvPin's value\n
    ### Parameters:\n
    'pick' (bool): If True skip rechecking for node existing and update textField once done\n
    'node_name' (None/str): Selection picked node if 'pick' is True, else getting it from the textField's text\n
    'from_reload' (bool): If True, skip relevant confirmation windows if values didn't change\n
    'partial_empty' (bool): Extra 'False' argument from partial() when function call includes argument(s)
    """
    if self is None:
        self = _Get_Instance( self_idx )
    
    txtField = self.ui_items[0]['uvp_picker_txtField']
    is_new = False
    if not pick: #If not pick, get node name from textField and check it
        node_name = cmds.textField( txtField, query=True, text=True )

        if node_name == '':
            _Set_UVPIN_Revert(self)
            return
        elif node_name == "None":
            _Set_UVPIN_Revert(self)
            cmds.error( f"[ISSUE]: 'None' can't be set as a uvPin name!", noContext=True )
        if node_name is not None:
            if not cmds.objExists( node_name ): #If doesn't exist, guess as new
                is_new = True
            elif cmds.nodeType( node_name ) != 'uvPin': #Else, check if is right type uvPin
                cmds.error( f"[ISSUE]: '{node_name}' exists but isn't an uvPin node!", noContext=True )
        else:
            _Set_UVPIN_Revert(self)
            return
    
    #Store value and update UI
    self.ui_data[0]['uvpin'] = node_name
    if pick:
        cmds.textField( txtField, edit=True, text=node_name )
    #Update UI if changed
    _Update_UVPIN_State( self, is_new )
    
    #If not new, try to load data from it
    if not is_new:
        #Geometry
        geo_orig = cmds.connectionInfo( f'{node_name}.originalGeometry', sourceFromDestination=True )
        geo_defo = cmds.connectionInfo( f'{node_name}.deformedGeometry', sourceFromDestination=True )

        if not from_reload or (from_reload and (self.ui_data[0]['geo_orig'] != geo_orig or self.ui_data[0]['geo_defo'] != geo_defo)): #Only ask changes if not from reload or from reload and a value changed
            confirm_result = None
            geo_result = None
            geo_msg = None
            if geo_orig != '' and geo_defo != '': #If both attributes have a connection, ask user if they want to load them
                confirm_result = cmds.confirmDialog(
                    title="Selected uvPin",
                    message=f"Existing connections found on uvPin's\noriginal and deformed geometry\n\nLoad both ?",
                    button=["Yes","Original geo","Deformed geo","No"], defaultButton="No", cancelButton="No", dismissString="No"
                )
                if confirm_result == "Yes":
                    geo_result = ( (geo_orig,'original geometry',False,'geo_orig',0,'geoOrig_picker_txtField'), (geo_defo,'deformed geometry',True,'geo_defo',1,'geoDefo_picker_txtField') )
                    geo_msg = "Original and deformed geometries"
                elif confirm_result == "Original geo":
                    geo_result = ( (geo_orig,'original geometry',False,'geo_orig',0,'geoOrig_picker_txtField'), )
                    confirm_result = "Yes"
                    geo_msg = "Original geometry"
                elif confirm_result == "Deformed geo":
                    geo_result = ( (geo_defo,'deformed geometry',True,'geo_defo',1,'geoDefo_picker_txtField'), )
                    confirm_result = "Yes"
                    geo_msg = "Deformed geometry"
            elif geo_orig != '' or geo_defo != '': #If one attribute has a connection, ask user if they want to load it
                geo_result = ( (geo_orig,'original geometry',False,'geo_orig',0,'geoOrig_picker_txtField'), ) if geo_defo == '' else ( (geo_defo,'deformed geometry',True,'geo_defo',1,'geoDefo_picker_txtField'), )
                # (connection(str), txt info(str), get_type(bool), geo_idx(int), ui_items(str))
                confirm_result = cmds.confirmDialog(
                    title="Selected uvPin",
                    message=f"Existing connection found on uvPin's\n{geo_result[0][1]}, load it ?",
                    button=["Yes","No"], defaultButton="No", cancelButton="No", dismissString="No"
                )
            if confirm_result == "Yes":
                name_set = False
                for geo in geo_result:
                    #Get type
                    if geo[2]: #If should get geometry type from that geometry, load it
                        geo_type = cmds.nodeType( _Split_NodeAttr(geo_defo) )
                        
                        if geo_type != 'mesh' and geo_type != 'nurbsSurface': #If unknown type, ask user what to do
                            confirm_result = cmds.confirmDialog(
                                title="Unknown geo type",
                                message="Couldn't find the type of deformed geometry\nPlease precise one for Match 'Closest to' and Mirror",
                                button=["Mesh","Surface","Skip"], defaultButton="Skip", cancelButton="Skip", dismissString="Skip"
                            )
                            if confirm_result == "Mesh":
                                _Set_Geo_Type( self_idx, True, 'mesh' )
                            elif confirm_result == "Surface":
                                _Set_Geo_Type( self_idx, True, 'nurbsSurface' )
                        else: #Type matches mesh or nurbsSurface, store it
                            _Set_Geo_Type( self_idx, True, geo_type )
                    
                    #Store data and update UI
                    self.ui_data[0][geo[3]] = geo[0]
                    _Update_GeoField(( ( geo[4], self.ui_items[0][geo[5]], geo[0] ), ))
                    if not name_set:
                        geo_name = _Split_NodeAttr( geo[0] ) #Get geo node without attr
                        if geo_name is not None:
                            geo_name = cmds.listRelatives( geo_name, parent=True, noIntermediate=True, type='transform' ) #Get parent above geo node, if it is shape it should return the object transform
                        if geo_name is not None:
                            geo_name = geo_name[0]
                            self.ui_data[0]['geo'] = geo_name
                            # UI
                            cmds.textField( self.ui_items[0]['geo_picker_txtField'], edit=True, text=geo_name )
                            name_set = True
                cmds.inViewMessage( message=f"<font color={self.THEME['done_txt']}>{geo_msg} loaded from uvPin!</font color>", position="botCenter", fade=True, fadeOutTime=300 )
                print( f"[INFO]: {geo_msg} loaded from uvPin!" )
        
        #Start index
        _Update_Start_Idx( self_idx, node_name )
    else: #If new, set back start index to 0
        _Set_Start_Idx( self_idx, None, True, 0 )

def _Set_UVPIN_Revert( self ): #Revert uvPin textField to data value
    """ Revert uvPin textField to data value """
    old_value = self.ui_data[0]['uvpin']
    if old_value is None:
        old_value = 'None'
    cmds.textField( self.ui_items[0]['uvp_picker_txtField'], edit=True, text=old_value )

def _Update_UVPIN_State( self, new_state:bool ): #Update uvPin state text if changed
    """ Update uvPin state text if changed """
    if new_state and not self.ui_data[0]['uvpin_new']:
        cmds.text(
            self.ui_items[0]['uvpin_state_txtCtrl'], edit=True,
            label=f"<font size=6>( <font color={self.THEME['crt']['uvpTxt_new']}>New</font color> )</font>",
            annotation="No uvPin node found at this name,\nthe uvPin will be created too",
            statusBarMessage="No uvPin node found at this name, the uvPin will be created too"
        )
        self.ui_data[0]['uvpin_new'] = True
    elif not new_state and self.ui_data[0]['uvpin_new']:
        cmds.text(
            self.ui_items[0]['uvpin_state_txtCtrl'], edit=True,
            label="<font size=6>( <font color=orange>Existing</font color> )</font>",
            annotation="An uvPin node found at this name,\nchanges will be applied on it",
            statusBarMessage="An uvPin node found at this name, changes will be applied on it",
        )
        self.ui_data[0]['uvpin_new'] = False

def _Reload_UVPin( self_idx:int, partial_empty=None ): #Reload current uvPin to update changes or undo
    """ Reload current uvPin to update changes or undo. If uvPin doesn't exist update state text """
    self = _Get_Instance( self_idx )
    if self.ui_data[0]['uvpin'] is None:
        return
    if cmds.objExists( self.ui_data[0]['uvpin'] ):
        _Set_UVPIN( self, self_idx, True, self.ui_data[0]['uvpin'], True )
    else:
        _Update_UVPIN_State( self, True )
        _Set_Start_Idx( self_idx, None, True, 0 )

# Geometry
def _Build_GeoExtraLyt( self, self_idx:int, state:bool, partial_empty=None ): #Build extra geometry UI
    """ Build extra geometry UI """
    if self is None:
        self = _Get_Instance( self_idx )
    
    if state: #Add UI
        geo_extra_rowLyt = cmds.rowLayout(
            height=30,
            numberOfColumns=14,
            parent=self.ui_items[0]['geo_rowLyt']
        )
        self.ui_items[0]['geo_extraLyt'] = geo_extra_rowLyt
        cmds.text( height=30, label='<font color=silver>ORIG</font>', parent=geo_extra_rowLyt )
        cmds.separator( height=30, width=1, style='none', parent=geo_extra_rowLyt )
        self.ui_items[0]['geoOrig_picker_txtField'], self.ui_items[0]['geoOrig_picker_symbBttn'] = _Build_PickerBttn( #Picker
            geo_extra_rowLyt, 30,
            (
                115, self.ui_data[0]['geo_orig'], True, partial(_Set_Geo, self_idx, 1, False, None),
                "uvPin original geometry:\n\nNone\n\n(Will require a geometry output attribute)\n[Middle mouse]: Select node",
                "uvPin original geometry:  None    (Will require a geometry output attribute)  [Middle mouse]: Select node",
                self.THEME['crt']['main_option_back'], partial(_Select_Callback, self_idx, 2)
            ),
            1,
            (
                partial(_Pick_Init, self_idx, 1, _Pick_Geo_Done, 10, None, True, False, True),
                "Pick tool for uvPin original geometry's node\n\n(Will require a geometry output attribute)",
                "Pick tool for uvPin original geometry's node (Will require a geometry output attribute)",
                self.THEME['crt']['pick_back_off'], (25,25)
            )
        )
        cmds.separator( height=30, width=5, style='none', parent=geo_extra_rowLyt )
        
        cmds.text( height=30, label='<font color=silver>DEFO</font>', parent=geo_extra_rowLyt )
        cmds.separator( height=30, width=1, style='none', parent=geo_extra_rowLyt )
        self.ui_items[0]['geoDefo_picker_txtField'], self.ui_items[0]['geoDefo_picker_symbBttn'] = _Build_PickerBttn( #Picker
            geo_extra_rowLyt, 30,
            (
                115, self.ui_data[0]['geo_defo'], True,
                partial(_Set_Geo, self_idx, 2, False, None),
                "uvPin deformed geometry:\n\nNone\n\n(Will require a geometry output attribute)\n[Middle mouse]: Select node",
                "uvPin deformed geometry:  None    (Will require a geometry output attribute)  [Middle mouse]: Select node",
                self.THEME['crt']['main_option_back'],
                partial(_Select_Callback, self_idx, 3)
            ),
            1,
            (
                partial(_Pick_Init, self_idx, 1, _Pick_Geo_Done, 11, None, True, False, True),
                "Pick tool for uvPin deformed geometry's node\n\n(Will require a geometry output attribute)",
                "Pick tool for uvPin deformed geometry's node (Will require a geometry output attribute)",
                self.THEME['crt']['pick_back_off'], (25,25)
            )
        )
        cmds.separator( height=30, width=4, style='none', parent=geo_extra_rowLyt )
        
        geo_type_opMenu = cmds.optionMenu(
            height=30, width=78,
            maxVisibleItems=3, changeCommand=partial(_Set_Geo_Type, self_idx, False, None),
            annotation="Type of geometry\nRequired for 'Match closest to' and Mirror", statusBarMessage="Type of geometry, required for 'Match closest to' and Mirror",
            backgroundColor=self.THEME['crt']['main_option_back'],
            parent=geo_extra_rowLyt
        )
        self.ui_items[0]['geo_type_opMenu'] = geo_type_opMenu
        cmds.menuItem( label="None", annotation="No geometry type", parent=geo_type_opMenu )
        cmds.menuItem( label="Mesh", annotation="Polygon mesh geometry type", parent=geo_type_opMenu )
        cmds.menuItem( label="Surface", annotation="Surface/nurbsSurface geometry type", parent=geo_type_opMenu )
        cmds.separator( height=30, width=10, style='none', parent=geo_extra_rowLyt )
        if self.ui_data[0]['geo_type'] == 'mesh':
            cmds.optionMenu( geo_type_opMenu, edit=True, value='Mesh' )
        elif self.ui_data[0]['geo_type'] == 'nurbsSurface':
            cmds.optionMenu( geo_type_opMenu, edit=True, value='Surface' )
    else: #Remove UI
        cmds.deleteUI( self.ui_items[0]['geo_extraLyt'], layout=True )
        self.ui_items[0]['geoOrig_picker_txtField'] = None
        self.ui_items[0]['geoDefo_picker_txtField'] = None
        self.ui_items[0]['geo_type_opMenu'] = None

def _Pick_Geo_Done( self_idx, skip_check=False ): #End function for geometry pick
    """ End function for geometry pick """
    self_idx = int(self_idx)
    self = _Get_Instance( self_idx )
    if self.callback_hook is not None: #Prevent function called twice
        self.callback_hook = None
    else:
        return
    
    if skip_check or (self.pick_sel != [] and self.pick_sel is not None):
        _Set_Geo( self_idx, self.pick_selData, True, self.pick_sel[-1] )
    self.pick_sel = None
    self.pick_selData = None
    self.pick_ui = None

def _Set_Geo( self_idx:int, geo_idx:int, pick=False, node_name=None, partial_empty=None ): #Set geometry value from textField and picker
    """ Set geometry value from textField and picker """
    self = _Get_Instance( self_idx )

    txtField = None
    data_name = None
    
    if geo_idx == 0:
        txtField = self.ui_items[0]['geo_picker_txtField']
        data_name = 'geo'
        
        if not pick:
            node_name = cmds.textField( txtField, query=True, text=True )
        t_node_name = node_name
        node_name = _Split_NodeAttr( node_name ) #Check node exists and remove eventual attribute
        if node_name is None: #Revert to old value
            old_value = self.ui_data[0][data_name]
            if old_value is None:
                old_value = 'None'
            #_Update_GeoField( [ (geo_idx, txtField, old_value) ] )
            cmds.textField( self.ui_items[0]['geo_picker_txtField'], edit=True, text=old_value )
            cmds.error( f"[ISSUE]: Node '{t_node_name}' not found!", noContext=True )
        t_node_name = None

        #Global geometry
        #If mesh, get transform and run below
        #If transform, get orig and deformed mesh or surface
        inherited_types = cmds.objectType( node_name ) #cmds.nodeType( node_name, inherited=True )
        type_found = None
        if 'transform' in inherited_types: #transform
            type_found = 'transform'
        elif 'mesh' in inherited_types: #mesh
            type_found = 'mesh'
        elif 'nurbsSurface' in inherited_types: #surface
            type_found = 'nurbsSurface'
        else:
            cmds.error( f"[ISSUE]: Selection doesn't match required types!", noContext=True )
        
        #Type matching
        shape_orig_node = None
        shape_orig = None
        shape_defo = None
        orig_attr_found = False
        defo_attr_found = False

        if type_found != 'transform': #Find parent transform and set it as node_name to get full plug chain
            shape_trnsf = cmds.listRelatives( node_name, parent=True, noIntermediate=True, type='transform' )
            if shape_trnsf is None:
                cmds.error( f"[ISSUE]: Couldn't find parent transform above '{node_name}'", noContext=True )
            node_name = shape_trnsf[0]
        #Update UI
        self.ui_data[0]['geo'] = node_name
        cmds.textField( self.ui_items[0]['geo_picker_txtField'], edit=True, text=node_name )
        
        #Get chain
        node_chain = cmds.deformableShape( node_name, plugChain=True )
        if node_chain is None:
            cmds.error( f"[ISSUE]: Selected object doesn't seem to have mesh or nurbsSurface shape under it's transform", noContext=True )
        node_chain_len = len(node_chain)
        types = {'mesh','nurbsSurface'}
        geo_type = None

        if node_chain_len == 1: #No deformer (including cases with deformers sending geometry into the only shape)
            shape_orig_node = _Split_NodeAttr( node_chain[0] )
            geo_type = cmds.nodeType( shape_orig_node )
            
            shape_orig_attr = 'worldMesh[0]' if geo_type == 'mesh' else 'worldSpace[0]'
            shape_orig_attr_query = 'worldMesh' if geo_type == 'mesh' else 'worldSpace'
            if cmds.attributeQuery( shape_orig_attr_query, node=shape_orig_node, exists=True ):
                shape_orig = f'{shape_orig_node}.{shape_orig_attr}'
                orig_attr_found = True
            else: #Attribute not found
                shape_orig = shape_orig_node
            
            shape_defo_attr = 'outMesh' if geo_type == 'mesh' else 'local'
            if cmds.attributeQuery( shape_defo_attr, node=shape_orig_node, exists=True ):
                shape_defo = f'{shape_orig_node}.{shape_defo_attr}'
                defo_attr_found = True
            else: #Attribute not found
                shape_defo = shape_orig_node
        else: #Check both sides of the chain for the right nodes
            #Start of chain
            i = 0
            shape_orig_idx = 0
            while i < node_chain_len:
                node = node_chain[i]
                node_type = cmds.nodeType( node )
                if node_type in types:
                    geo_type = node_type
                    shape_orig_node = _Split_NodeAttr( node )
                    
                    shape_orig_attr = 'worldMesh[0]' if geo_type == 'mesh' else 'worldSpace[0]'
                    shape_orig_attr_query = 'worldMesh' if geo_type == 'mesh' else 'worldSpace'
                    if cmds.attributeQuery( shape_orig_attr_query, node=shape_orig_node, exists=True ):
                        shape_orig = f'{shape_orig_node}.{shape_orig_attr}'
                        orig_attr_found = True
                    else:
                        shape_orig = shape_orig_node
                    shape_orig_idx = i
                    break
                i+=1
            #Clear from the list nodes before the first shape
            if shape_orig_idx != 0:
                del node_chain[:i]
                node_chain_len = len(node_chain)
            
            #End of chain
            if node_chain_len == 1: #There is actually only one shape
                shape_defo_attr = 'outMesh' if geo_type == 'mesh' else 'local'
                if cmds.attributeQuery( shape_defo_attr, node=shape_orig_node, exists=True ):
                    shape_defo = f'{shape_orig_node}.{shape_defo_attr}'
                    defo_attr_found = True
                else:
                    shape_defo = shape_orig_node
            else:
                i = node_chain_len -1
                while i > 0:
                    node = node_chain[i]
                    node_type = cmds.nodeType( node )
                    if node_type in types and cmds.getAttr( f'{node.rsplit(".",1)[0]}.intermediateObject' ) == 0: #End of chain shape, supposing it's not an intermediateObject
                        if i == 1:
                            cmds.warning( f"[ISSUE]: Detected node prior end-of-chain shape seems to be start-of-chain shape, please them in their original and deformed geometry fields", noContext=True )
                        shape_defo = node_chain[i-1]
                        if _Split_NodeAttr( shape_defo, False, True ): #Check if found end of chain contains an attribute
                            defo_attr_found = True
                        break
                    i-=1
        
        #Store values
        self.ui_data[0]['geo_orig'] = shape_orig
        self.ui_data[0]['geo_defo'] = shape_defo

        #Update UI(s)
        _Set_Geo_Type( self_idx, True, geo_type )
        orig_ui = self.ui_items[0]['geoOrig_picker_txtField']
        if orig_ui is not None:
            _Update_GeoField([
                ( 0, orig_ui, shape_orig ),
                ( 1, self.ui_items[0]['geoDefo_picker_txtField'], shape_defo )
            ])
        
        #If attribute(s) not found
        if not orig_attr_found and not defo_attr_found:
            cmds.warning( f"[ISSUE]: Output geometry attribute not found on original geometry '{shape_orig}' and deformed geometry '{shape_defo}'!", noContext=True )
        elif not orig_attr_found:
            cmds.warning( f"[ISSUE]: Output geometry attribute not found on original geometry '{shape_orig}'!", noContext=True )
        elif not defo_attr_found:
            cmds.warning( f"[ISSUE]: Output geometry attribute not found on deformed geometry '{shape_defo}'!", noContext=True )
    else:
        if geo_idx == 1:
            txtField = self.ui_items[0]['geoOrig_picker_txtField']
            data_name = 'geo_orig'
        if geo_idx == 2:
            txtField = self.ui_items[0]['geoDefo_picker_txtField']
            data_name = 'geo_defo'
        
        has_attr = False
        if not pick: #If called from textField and not global geometry (which already does that earlier)
            node_name = cmds.textField( txtField, query=True, text=True )

            if '.' in node_name: #May have an attribute
                node_name = _Split_NodeAttr( node_name, True )

                if geo_idx == 0 and type(node_name) == list: #Remove attr from global geometry node name
                    node_name = node_name[0]
                
                if type(node_name) == list: #Node and attribute found
                    self.ui_data[0][data_name] = f'{node_name[0]}.{node_name[1]}'
                    _Update_GeoField( [ (geo_idx, txtField, f'{node_name[0]}.{node_name[1]}') ] )
                    has_attr = True
                elif node_name is not None: #Node found
                    self.ui_data[0][data_name] = node_name
                    _Update_GeoField( [ (geo_idx, txtField, node_name) ] )
            elif not cmds.objExists( node_name ): #No attribute and node doesn't exist
                node_name = None
            
            if node_name is None: #Revert to old value
                old_value = self.ui_data[0][data_name]
                if old_value is None:
                    old_value = 'None'
                _Update_GeoField( [ (geo_idx, txtField, old_value) ] )
                cmds.error( f"[ISSUE]: Node '{node_name}' not found!", noContext=True )
        else: #If called from picker
            self.ui_data[0][data_name] = node_name
            _Update_GeoField( [ (geo_idx, txtField, node_name) ] )
        
        if not has_attr: #If not global geometry and has no attr/existing attr
            #Get all matching attributes
            attr_list = cmds.listAttr( node_name )
            attr_list_fixed = []
            attr_to_skip = {'controlPoints','pnt','pnts','vrts','edge','uvpt','face','weightList','envelopeWeightsList','perInfluenceWeights','bindPreMatrix','lockWeights'}
            for attr in attr_list:
                if attr in attr_to_skip: #Skip known useless multi attributes to prevent useless massive indexes to check
                    continue
                if not cmds.attributeQuery( attr, node=node_name, exists=True ): #Skip some unusable multi children attributes
                    continue
                try: #Skip if attribute doesn't exist on node_name
                    cmds.getAttr( f'{node_name}.{attr}', type=True )
                except ValueError:
                    continue
                except RuntimeError:
                    continue
                except Exception as exception_info:
                    cmds.warning( f"Unexpected exception while trying to read attr '{node_name}.{attr}' (Exception '{exception_info}', type {type(exception_info)})", noContext=True )
                
                t_attr_list = []
                if cmds.attributeQuery( attr, node=node_name, multi=True ): #If multi, add to the list every indexes too
                    attr_size = cmds.getAttr( f'{node_name}.{attr}', size=True )
                    if attr_size != -1: #Is multi
                        i = 0
                        while i < attr_size:
                            t_attr_list.append( f'{attr}[{i}]' )
                            i+=1
                    else:
                        t_attr_list.append( attr )
                else: #Else add as it is
                    t_attr_list.append( attr )
                for c_attr in t_attr_list:
                    if not _Get_TypeMatchGeo( None, f'{node_name}.{c_attr}' ): #Skip attributes not matching geometry type or Maya classification
                        continue
                    attr_list_fixed.append( c_attr )
            attr_list = []
            attr_list_fixed.sort() #Sort result attributes as alphabetical order may be quicker to read

            #Build attr list
            i = 0
            attr_list_fixed_len = len(attr_list_fixed)
            while i < attr_list_fixed_len:
                attr_list_fixed[i] = ( attr_list_fixed[i], (_AttrWin_GeoBttn, self_idx, '<node>.<attr>', geo_idx) )
                i+=1
            
            attr_advice = {'worldMesh[0]','worldSpace[0]','outputGeometry[0]'} if geo_idx == 1 else {'outMesh','local','outputGeometry[0]'}
            _Build_AttrWindow( self, self_idx, node_name, attr_list_fixed, ("geometry output attribute","geometry",attr_advice) )

def _AttrWin_GeoBttn( self_idx:int, value:str, geo_idx:int, partial_empty=None ): #Called by button on attr window to change original/deformed geometry attribute
    """ Called by button on attr window to change original/deformed geometry attribute """
    self = _Get_Instance( self_idx )

    txtField = None
    if geo_idx == 1: #Original geometry
        self.ui_data[0]['geo_orig'] = value
        txtField = self.ui_items[0]['geoOrig_picker_txtField']
        geo_idx = 0
    elif geo_idx == 2: #Deformed geometry
        self.ui_data[0]['geo_defo'] = value
        txtField = self.ui_items[0]['geoDefo_picker_txtField']
        geo_idx = 1
    
    if txtField is not None:
        _Update_GeoField( [ (geo_idx, txtField, value) ] )
    cmds.evalDeferred( f"cmds.deleteUI( '{self.attrwin}', window=True )" )
    self.attrwin = None

def _Update_GeoField( field_data:list ): #Update original and/or deformed geometry field(s)
    """
    Update original and/or deformed geometry field(s)\n
    ### Parameters:\n
    'fieldData' (list): [ ( field_idx(int)[0: orig; 1:deformed], field_ui_path(str), text(str) ), ... ]
    """
    for c_data in field_data:
        if c_data[1] is not None and cmds.textField( c_data[1], query=True, exists=True ):
            info_anno = f"uvPin original geometry:\n\n{c_data[2]}\n\n(Will require a matrix output attribute)\n[Middle mouse]: Select node" if c_data[0] == 0 else f"uvPin deformed geometry:\n\n{c_data[2]}\n\n(Will require a matrix output attribute)\n[Middle mouse]: Select node"
            info_status = f"uvPin original geometry:  {c_data[2]}    (Will require a matrix output attribute)  [Middle mouse]: Select node" if c_data[0] == 0 else f"uvPin deformed geometry:  {c_data[2]}    (Will require a matrix output attribute)  [Middle mouse]: Select node"

            cmds.textField( c_data[1], edit=True, text=c_data[2], annotation=info_anno, statusBarMessage=info_status )

def _Set_Geo_Type( self_idx:int, from_obj=False, value=None, partial_empty=None ): #Set geometry type value from dropdown
    """ Set geometry type value from dropdown """
    self = _Get_Instance( self_idx )
    
    if self.ui_items[0]['geo_type_opMenu'] is not None:
        if from_obj:
            #Update UI
            ui_value = None
            if value == 'mesh':
                ui_value = 'Mesh'
            elif value == 'nurbsSurface':
                ui_value = 'Surface'
            else:
                ui_value = 'None'
            if ui_value is not None:
                cmds.optionMenu( self.ui_items[0]['geo_type_opMenu'], edit=True, value=ui_value )
        else:
            #Get value from UI
            value = cmds.optionMenu( self.ui_items[0]['geo_type_opMenu'], query=True, value=True )
            if value == 'Mesh':
                value = 'mesh'
            elif value == 'Surface':
                value = 'nurbsSurface'
            else:
                value = None
    #Update data
    self.ui_data[0]['geo_type'] = value

# Object
def _Set_Obj( self_idx:int, partial_empty=None ): #Set obj value from dropdown UI
    """ Set obj value from dropdown UI """
    self = _Get_Instance( self_idx )
    
    old_option_idx = self.ui_data[0]['obj']
    option_idx = cmds.optionMenu( self.ui_items[0]['obj_type_opMenu'], query=True, select=True )
    
    self.ui_data[0]['obj'] = option_idx
    
    _Update_ObjOff( self, self_idx )
    _Update_MatchSel( self, self_idx )

def _Set_ObjOff( self_idx:int, drpdwn_idx:int, partial_empty=None ): #Set obj_off value from dropdown UI
    """
    Set obj_off value from dropdown UI\n
    ### Parameters:\n
    'drpwn_idx' (int): Dropdown index ( 0:Offset transforms, 1:Offset type, 2:Offset reference )\n
        Offset transforms: Set self.ui_data[0]['obj_off'] as None if no offset else bools in format (Translate, Rotate, Scale)\n
    'partial_empty' (bool): Extra 'False' argument from partial() when function call includes argument(s)
    """
    self = _Get_Instance( self_idx )
    
    if drpdwn_idx == 0: #Transforms to offset
        value = cmds.optionMenu( self.ui_items[0]['obj_off_opMenu'], query=True, select=True ) #1:None, 2:Translate, 3:Rotate, 4:Scale, 5:Both
        #Get new obj_off value from value and previous obj_off value
        if value == 1: # None
            self.ui_data[0]['obj_off'] = (False, False, False)
        elif value == 5: # Both
            self.ui_data[0]['obj_off'] = (True, True, True)
        else:
            if value == 2: # Translate
                if self.ui_data[0]['obj_off'] is None:
                    self.ui_data[0]['obj_off'] = (True, False, False)
                else:
                    new_value = False if self.ui_data[0]['obj_off'][0] else True
                    self.ui_data[0]['obj_off'] = (new_value, self.ui_data[0]['obj_off'][1], self.ui_data[0]['obj_off'][2])
            elif value == 3: # Rotate
                if self.ui_data[0]['obj_off'] is None:
                    self.ui_data[0]['obj_off'] = (False, True, False)
                else:
                    new_value = False if self.ui_data[0]['obj_off'][1] else True
                    self.ui_data[0]['obj_off'] = (self.ui_data[0]['obj_off'][0], new_value, self.ui_data[0]['obj_off'][2])
            elif value == 4: # Scale
                if self.ui_data[0]['obj_off'] is None:
                    self.ui_data[0]['obj_off'] = (False, False, True)
                else:
                    new_value = False if self.ui_data[0]['obj_off'][2] else True
                    self.ui_data[0]['obj_off'] = (self.ui_data[0]['obj_off'][0], self.ui_data[0]['obj_off'][1], new_value)
        
        #Update UI
        ui_opm_items = cmds.optionMenu( self.ui_items[0]['obj_off_opMenu'], query=True, itemListLong=True )
        #Calcul transform menu items's state
        ui_opm_items.pop(0)
        ui_opm_items.pop(3)
        labels = ('Pos','Rot','Scale')
        label_str = ''
        i = 0
        for ui_value in self.ui_data[0]['obj_off']:
            old_label = cmds.menuItem( ui_opm_items[i], query=True, label=True )
            if ui_value:
                cmds.menuItem( ui_opm_items[i], edit=True, label=f"☑{old_label[1:]}" )
                label_str = f'{label_str}/{labels[i]}'
            else:
                cmds.menuItem( ui_opm_items[i], edit=True, label=f"☐{old_label[1:]}" )
            i+=1
        #Update menu items
        if self.ui_data[0]['obj_off'] is None or self.ui_data[0]['obj_off'] == (False, False, False): #None
            self.ui_data[0]['obj_off'] = None
            cmds.optionMenu( self.ui_items[0]['obj_off_opMenu'], edit=True, label="  No offset                    ", select=1 )
        else: #Not none
            label_str = f"  {label_str[1:]}                    "
            cmds.optionMenu( self.ui_items[0]['obj_off_opMenu'], edit=True, label=label_str )
    elif drpdwn_idx == 1: #Offset type
        self.ui_data[0]['obj_off_type'] = cmds.optionMenu( self.ui_items[0]['obj_off_type_opMenu'], query=True, select=True ) #1:Hierarchy, 2:Selection, 3:Node
    elif drpdwn_idx == 2: #Offset reference
        self.ui_data[0]['obj_off_ref'] = cmds.optionMenu( self.ui_items[0]['obj_off_ref_opMenu'], query=True, select=True ) #1:Object, 2:Match

def _Update_ObjOff( self, self_idx:int ): #Update object offset UIs and eventually offset reference value
    """ Update object offset UIs and eventually offset reference value """
    if self is None:
        self = _Get_Instance( self_idx )

    #Update Object offset dropdowns' visibility
    if self.ui_data[0]['obj'] == 1 or self.ui_data[0]['match'] == 1 or (self.ui_data[0]['obj'] != 11 and self.ui_data[0]['match'] < 3): #Can't have offset
        cmds.optionMenu( self.ui_items[0]['obj_off_ref_opMenu'], edit=True, visible=False, width=1 )
        cmds.optionMenu( self.ui_items[0]['obj_off_opMenu'], edit=True, visible=False, width=1 )
        cmds.optionMenu( self.ui_items[0]['obj_off_type_opMenu'], edit=True, visible=False, width=1 )
        self.ui_data[0]['obj_off_ref'] = None
    else: #Can have offset
        cmds.optionMenu( self.ui_items[0]['obj_off_ref_opMenu'], edit=True, visible=True, width=70 )
        cmds.optionMenu( self.ui_items[0]['obj_off_opMenu'], edit=True, visible=True, width=105 )
        cmds.optionMenu( self.ui_items[0]['obj_off_type_opMenu'], edit=True, visible=True, width=100 )
    
        old_value = cmds.optionMenu( self.ui_items[0]['obj_off_ref_opMenu'], query=True, select=True )

        #Update Object offset reference dropdown's values
        if self.ui_data[0]['match'] < 3: #No match object
            cmds.menuItem( self.ui_items[0]['obj_off_ref_match'], edit=True, enable=False )
            cmds.menuItem( self.ui_items[0]['obj_off_ref_obj'], edit=True, enable=True )
            
            #Set ref Obj
            cmds.optionMenu( self.ui_items[0]['obj_off_ref_opMenu'], edit=True, select=1 )
            self.ui_data[0]['obj_off_ref'] = 1
        else: #Match object
            cmds.menuItem( self.ui_items[0]['obj_off_ref_match'], edit=True, enable=True )
            
            if self.ui_data[0]['obj'] == 11: # Selection object
                cmds.menuItem( self.ui_items[0]['obj_off_ref_obj'], edit=True, enable=True )
                
                if self.ui_data[0]['obj_off_ref'] is None:
                    #Set ref Obj
                    cmds.optionMenu( self.ui_items[0]['obj_off_ref_opMenu'], edit=True, select=1 )
                    self.ui_data[0]['obj_off_ref'] = 1
            else: # New object
                cmds.menuItem( self.ui_items[0]['obj_off_ref_obj'], edit=True, enable=False )
                
                #Set ref Match
                cmds.optionMenu( self.ui_items[0]['obj_off_ref_opMenu'], edit=True, select=2 )
                self.ui_data[0]['obj_off_ref'] = 2

# Match
def _Set_Match( self_idx:int, partial_empty=None ): #Set match value from dropdown UI
    """
    Set match value from dropdown UI\n
    ### Parameters:\n
    Note: 1:None, 2:Coordinate, 3:Closest to other, 4:Closest to selection\n
    'partial_empty' (bool): Extra 'False' argument from partial() when function call includes argument(s)
    """
    self = _Get_Instance( self_idx )

    old_option = self.ui_data[0]['match']
    option_idx = cmds.optionMenu( self.ui_items[0]['match_opMenu'], query=True, select=True )
    self.ui_data[0]['match'] = option_idx

    #Option extra UI and match_extra value
    if old_option != 1: #Reset UI if wasn't already cleared on None
        _Clear_Layout( self.ui_items[0]['match_extraLyt'] )
    else: #None
        self.ui_data[0]['match_extra'] = None
        self.ui_items[0]['match_extra_ui'] = None
    if option_idx == 2: #Coordinate
        
        uv_fields = [None, None]
        i = 0
        while i < 2:
            uv_fields[i] = cmds.floatField(
                height=28, width=70,
                value=0, precision=3, changeCommand=partial(_Set_MatchExtra, self_idx, 2, i),
                annotation='', statusBarMessage='',
                backgroundColor=self.THEME['crt']['extra_option_back'],
                parent=self.ui_items[0]['match_extraLyt']
            )
            if i == 0:
                cmds.separator( height=28, width=5, style='none', parent=self.ui_items[0]['match_extraLyt'] )
            i+=1
        self.ui_items[0]['match_extra_ui'] = uv_fields
        self.ui_data[0]['match_extra'] = (0,0)
    elif option_idx == 3: #Closest to other
        
        txtField, picker = _Build_PickerBttn(
            self.ui_items[0]['match_extraLyt'], 28,
            (   120, "None", True, partial(_Set_MatchOther, self_idx, False, None),
                "Node name\n\n(Will require a matrix output attribute)\n[Middle mouse]: Select node",
                "Node name    (Will require a matrix output attribute)  [Middle mouse]: Select node",
                self.THEME['crt']['extra_option_back'], partial(_Select_Callback, self_idx, 4)
            ),
            1,
            ( partial(_Pick_Init, self_idx, 1, _Pick_MatchOther_Done, 3, None, True, False, True),
                "Pick tool for match close to other node\n\n(Will require a matrix output attribute)",
                "Pick tool for match close to other node (Will require a matrix output attribute)",
                self.THEME['crt']['pick_back_off'], (25,25)
            )
        )
        self.ui_items[0]['match_extra_ui'] = (txtField, picker)
        self.ui_data[0]['match_extra'] = None
    elif option_idx == 4: #Selection
        
        anno_info = "Consider selection as pair(s) of:\n\n-Reference object from which to get closest position on geometry\nand\n-Object to receive new coordinate's output matrix"
        status_info = "Consider selection as pair(s) of: Reference object from which get closest position on geometry and object to receive new coordinate's output matrix"
        txtCtrl = cmds.text( height=28, label="Alternate closest and object", align='left', annotation=anno_info, statusBarMessage=status_info, parent=self.ui_items[0]['match_extraLyt'] )
        cmds.separator( height=28, width=5, style='none', parent=self.ui_items[0]['match_extraLyt'] )
        symbChckboxCtrl = cmds.symbolCheckBox(
            height=28, width=28,
            onImage='confirm.png', offImage='ghostingObjectTypeAll.png', highlightColor=self.THEME['crt']['crt_clmn_back'],
            onCommand=partial(_Set_MatchExtra, self_idx, 4, True), offCommand=partial(_Set_MatchExtra, self_idx, 4, False),
            annotation=anno_info, statusBarMessage=status_info,
            parent=self.ui_items[0]['match_extraLyt']
        )
        self.ui_items[0]['match_extra_ui'] = (txtCtrl, symbChckboxCtrl)
        self.ui_data[0]['match_extra'] = False
        _Update_MatchSel( self, self_idx )
    _Update_ObjOff( self, self_idx )

def _Set_MatchExtra( self_idx:int, idx:int, value, partial_empty=None ): #Set match_extra value from UI call
    """
    Set match_extra value from UI call\n
    ### Parameters:\n
    'idx' (int): Match kind index ( 2: coordinates, 4:selection )\n
    'value' (int/bool): Apply value ( idx 2:int idx for U/V, idx 3:bool Alternate state )\n
    'partial_empty' (bool): Extra 'False' argument from partial() when function call includes argument(s)
    """
    self = _Get_Instance( self_idx )

    if idx == 2:
        if value == 0:
            self.ui_data[0]['match_extra'] = ( cmds.floatField( self.ui_items[0]['match_extra_ui'][value], query=True, value=True ), self.ui_data[0]['match_extra'][1] )
        elif value == 1:
            self.ui_data[0]['match_extra'] = ( self.ui_data[0]['match_extra'][0], cmds.floatField( self.ui_items[0]['match_extra_ui'][value], query=True, value=True ) )
    #Idx 3 done via _Set_MatchExtra_Pick_Done
    if idx == 4:
        self.ui_data[0]['match_extra'] = value

def _Pick_MatchOther_Done( self_idx, skip_check=False ): #End function for match other pick
    """ End function for match other pick """
    self_idx = int(self_idx)
    self = _Get_Instance( self_idx )
    if self.callback_hook is not None: #Prevent function called twice
        self.callback_hook = None
    else:
        return
    
    if skip_check or (self.pick_sel != [] and self.pick_sel != None):
        _Set_MatchOther( self_idx, True, self.pick_sel[-1] )
    self.pick_sel = None
    self.pick_selData = None
    self.pick_ui = None

def _Set_MatchOther( self_idx:int, pick=False, node_name=None, partial_empty=None ): #Set match object value from textField and picker
    """ Set match object value from textField and picker """
    self = _Get_Instance( self_idx )

    txtField = self.ui_items[0]['match_extra_ui'][0]
    has_attr = False
    if not pick: #If called from textField
        node_name = cmds.textField( txtField, query=True, text=True )

        if '.' in node_name: #May have an attribute
            node_name = _Split_NodeAttr( node_name, True )
            
            if type(node_name) == list: #Node and attribute found
                node_name = f'{node_name[0]}.{node_name[1]}'
                self.ui_data[0]['match_extra'] = node_name
                cmds.textField( txtField, edit=True, text=node_name )
                has_attr = True
            elif node_name is not None: #Node found
                self.ui_data[0]['match_extra'] = node_name
                cmds.textField( txtField, edit=True, text=node_name )
        elif not cmds.objExists( node_name ): #No attribute and node doesn't exist
            node_name = None
    
        if node_name is None: #Revert to old value
            old_value = self.ui_data[0]['match_extra']
            if old_value is None:
                old_value = 'None'
            cmds.textField( txtField, edit=True, text=old_value )
            cmds.error( f"[ISSUE]: Node '{node_name}' not found!", noContext=True )
    else: #If called from picker
        self.ui_data[0]['match_extra'] = node_name
        cmds.textField( txtField, edit=True, text=node_name )
    
    if not has_attr:
        #Get all matching attributes
        attr_list = cmds.listAttr( node_name )
        attr_list_fixed = []
        attr_to_skip = {'controlPoints','pnt','pnts','vrts','edge','uvpt','face','weightList','envelopeWeightsList','perInfluenceWeights','bindPreMatrix','lockWeights'}
        for attr in attr_list:
            if attr in attr_to_skip: #Skip known useless multi attributes to prevent useless massive indexes to check
                continue
            if not cmds.attributeQuery( attr, node=node_name, exists=True ): #Skip some unusable multi children attributes
                continue
            
            t_attr_list = []
            if cmds.attributeQuery( attr, node=node_name, multi=True ): #If multi, add to the list every indexes too
                attr_size = cmds.getAttr( f'{node_name}.{attr}', size=True )
                if attr_size != -1: #Is multi
                    i = 0
                    while i < attr_size:
                        t_attr_list.append( f'{attr}[{i}]' )
                        i+=1
                else:
                    t_attr_list.append( attr )
            else: #Else add as it is
                t_attr_list.append( attr )
            for c_attr in t_attr_list:
                try:
                    if cmds.getAttr( f'{node_name}.{c_attr}', type=True ) != 'matrix': #Skip attributes not matching matrix type
                        continue
                except ValueError:
                    continue
                attr_list_fixed.append( c_attr )
        attr_list = []
        attr_list_fixed.sort() #Sort result attributes as alphabetical order may be quicker to read
        
        #Build attr list
        i = 0
        attr_list_fixed_len = len(attr_list_fixed)
        while i < attr_list_fixed_len:
            attr_list_fixed[i] = ( attr_list_fixed[i], (_AttrWin_MatchOtherBttn, self_idx, '<node>.<attr>') )
            i+=1

        _Build_AttrWindow( self, self_idx, node_name, attr_list_fixed, ("matrix output attribute","matrix",{'worldMatrix[0]'}) )

def _AttrWin_MatchOtherBttn( self_idx:int, value:str, partial_empty=None ): #Called by button on attr window to change match other attribute
    """ Called by button on attr window to change match other attribute """
    self = _Get_Instance( self_idx )

    self.ui_data[0]['match_extra'] = value
    txtField = self.ui_items[0]['match_extra_ui'][0]
    
    if txtField is not None:
        cmds.textField( txtField, edit=True, text=value )
    cmds.evalDeferred( f"cmds.deleteUI( '{self.attrwin}', window=True )" )
    self.attrwin = None

def _Update_MatchSel( self, self_idx:int ): #Update enable state of the match selection extra option UI
    """ Update enable state of the match selection extra option UI """
    if self is None:
        self = _Get_Instance( self_idx )
    
    if self.ui_data[0]['match'] != 4: #If UI not there anyway, skip
        return
    
    ui = self.ui_items[0]['match_extra_ui']
    if self.ui_data[0]['obj'] == 11: #Enabled option
        cmds.text( ui[0], edit=True, enable=True )
        cmds.symbolCheckBox( ui[1], edit=True, enable=True )
    else: #Disabled option
        cmds.text( ui[0], edit=True, enable=False )
        cmds.symbolCheckBox( ui[1], edit=True, enable=False )

# Start index
def _Set_Start_Idx( self_idx:int, arrow_idx=None, from_obj=False, value=None, partial_empty=None ): #Set start index
    """ Set start index """
    self = _Get_Instance( self_idx )
    
    if not from_obj:
        value = cmds.intField( self.ui_items[0]['start_idx_intField'], query=True, value=True )
        if arrow_idx == 0:
            value+=1
        elif arrow_idx == 1:
            value = value - 1 if value > 0 else 0
        self.ui_data[0]['start_idx'] = value

        if arrow_idx is not None: #If from arrows, update intField
            cmds.intField( self.ui_items[0]['start_idx_intField'], edit=True, value=value )
    else:
        self.ui_data[0]['start_idx'] = value
        cmds.intField( self.ui_items[0]['start_idx_intField'], edit=True, value=value )

def _Update_Start_Idx( self_idx:int, uvpin:str ): #Update start index
    """ Update start index """
    last_idx = cmds.getAttr( f'{uvpin}.coordinate', multiIndices=True ) #Get every uvp coordinate inputs
    last_idx = 0 if last_idx is None else last_idx[-1]+1
    _Set_Start_Idx( self_idx, None, True, last_idx )

# Mirror
def _Set_Mirror( self_idx:int, state:bool, partial_empty=None ): #Toggle mirror value from UI
    """ Toggle mirror value from UI """
    self = _Get_Instance( self_idx )
    self.ui_data[0]['mirror'] = state

def _Set_MirrorParam( self_idx:int, param_idx:int, from_ui=False, value=None, partial_empty=None ): #Set mirror behavior or offset method
    """
    Set mirror behavior or offset method\n
    ### Parameters:\n
    'param_idx' (int): Parameter index ( 0:Axis, 1:Space, 2:Behavior, 3:Method, 4:Name_type, 5:Name_source, 6:Name_target )\n
    'partial_empty' (bool): Extra 'False' argument from partial() when function call includes argument(s)
    """
    self = _Get_Instance( self_idx )

    if param_idx == 0:
        #Axis
        value = cmds.optionMenu( self.ui_items[0]['mirror_axis_opMenu'], query=True, select=True )
        if value == 1 or value == 5: #X
            self.ui_data[0]['mirror_axis'] = 0
        if value == 2 or value == 6: #Y
            self.ui_data[0]['mirror_axis'] = 1
        if value == 3 or value == 7: #Z
            self.ui_data[0]['mirror_axis'] = 2
        
        #If mirror name type isn't None and axis direction changed, flip mirror names
        if self.ui_data[0]['mirror_name_type'] != 1 and ((self.ui_data[0]['mirror_direction'] == -1 and value < 4) or (self.ui_data[0]['mirror_direction']) == 1 and value > 3):
            _Flip_Mirror_Names( self_idx )

        self.ui_data[0]['mirror_direction'] = -1 if value < 4 else 1
    elif param_idx == 1:
        #Space
        if not from_ui:
            value = cmds.symbolCheckBox( self.ui_items[0]['mirror_space_symbolChckBx'], query=True, value=True )
        
        if value: # Object space
            if self.ui_data[0]['mirror_space'] is None:
                self.ui_data[0]['mirror_space'] = cmds.textField( self.ui_items[0]['mirror_space_picker_txtField'], query=True, text=True )
            
            if from_ui: #Update symbolCheckBox value too
                cmds.symbolCheckBox( self.ui_items[0]['mirror_space_symbolChckBx'], edit=True, value=value, annotation="Object space", statusBarMessage="Object space" )
            else:
                cmds.symbolCheckBox( self.ui_items[0]['mirror_space_symbolChckBx'], edit=True, annotation="Object space", statusBarMessage="Object space" )
            
            #Show object space picker
            cmds.control( self.ui_items[0]['mirror_space_picker_txtField'], edit=True, visible=True )
            cmds.control( self.ui_items[0]['mirror_space_picker_symbBttn'], edit=True, visible=True )
        else: # World space
            self.ui_data[0]['mirror_space'] = None
            
            if from_ui: #Update symbolCheckBox value too
                cmds.symbolCheckBox( self.ui_items[0]['mirror_space_symbolChckBx'], edit=True, value=value, annotation="World space", statusBarMessage="World space" )
            else:
                cmds.symbolCheckBox( self.ui_items[0]['mirror_space_symbolChckBx'], edit=True, annotation="World space", statusBarMessage="World space" )
            
            #Hide object space picker
            cmds.control( self.ui_items[0]['mirror_space_picker_txtField'], edit=True, visible=False )
            cmds.control( self.ui_items[0]['mirror_space_picker_symbBttn'], edit=True, visible=False )
    elif param_idx == 2:
        #Behavior
        value = cmds.optionMenu( self.ui_items[0]['mirror_bhv_opMenu'], query=True, select=True )
        self.ui_data[0]['mirror_bhv'] = value
        
        if value == 3: # Enable offset method UI
            cmds.layout( self.ui_items[0]['mirror_offmtd_layout'], edit=True, enable=True )
            if self.ui_data[0]['mirror_offmtd'] == 1 or self.ui_data[0]['mirror_offmtd'] == 2: #If method requires object space, enable object space
                _Set_MirrorParam( self_idx, 1, True, True )
        else: # Disable offset method UI
            cmds.layout( self.ui_items[0]['mirror_offmtd_layout'], edit=True, enable=False )
    elif param_idx == 3:
        #Offset method
        value = cmds.optionMenu( self.ui_items[0]['mirror_offmdt_opMenu'], query=True, select=True )
        self.ui_data[0]['mirror_offmtd'] = value
        if value == 1 or value == 2: #If method requires object space, enable object space
            _Set_MirrorParam( self_idx, 1, True, True )
    elif param_idx == 4:
        #Name type
        self.ui_data[0]['mirror_name_type'] = cmds.optionMenu( self.ui_items[0]['mirror_name_type_opMenu'], query=True, select=True )
    elif param_idx == 5:
        #Name source
        if from_ui:
            self.ui_data[0]['mirror_name_source'] = value
            cmds.textField( self.ui_items[0]['mirror_name_source_txtField'], edit=True, text=value )
        else:
            self.ui_data[0]['mirror_name_source'] = cmds.textField( self.ui_items[0]['mirror_name_source_txtField'], query=True, text=True )
    elif param_idx == 6:
        #Name target
        if from_ui:
            self.ui_data[0]['mirror_name_target'] = value
            cmds.textField( self.ui_items[0]['mirror_name_target_txtField'], edit=True, text=value )
        else:
            self.ui_data[0]['mirror_name_target'] = cmds.textField( self.ui_items[0]['mirror_name_target_txtField'], query=True, text=True )

def _Flip_Mirror_Names( self_idx:int, partial_empty=None ): #Flip mirror name source and to target
    """ Flip mirror name source and target values """
    self = _Get_Instance( self_idx )

    old_source = self.ui_data[0]['mirror_name_source']
    _Set_MirrorParam( self_idx, 5, True, self.ui_data[0]['mirror_name_target'] )
    _Set_MirrorParam( self_idx, 6, True, old_source )

def _Pick_Mirror_SpaceObj_Done( self_idx, skip_check=False ): #End function for mirror space object pick
    """ End function for mirror space object pick """
    self_idx = int(self_idx)
    self = _Get_Instance( self_idx )
    if self.callback_hook is not None: #Prevent function called twice
        self.callback_hook = None
    else:
        return
    
    if skip_check or (self.pick_sel != [] and self.pick_sel != None):
        _Set_Mirror_SpaceObject( self_idx, True, self.pick_sel[-1] )
    self.pick_sel = None
    self.pick_selData = None
    self.pick_ui = None

def _Set_Mirror_SpaceObject( self_idx:int, pick=False, node_name=None, partial_empty=None ): #Set mirror space object value from textField and picker
    """ Set mirror space object value from textField and picker """
    self = _Get_Instance( self_idx )

    txtField = self.ui_items[0]['mirror_space_picker_txtField']
    has_attr = False
    if not pick: #If called from textField
        node_name = cmds.textField( txtField, query=True, text=True )

        if '.' in node_name: #May have an attribute
            node_name = _Split_NodeAttr( node_name, True )
            
            if type(node_name) == list: #Node and attribute found
                node_name = f'{node_name[0]}.{node_name[1]}'
                self.ui_data[0]['mirror_space'] = node_name
                cmds.textField( txtField, edit=True, text=node_name )
                has_attr = True
            elif node_name is not None: #Node found
                self.ui_data[0]['mirror_space'] = node_name
                cmds.textField( txtField, edit=True, text=node_name )
        elif not cmds.objExists( node_name ): #No attribute and node doesn't exist
            node_name = None
    
        if node_name is None: #Revert to old value
            old_value = self.ui_data[0]['mirror_space']
            if old_value is None:
                old_value = 'None'
            cmds.textField( txtField, edit=True, text=old_value )
            cmds.error( f"[ISSUE]: Node '{node_name}' not found!", noContext=True )
    else: #If called from picker
        self.ui_data[0]['mirror_space'] = node_name
        cmds.textField( txtField, edit=True, text=node_name )
    
    if not has_attr:
        #Get all matching attributes
        attr_list = cmds.listAttr( node_name )
        attr_list_fixed = []
        attr_to_skip = {'controlPoints','pnt','pnts','vrts','edge','uvpt','face','weightList','envelopeWeightsList','perInfluenceWeights','bindPreMatrix','lockWeights'}
        for attr in attr_list:
            if attr in attr_to_skip: #Skip known useless multi attributes to prevent useless massive indexes to check
                continue
            if not cmds.attributeQuery( attr, node=node_name, exists=True ): #Skip some unusable multi children attributes
                continue
            
            t_attr_list = []
            if cmds.attributeQuery( attr, node=node_name, multi=True ): #If multi, add to the list every indexes too
                attr_size = cmds.getAttr( f'{node_name}.{attr}', size=True )
                if attr_size != -1: #Is multi
                    i = 0
                    while i < attr_size:
                        t_attr_list.append( f'{attr}[{i}]' )
                        i+=1
                else:
                    t_attr_list.append( attr )
            else: #Else add as it is
                t_attr_list.append( attr )
            for c_attr in t_attr_list:
                try:
                    if cmds.getAttr( f'{node_name}.{c_attr}', type=True ) != 'matrix': #Skip attributes not matching matrix type
                        continue
                except ValueError:
                    continue
                attr_list_fixed.append( c_attr )
        attr_list = []
        attr_list_fixed.sort() #Sort result attributes as alphabetical order may be quicker to read
        
        #Build attr list
        i = 0
        attr_list_fixed_len = len(attr_list_fixed)
        while i < attr_list_fixed_len:
            attr_list_fixed[i] = ( attr_list_fixed[i], (_AttrWin_MirrorSpaceBttn, self_idx, '<node>.<attr>') )
            i+=1

        _Build_AttrWindow( self, self_idx, node_name, attr_list_fixed, ("matrix output attribute","matrix",{'worldMatrix[0]'}) )

def _AttrWin_MirrorSpaceBttn( self_idx:int, value:str, partial_empty=None ): #Called by button on attr window to change mirror space object attribute
    """ Called by button on attr window to change mirror space object attribute """
    self = _Get_Instance( self_idx )

    self.ui_data[0]['mirror_space'] = value
    txtField = self.ui_items[0]['mirror_space_picker_txtField']
    
    if txtField is not None:
        cmds.textField( txtField, edit=True, text=value )
    cmds.evalDeferred( f"cmds.deleteUI( '{self.attrwin}', window=True )" )
    self.attrwin = None

def _Refresh_UVPin( uvpin:str, co_idx:int ): #Try to refresh uvPin outputMatrix value by connecting and disconnecting a temporary transform to it
    """ Try to refresh uvPin outputMatrix value by connecting and disconnecting a temporary transform to it """
    temp_obj = cmds.createNode( 'transform', skipSelect=True )
    cmds.connectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{temp_obj}.offsetParentMatrix' )
    cmds.disconnectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{temp_obj}.offsetParentMatrix' )
    cmds.delete( temp_obj )

def _Create_Offset( offset_type:int, uvpin:str, co_idx:int, target_obj:str, ref_obj:str, keep_pos:bool, keep_rot:bool, keep_sca:bool, geo_defo=None ): #Create offset on object and connect it to uvpin
    """
    Create offset on object and connect it to uvpin\n
    ### Parameters:\n
    'offset_type' (int): self.ui_data[0]['obj_off_type'] value\n
    'uvpin' (str): uvPin's name\n
    'co_idx' (int): target's coordinate index\n
    'target_obj' (str): Object to apply offset and coordinate matrix on\n
    'ref_obj' (str): Object to get offset from transform(s)\n
    'keep_pos' (bool): Keep position\n
    'keep_rot' (bool): Keep rotation\n
    'keep_sca' (bool): Keep scale\n
    'geo_invmtx' (None/str): Original geometry's worldMatrix[0]\n
    ### Return:\n
    Offset (str) if offset hierarchy else target_obj (str)
    """
    if offset_type == 1:
        #Apply offset on a new parent, joint if selection is joint else transform
        
        # Save world transforms on a temporary object
        offset = cmds.createNode( 'transform', skipSelect=True )
        cmds.matchTransform( offset, ref_obj, position=keep_pos, rotation=keep_rot, scale=keep_sca )
        
        # New parent
        target_obj = _Create_Parent( target_obj, True )
        # Connect coordinate matrix to offset parent
        cmds.connectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{target_obj}.offsetParentMatrix', force=True )
        
        # Move target_obj to old pos
        cmds.matchTransform( target_obj, offset, position=keep_pos, rotation=keep_rot, scale=keep_sca )
        cmds.delete( offset )
    elif offset_type == 2:
        #Apply offset on selection
        
        # Save world transforms on a temporary object
        offset = cmds.createNode( 'transform', skipSelect=True )
        cmds.matchTransform( offset, ref_obj, position=keep_pos, rotation=keep_rot, scale=keep_sca )
        
        # Reset target_obj's transforms
        if cmds.nodeType( target_obj ) == 'joint':
            _Clear_Transform( target_obj, ('jointOrient',) )
        else:
            _Clear_Transform( target_obj )
        # Connect coordinate matrix to target_obj
        cmds.connectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{target_obj}.offsetParentMatrix', force=True )
        
        # Move target_obj to old pos
        cmds.matchTransform( target_obj, offset, position=keep_pos, rotation=keep_rot, scale=keep_sca )
        cmds.delete( offset )
    elif offset_type == 3:
        #Apply offset on intermediate node
        
        node_offset = cmds.createNode( 'multMatrix', name=f'{target_obj}_offset_mmtx', skipSelect=True )
        # Calculate offset matrix via the node_offset multMatrix
        ref_obj_mtx = cmds.getAttr( f'{ref_obj}.worldMatrix[0]' )
        # Try to update uvPin's deformed geometry cache so coordinate's outputMatrix should be correct even with deformers
        if cmds.attributeQuery( 'caching', node=geo_defo, exists=True ):
            old_caching = cmds.getAttr( f'{geo_defo}.caching' )
            if old_caching == 1:
                cmds.setAttr( f'{geo_defo}.caching', 0 )
            cmds.setAttr( f'{geo_defo}.caching', 1 )
            cmds.setAttr( f'{geo_defo}.caching', old_caching )
        if co_idx == 0: #If first coordinate, connect and disconnect outputMatrix to a temporary transform to have it update it's value
            _Refresh_UVPin( uvpin, co_idx )
        # Calcul offset via the multMatrix
        co_invmtx = cmds.getAttr( f'{uvpin}.outputMatrix[{co_idx}]' )
        co_invmtx = cmds.matrixUtil( *co_invmtx, inverse=True )
        cmds.setAttr( f'{node_offset}.matrixIn[0]', *ref_obj_mtx, type='matrix' )
        cmds.setAttr( f'{node_offset}.matrixIn[1]', *co_invmtx, type='matrix' )
        offset_mtx = cmds.getAttr( f'{node_offset}.matrixSum' )
        # Remove unasked transform offset(s)
        if not keep_pos:
            offset_mtx = cmds.matrixUtil( *offset_mtx, edit=True, translation=(0,0,0) )
        if not keep_rot:
            offset_mtx = cmds.matrixUtil( *offset_mtx, edit=True, rotation=(0,0,0) )
        if not keep_sca:
            offset_mtx = cmds.matrixUtil( *offset_mtx, edit=True, scale=(1,1,1) )
        
        # Apply offset and coordinate matrix on target_obj
        cmds.setAttr( f'{node_offset}.matrixIn[0]', *offset_mtx, type='matrix' )
        cmds.connectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{node_offset}.matrixIn[1]', force=True )
        cmds.connectAttr( f'{node_offset}.matrixSum', f'{target_obj}.offsetParentMatrix', force=True )
        # Reset target_obj's transforms
        if cmds.nodeType( target_obj ) == 'joint':
            _Clear_Transform( target_obj, ('jointOrient',) )
        else:
            _Clear_Transform( target_obj )
    return target_obj

# Create uvPin/object
def _Create_UVPin( self_idx:int, partial_empty=None ): #Create UVPin or update an existing one
    """ Create UVPin or update an existing one """
    self = _Get_Instance( self_idx )
    
    # Check variables
    if self.ui_data[0]['uvpin_new']:
        if self.ui_data[0]['uvpin'] is None:
            cmds.error( f"[ISSUE]: No uvPin name set!", noContext=True )
        elif cmds.objExists( self.ui_data[0]['uvpin'] ):
            cmds.error( f"[ISSUE]: A node named '{self.ui_data[0]['uvpin']}' already exists since uvPin name was set!", noContext=True )
    else:
        if not cmds.objExists( self.ui_data[0]['uvpin'] ):
            _Update_UVPIN_State( self, True )
            cmds.error( f"[ISSUE]: uvPin '{self.ui_data[0]['uvpin']}' not found", noContext=True )
        elif type( cmds.getAttr( f"{self.ui_data[0]['uvpin']}.nodeState" ) ) == list:
            cmds.error( f"[ISSUE]: More than one uvPin '{self.ui_data[0]['uvpin']}' found!", noContext=True )
    if self.ui_data[0]['geo_orig'] == 'None':
        cmds.error( f"[ISSUE]: No object picked on the 'Original' geometry parameter!", noContext=True )
    elif '.' not in self.ui_data[0]['geo_orig']:
        cmds.error( f"[ISSUE]: No attribute found one original geometry '{self.ui_data[0]['geo_orig']}'! An output geometry attribute is necessary", noContext=True )
    elif not cmds.objExists( self.ui_data[0]['geo_orig'] ):
        cmds.error( f"[ISSUE]: Original geometry '{self.ui_data[0]['geo_orig']}' not found!", noContext=True )
    
    if self.ui_data[0]['geo_defo'] == 'None':
        cmds.error( f"[ISSUE]: No object picked on the 'Deformed' geometry parameter!", noContext=True )
    elif '.' not in self.ui_data[0]['geo_defo']:
        cmds.error( f"[ISSUE]: No attribute found one deformed geometry '{self.ui_data[0]['geo_defo']}'! An output geometry attribute is necessary", noContext=True )
    elif not cmds.objExists( self.ui_data[0]['geo_defo'] ):
        cmds.error( f"[ISSUE]: Deformed geometry '{self.ui_data[0]['geo_defo']}' not found!", noContext=True )
    
    if (self.ui_data[0]['match'] == 3 or self.ui_data[0]['match'] == 4) and self.ui_data[0]['geo_type'] != 'mesh' and self.ui_data[0]['geo_type'] != 'nurbsSurface':
        cmds.error( f"[ISSUE]: 'geo_type' value hasn't been updated when setting geometry value(s)! Match 'Closest to' requires 'mesh' or 'nurbsSurface' type", noContext=True )
    if self.ui_data[0]['match'] == 3 and self.ui_data[0]['match_extra'] is None:
        cmds.error( f"[ISSUE]: Nothing set in the match to other field!", noContext=True )
    
    if self.ui_data[0]['mirror']:
        if (self.ui_data[0]['match'] == 3 or self.ui_data[0]['match'] == 4) and self.ui_data[0]['geo_type'] != 'mesh' and self.ui_data[0]['geo_type'] != 'nurbsSurface':
            cmds.error( f"[ISSUE]: 'geo_type' value hasn't been updated when setting geometry value(s)! Match 'Closest to' requires 'mesh' or 'nurbsSurface' type", noContext=True )
        if self.ui_data[0]['mirror_space'] is not None and not cmds.objExists( self.ui_data[0]['mirror_space'] ):
            cmds.error( f"[ISSUE]: Mirror space object '{self.ui_data[0]['mirror_space']}' not found!", noContext=True )
    # Check variables

    # Get and check selection if Object set to selection
    pre_sel = cmds.ls( selection=True, objectsOnly=True )
    if (self.ui_data[0]['obj'] == 11 or self.ui_data[0]['match'] == 4): #If Object is selection or Match is closest to selection
        if pre_sel is None:
            cmds.error( f"[ISSUE]: No object selected!", noContext=True )
        else:
            if pre_sel == []:
                cmds.error( f"[ISSUE]: No object selected!", noContext=True )
            if pre_sel[-1] == self.ui_data[0]['geo']:
                cmds.error( f"[ISSUE]: Geometry object can't be it's own selection coordinate target object!", noContext=True )
    # Get and check selection if Object set to selection

    #Create/get uvpin
    uvpin = None
    geo_orig_node = _Split_NodeAttr( self.ui_data[0]['geo_orig'] )
    geo_defo_node = _Split_NodeAttr( self.ui_data[0]['geo_defo'] )
    if self.ui_data[0]['uvpin_new']:
        #Create
        uvpin = cmds.createNode( 'uvPin', name=self.ui_data[0]['uvpin'], skipSelect=True )
        
        if uvpin != self.ui_data[0]['uvpin']: #If doesn't match Maya naming, update uvpin data and UI
            self.ui_data[0]['uvpin'] = uvpin
            cmds.textField( self.ui_items[0]['uvp_picker_txtField'], edit=True, text=uvpin )
        #Update uvPin state text
        _Update_UVPIN_State( self, False )
        
        #Connect geometry to uvpin
        cmds.connectAttr( self.ui_data[0]['geo_orig'], f"{uvpin}.originalGeometry" )
        cmds.connectAttr( self.ui_data[0]['geo_defo'], f"{uvpin}.deformedGeometry" )
        if geo_orig_node == geo_defo_node: #Same geometry for both, requires sending object's inverseWorldMatrix into uvPin's spaceMatrix for coordinates to follow object
            cmds.setAttr( f'{uvpin}.relativeSpaceMode', 2 )
            cmds.connectAttr( f"{geo_orig_node}.worldInverseMatrix[0]", f'{uvpin}.relativeSpaceMatrix' )
    else:
        uvpin = self.ui_data[0]['uvpin']
        #Check actual connections on original and deformed geometry match what is setup, else ask what to do
        to_check = ( ('originalGeometry', self.ui_data[0]['geo_orig'], "original geometry", 'geo_orig'), ('deformedGeometry', self.ui_data[0]['geo_defo'], "deformed geometry", 'geo_defo') )
        for geo in to_check:
            c_source = cmds.connectionInfo( f"{uvpin}.{geo[0]}", sourceFromDestination=True )
            confirm = None
            if c_source == '':
                confirm = f"No {geo[2]} already connected to uvPin\n\nConnect '{geo[1]}' ?"
            elif c_source != geo[1]:
                confirm = f"Different {geo[2]} set than what is connected to the uvPin!\n\nDo you want to apply the change to '{geo[1]}' ?"
            
            if confirm is not None:
                #If there is a change to ask
                confirm_result = cmds.confirmDialog(
                    title="Create object",
                    message=confirm,
                    button=["Yes","No","Cancel"], defaultButton="No", cancelButton="Cancel", dismissString="Cancel"
                )
                if confirm_result == "Cancel":
                    cmds.inViewMessage( message=f"<font color={self.THEME['cancel_txt']}>Object creation cancelled!</font color>", position="botCenter", fade=True, fadeOutTime=300 )
                    print( "[INFO]: Object creation cancelled!" )
                    return
                elif confirm_result == "Yes": #Connect what is setup in ui_data to the attribute
                    cmds.connectAttr( self.ui_data[0][geo[3]], f"{uvpin}.{geo[0]}", force=True )
        
        #Check last index has a gap with actual last index
        last_idx = cmds.getAttr( f'{uvpin}.coordinate', multiIndices=True ) #Get every uvp coordinate inputs
        last_idx = 0 if last_idx is None else last_idx[-1]+1
        if self.ui_data[0]['start_idx'] > last_idx:
            confirm_result = cmds.confirmDialog(
                title="Start index gap",
                message=f"Start index '{self.ui_data[0]['start_idx']}' is higher to actual\nuvPin's next index '{last_idx}'\n\nChange start index to '{last_idx}' ?",
                button=["Yes","No"], defaultButton="No", cancelButton="No", dismissString="No"
            )
            if confirm_result == "Yes":
                _Set_Start_Idx( self_idx, None, True, last_idx )
    
    #Create coordinates
    uv_pos = [] # [((uv), target_matrix), ...] or ((uv), target_matrix) or (uv)
    single_uv = False
    target_obj = None
    source_pos_obj = None
    uv_tfmtx = None
    uv_closestPoint = None

    #Match
    if self.ui_data[0]['match'] == 1: #None
        co = cmds.getAttr( f'{uvpin}.coordinate', multiIndices=True )
        if co is not None and self.ui_data[0]['start_idx'] in co: #If coordinate index already exists, don't overwrite it with (0,0) and get it's value instead
            uv_pos = cmds.getAttr( f"{uvpin}.coordinate[{self.ui_data[0]['start_idx']}]" )[0]
        else:
            uv_pos = (0,0)
        single_uv = True
    elif self.ui_data[0]['match'] == 2: #Coordinate
        uv_pos = self.ui_data[0]['match_extra']
        single_uv = True
    else: #Closest to other and closest to selection
        source_pos = None

        #Get source_pos and in one case target_obj
        if self.ui_data[0]['match'] == 3: #Closest to other
            source_pos = ( self.ui_data[0]['match_extra'], )
            single_uv = True
        else: #Closest to selection
            sel = pre_sel

            if sel is not None:
                if self.ui_data[0]['match_extra']: #Alternate source_pos and target_obj
                    source_pos = []
                    target_obj = []
                    sel_len = len(sel)
                    
                    i = 0
                    to_ref = True
                    while i < sel_len:
                        if to_ref:
                            source_pos.append( f'{sel[i]}.worldMatrix[0]' )
                            to_ref = False
                        else:
                            target_obj.append( sel[i] )
                            to_ref = True
                        i+=1
                else: #Don't alternate
                    source_pos = []
                    for c_sel in sel:
                        source_pos.append( f'{c_sel}.worldMatrix[0]' )
                    if self.ui_data[0]['obj'] == 11: #Object set to selection, add selection as target(s)
                        target_obj = sel

        if source_pos is not None:
            #Get closest UV from source_pos object(s)
            # Prepare system
            is_mesh = True if self.ui_data[0]['geo_type'] == 'mesh' else False
            uv_tfmtx = cmds.createNode( 'translationFromMatrix', skipSelect=True )
            uv_closestPoint = 'closestPointOnMesh' if is_mesh else 'closestPointOnSurface'
            uv_closestPoint = cmds.createNode( uv_closestPoint, skipSelect=True )
            cmds.connectAttr( f'{uv_tfmtx}.output', f"{uv_closestPoint}.inPosition" )
            cmds.connectAttr( self.ui_data[0]['geo_defo'], f"{uv_closestPoint}.{'inMesh' if is_mesh else 'inputSurface'}" )
            if is_mesh:
                cmds.connectAttr( f"{geo_orig_node}.worldMatrix[0]", f'{uv_closestPoint}.inputMatrix' )
            
            #Get uv position closest to each source_pos object and, if with remaning targets, store them in uv_pos
            for c_source in source_pos:
                cmds.connectAttr( c_source, f'{uv_tfmtx}.input', force=True )
                uv = ( cmds.getAttr(f'{uv_closestPoint}.parameterU'), cmds.getAttr(f'{uv_closestPoint}.parameterV') )
                uv_pos.append( uv )
            if len(uv_pos) == 1: #If only one coordinate, set it directly as uv_pos instead of inside a list
                uv_pos = uv_pos[0]
                single_uv = True
            # Delete system
            if not self.ui_data[0]['mirror']:
                cmds.delete( uv_tfmtx, uv_closestPoint )
                uv_tfmtx = None
                uv_closestPoint = None
            if self.ui_data[0]['obj_off'] is not None and self.ui_data[0]['obj_off_ref'] == 2: #Offset on targets to do, store source pos objects without their attribute
                source_pos_obj = []
                for c_source in source_pos:
                    source_pos_obj.append( _Split_NodeAttr( c_source ) )
                source_pos_obj = tuple(source_pos_obj)
    if uv_pos is None:
        uv_pos = (0,0)
        single_uv = True

    #Objects
    offset_pos = None
    offset_rot = None
    offset_sca = None
    if self.ui_data[0]['obj'] != 1: #If not None
        c_targets = None
        # Create object
        if self.ui_data[0]['obj'] > 1 and self.ui_data[0]['obj'] < 7: #Joint controller // Joint > Joint controller  or  Joint locator // Joint > Joint locator
            suffix = None
            shape_obj = None
            shape = None
            # Get suffix and create shape
            if self.ui_data[0]['obj'] == 2 or self.ui_data[0]['obj'] == 3: #Controller
                suffix = '_ctrl'
                shape_obj = cmds.circle( radius=2, object=True, constructionHistory=False, normal=(1,0,0) )
            elif self.ui_data[0]['obj'] == 5 or self.ui_data[0]['obj'] == 6: #Locator
                suffix = '_loc'
                shape_obj = cmds.createNode( 'transform', skipSelect=True )
                shape = cmds.createNode( 'locator', parent=shape_obj, skipSelect=True )
            
            # Create joint
            c_targets = cmds.createNode( 'joint', name=f"{self.ui_data[0]['uvpin']}_item{self.ui_data[0]['start_idx']}_jnt{suffix}", skipSelect=True )
            
            # Parent shape under joint, remove old shape parent and set color on shape
            shape = cmds.listRelatives( shape_obj, children=True, shapes=True ) if shape is None else shape
            cmds.parent( shape, c_targets, relative=True, shape=True )
            shape = cmds.rename( shape, f'{c_targets}Shape' )
            cmds.delete( shape_obj )
            cmds.setAttr( f'{c_targets}.drawStyle', 2 )
            cmds.setAttr( f'{shape}.overrideEnabled', 1 )
            cmds.setAttr( f'{shape}.overrideColor', 13 )
            
            has_parent = False
            if self.ui_data[0]['obj'] == 3 or self.ui_data[0]['obj'] == 6: #Joint > Joint controller  or  Joint > Joint locator
                has_parent = True
                # Add above joint and set it as c_targets
                new_target = cmds.createNode( 'joint', name=f"{c_targets}_orig", skipSelect=True )
                cmds.setAttr( f'{new_target}.drawStyle', 2 )
                cmds.setAttr( f'{new_target}.radius', 1.5 )
                cmds.parent( c_targets, new_target )
                _Clear_Transform( c_targets )
                c_targets = new_target
            
            if not single_uv: # Object to duplicate for each coordinate
                extra_targets = []
                name_format = ( f"{self.ui_data[0]['uvpin']}_item", f"_jnt{suffix}_orig" ) if has_parent else ( f"{self.ui_data[0]['uvpin']}_item", f"_jnt{suffix}" )
                co_idx = self.ui_data[0]['start_idx']
                is_first = True
                for coordinate in uv_pos:
                    if is_first:
                        is_first = False
                        co_idx+=1
                    else:
                        extra_targets.append( cmds.duplicate( c_targets, name=f"{name_format[0]}{co_idx}{name_format[1]}", renameChildren=True )[0] )
                        co_idx+=1
                c_targets = [ c_targets, *extra_targets ]
            else:
                c_targets = [ c_targets ]
        elif self.ui_data[0]['obj'] == 8: #Transform
            c_targets = cmds.createNode( 'transform', name=f"{self.ui_data[0]['uvpin']}_item{self.ui_data[0]['start_idx']}_trnsf", skipSelect=True )
            c_targets = [ c_targets ]
        elif self.ui_data[0]['obj'] == 9: #Joint
            c_targets = cmds.createNode( 'joint', name=f"{self.ui_data[0]['uvpin']}_item{self.ui_data[0]['start_idx']}_jnt", skipSelect=True )
            c_targets = [ c_targets ]
        elif self.ui_data[0]['obj'] == 11: #Selection
            if target_obj is None: 
                c_targets = pre_sel
            else:
                c_targets = target_obj
            
            if self.ui_data[0]['obj_off'] is not None and self.ui_data[0]['obj_off_ref'] == 1: #If offset from selected objects
                source_pos_obj = c_targets
        
        cmds.select( clear=True )
        target_obj = c_targets
    
    #Offset
    if self.ui_data[0]['obj_off'] is not None:
        offset_pos = self.ui_data[0]['obj_off'][0]
        offset_rot = self.ui_data[0]['obj_off'][1]
        offset_sca = self.ui_data[0]['obj_off'][2]
    
    #Create coordinate(s)
    co_idx = self.ui_data[0]['start_idx']
    i = 0
    if single_uv: #Single UV
        # Create coordinate for each target object and set them all to the same UV
        if not (self.ui_data[0]['obj'] == 1 and self.ui_data[0]['match'] == 1): #If at least object or match isn't on None, else skip and don't create coordinate
            if target_obj is None: #No target object
                cmds.setAttr( f'{uvpin}.coordinate[{co_idx}]', *uv_pos )
                #Refresh uvPin to have outputMatrix updated
                _Refresh_UVPin( uvpin, co_idx )
            else:
                if self.ui_data[0]['obj_off'] is not None and source_pos_obj is not None: # Selection with offset
                    for target in target_obj:
                        cmds.setAttr( f'{uvpin}.coordinate[{co_idx}]', *uv_pos )
                        if i == 0: #Refresh uvPin to have outputMatrix updated
                            _Refresh_UVPin( uvpin, co_idx )
                        # Create/Apply offset, connect matrix to target and update target_obj with current top parent target object
                        target_obj[i] = _Create_Offset( self.ui_data[0]['obj_off_type'], uvpin, co_idx, target, source_pos_obj[i], offset_pos, offset_rot, offset_sca, geo_defo_node )
                        co_idx+=1
                        i+=1
                else: #Connect directly coordinate matrixes to targets
                    for target in target_obj:
                        cmds.setAttr( f'{uvpin}.coordinate[{co_idx}]', *uv_pos )
                        if i == 0: #Refresh uvPin to have outputMatrix updated
                            _Refresh_UVPin( uvpin, co_idx )
                        # Connect matrix to target
                        cmds.connectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{target}.offsetParentMatrix', force=True )
                        if cmds.nodeType( target ) == 'joint':
                            _Clear_Transform( target )
                        else:
                            _Clear_Transform( target, ('jointOrient',) )
                        co_idx+=1
                        i+=1
    else: #Multiple UV
        # Create coordinate for each UV and set them by order target objects
        if target_obj is None: #No target object
            for coordinate in uv_pos:
                cmds.setAttr( f'{uvpin}.coordinate[{co_idx}]', *coordinate )
                if i == 0: #Refresh uvPin to have outputMatrix updated
                    _Refresh_UVPin( uvpin, co_idx )
                    i = 1
                co_idx+=1
        else:
            target_obj_len = len(target_obj)
            if self.ui_data[0]['obj_off'] is not None and source_pos_obj is not None: # Selection with offset
                for coordinate in uv_pos:
                    cmds.setAttr( f'{uvpin}.coordinate[{co_idx}]', *coordinate )
                    if i == 0: #Refresh uvPin to have outputMatrix updated
                        _Refresh_UVPin( uvpin, co_idx )
                    if i < target_obj_len:
                        # Create/Apply offset, connect matrix to target and update target_obj with current top parent target object
                        target_obj[i] = _Create_Offset( self.ui_data[0]['obj_off_type'], uvpin, co_idx, target_obj[i], source_pos_obj[i], offset_pos, offset_rot, offset_sca, geo_defo_node )
                    co_idx+=1
                    i+=1
            else: #Connect directly coordinate matrixes to targets
                for coordinate in uv_pos:
                    cmds.setAttr( f'{uvpin}.coordinate[{co_idx}]', *coordinate )
                    if i == 0: #Refresh uvPin to have outputMatrix updated
                        _Refresh_UVPin( uvpin, co_idx )
                    if i < target_obj_len:
                        target = target_obj[i]
                        # Connect matrix to target
                        cmds.connectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{target}.offsetParentMatrix', force=True )
                        if cmds.nodeType( target ) == 'joint':
                            _Clear_Transform( target )
                        else:
                            _Clear_Transform( target, ('jointOrient',) )
                    co_idx+=1
                    i+=1
    
    if self.ui_data[0]['mirror']:
        target_obj = _Mirror( self, self_idx, target_obj, ( uv_tfmtx, uv_closestPoint, co_idx ) )
    _Update_Start_Idx( self_idx, uvpin )
    
    cmds.select( target_obj, replace=True )

def _Mirror( self, self_idx:int, targets, uv_system, from_ui=False, partial_empty=None ): #Mirror target objects and then add them to the uvPin
    """
    Mirror target objects and then add them to the uvPin\n
    ### Parameters:\n
    'self' (None/UVPin_Global): Class instance object\n
    'self_idx' (int): Index from which get class instance object in global_win_instances dictionnary\n
    'targets' (tuple/list): List of target objects to duplicate, mirror and add to the uvPin\n
    'uv_system' (None/tuple): Tuple of closest to UV system data if not from_ui ( uv_tfmtx(str), uv_closestPoint(str), co_idx(int) )\n
    'from_ui' (bool): Used by mirror button, get targets from selection\n
    'partial_empty' (bool): Extra 'False' argument from partial() when function call includes argument(s)
    ### Return:\n
    'targets' (None/tuple): Tuple of target names for both sides
    """
    if self is None:
        self = _Get_Instance( self_idx )
    
    if from_ui:
        targets = cmds.ls( selection=True, objectsOnly=True )
        # Check variables
        if self.ui_data[0]['uvpin'] is None:
            cmds.error( f"[ISSUE]: No uvPin name set!", noContext=True )
        else:
            if not cmds.objExists( self.ui_data[0]['uvpin'] ):
                _Update_UVPIN_State( self, True )
                cmds.error( f"[ISSUE]: uvPin '{self.ui_data[0]['uvpin']}' not found", noContext=True )
            elif type( cmds.getAttr( f"{self.ui_data[0]['uvpin']}.nodeState" ) ) == list:
                cmds.error( f"[ISSUE]: More than one uvPin '{self.ui_data[0]['uvpin']}' found!", noContext=True )
        
        if self.ui_data[0]['geo_orig'] == 'None':
            cmds.error( f"[ISSUE]: No object picked on the 'Original' geometry parameter!", noContext=True )
        elif '.' not in self.ui_data[0]['geo_orig']:
            cmds.error( f"[ISSUE]: No attribute found one original geometry '{self.ui_data[0]['geo_orig']}'! An output geometry attribute is necessary", noContext=True )
        elif not cmds.objExists( self.ui_data[0]['geo_orig'] ):
            cmds.error( f"[ISSUE]: Original geometry '{self.ui_data[0]['geo_orig']}' not found!", noContext=True )
        
        if self.ui_data[0]['geo_defo'] == 'None':
            cmds.error( f"[ISSUE]: No object picked on the 'Deformed' geometry parameter!", noContext=True )
        elif '.' not in self.ui_data[0]['geo_defo']:
            cmds.error( f"[ISSUE]: No attribute found one deformed geometry '{self.ui_data[0]['geo_defo']}'! An output geometry attribute is necessary", noContext=True )
        elif not cmds.objExists( self.ui_data[0]['geo_defo'] ):
            cmds.error( f"[ISSUE]: Deformed geometry '{self.ui_data[0]['geo_defo']}' not found!", noContext=True )
        
        if (self.ui_data[0]['match'] == 3 or self.ui_data[0]['match'] == 4) and self.ui_data[0]['geo_type'] != 'mesh' and self.ui_data[0]['geo_type'] != 'nurbsSurface':
            cmds.error( f"[ISSUE]: 'geo_type' value hasn't been updated when setting geometry value(s)! Match 'Closest to' requires 'mesh' or 'nurbsSurface' type", noContext=True )
        # Check variables
    if self.ui_data[0]['mirror_space'] is not None and not cmds.objExists( self.ui_data[0]['mirror_space'] ):
        cmds.error( f"[ISSUE]: Mirror space object '{self.ui_data[0]['mirror_space']}' not found!", noContext=True )
    if targets is None:
        return None
    
    targets_mirror = []
    uvpin = self.ui_data[0]['uvpin']
    uv_tfmtx = None
    uv_closestPoint = None
    co_idx = None
    mirror_axis = ('X','Y','Z')
    mirror_axis = mirror_axis[self.ui_data[0]['mirror_axis']]
    #Prepare UV system
    if from_ui:
        co_idx = self.ui_data[0]['start_idx']
        coordinates = cmds.getAttr( f"{self.ui_data[0]['uvpin']}.coordinate", multiIndices=True )
        #Check if new coordinates will overwrite existing indexes starting from start_idx
        if coordinates is not None:
            coordinates = tuple( coordinates )
            warn_overwrite = False
            if co_idx in coordinates: #If directly in existing coordinates
                warn_overwrite = True
            elif co_idx < coordinates[-1]: #If inbetween existing coordinates
                i = co_idx
                max_i = co_idx + len( targets )
                while i < max_i:
                    if i in coordinates:
                        warn_overwrite = True
                        break
                    i+=1
            if warn_overwrite:
                confirm_result = cmds.confirmDialog(
                    title="Mirror index overwrite",
                    message=f"Mirror objects will overwrite existing coordinate\nindexes if starting at start index '{co_idx}'!\n\nStart after last existing index instead ?",
                    button=["Yes","No","Cancel"], defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                )
                if confirm_result == "Cancel":
                    cmds.inViewMessage( message=f"<font color={self.THEME['cancel_txt']}>Mirror cancelled!</font color>", position="botCenter", fade=True, fadeOutTime=300 )
                    print( "[INFO]: Mirror cancelled!" )
                    return
                elif confirm_result == "Yes": #Increment last existing index
                    co_idx = coordinates[-1] + 1
                    _Set_Start_Idx( self_idx, None, True, co_idx )
        
        is_mesh = True if self.ui_data[0]['geo_type'] == 'mesh' else False
        uv_tfmtx = cmds.createNode( 'translationFromMatrix', skipSelect=True )
        uv_closestPoint = 'closestPointOnMesh' if is_mesh else 'closestPointOnSurface'
        uv_closestPoint = cmds.createNode( uv_closestPoint, skipSelect=True )
        cmds.connectAttr( f'{uv_tfmtx}.output', f"{uv_closestPoint}.inPosition" )
        cmds.connectAttr( self.ui_data[0]['geo_defo'], f"{uv_closestPoint}.{'inMesh' if is_mesh else 'inputSurface'}" )
        if is_mesh:
            cmds.connectAttr( f"{_Split_NodeAttr( self.ui_data[0]['geo_orig'] )}.worldMatrix[0]", f'{uv_closestPoint}.inputMatrix' )
    else: #Extract UV system variables
        uv_tfmtx = uv_system[0]
        uv_closestPoint = uv_system[1]
        co_idx = uv_system[2]
    space_obj_offset = cmds.createNode( 'transform', name="UVPin_Global_Temp_space_offset", skipSelect=True )
    space_obj = cmds.createNode( 'transform', name="UVPin_Global_Temp_space", parent=space_obj_offset, skipSelect=True )
    ref_obj = cmds.createNode( 'transform', name=f"UVPin_Global_Temp_ref", parent=space_obj, skipSelect=True )
    ref_get_child = False if (self.ui_data[0]['mirror_bhv'] == 2 or self.ui_data[0]['mirror_bhv'] == 4) else True
    cmds.connectAttr( f'{ref_obj}.worldMatrix[0]', f'{uv_tfmtx}.input', force=True )
    #Prepare UV system
    
    #Actually mirror
    space_obj_wm = None
    if self.ui_data[0]['mirror_space'] is not None: #Object space
        space_obj_wm = cmds.getAttr( self.ui_data[0]['mirror_space'] )
        cmds.xform( space_obj_offset, matrix=space_obj_wm )
    space_obj_wm = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)

    do_rename = True if self.ui_data[0]['mirror_name_type'] != 1 and self.ui_data[0]['mirror_name_source'] != "" and self.ui_data[0]['mirror_name_target'] != "" else False
    for target in targets:
        #Reset space_obj
        cmds.xform( space_obj, matrix=space_obj_wm )
        # Get mirror position
        if ref_get_child:
            cmds.matchTransform( ref_obj, cmds.listRelatives( target, children=True, fullPath=True, shapes=False )[0], position=True, rotation=True, scale=True )
        else:
            cmds.matchTransform( ref_obj, target, position=True, rotation=True, scale=True )
        cmds.setAttr( f'{space_obj}.scale{mirror_axis}', -1 )
        # Get mirror UV position and create coordinate
        cmds.setAttr( f'{uvpin}.coordinate[{co_idx}]', cmds.getAttr( f'{uv_closestPoint}.parameterU' ), cmds.getAttr( f'{uv_closestPoint}.parameterV' ) )
        
        # Create mirror object
        target_mirror = cmds.duplicate( target, renameChildren=True )[0]
        target_mirror_orig = f'{target_mirror}'
        offset = None
        if self.ui_data[0]['mirror_bhv'] == 3: #Mirror behavior offset
            
            if self.ui_data[0]['mirror_offmtd'] == 1 or self.ui_data[0]['mirror_offmtd'] == 2:
                #Parent/Object geo origin - Scale
                
                _Clear_OffsetParentMatrix( target_mirror )
                if cmds.nodeType( target_mirror ) == 'joint':
                    _Clear_Transform( target_mirror, ('jointOrient',) )
                else:
                    _Clear_Transform( target_mirror )
                
                if self.ui_data[0]['mirror_offmtd'] == 1: # Create parent
                    offset = _Create_Parent( target_mirror, True )
                else:
                    offset = target_mirror
                
                cmds.connectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{offset}.offsetParentMatrix' )
                cmds.matchTransform( offset, space_obj, position=True, rotation=True )
                cmds.matchTransform( target_mirror, target, position=True, rotation=True, scale=True )
                # Scale offset
                cmds.setAttr( f'{offset}.scale{mirror_axis}', self.ui_data[0]['mirror_direction'] )
                # Done
                if self.ui_data[0]['mirror_offmtd'] != 1: #Set offset back to None if wasn't created to not be renamed twice
                    offset = None
            elif self.ui_data[0]['mirror_offmtd'] == 4 or self.ui_data[0]['mirror_offmtd'] == 5:
                # Parent/Object - Rot/Scale
                
                _Clear_OffsetParentMatrix( target_mirror )
                if cmds.nodeType( target_mirror ) == 'joint':
                    _Clear_Transform( target_mirror, ('jointOrient',) )
                else:
                    _Clear_Transform( target_mirror )

                if self.ui_data[0]['mirror_offmtd'] == 4: # Create parent
                    offset = _Create_Parent( target_mirror, True )
                else:
                    offset = target_mirror
                cmds.connectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{offset}.offsetParentMatrix', force=True )
                
                cmds.setAttr( f'{space_obj}.scale', 1, 1, 1 )
                cmds.matchTransform( ref_obj, target, position=True, rotation=True, scale=True )
                if mirror_axis == 'X':
                    cmds.setAttr( f'{space_obj}.rotateY', 180 )
                    cmds.setAttr( f'{space_obj}.scaleZ', -1 )
                elif mirror_axis == 'Y':
                    cmds.setAttr( f'{space_obj}.rotateZ', 180 )
                    cmds.setAttr( f'{space_obj}.scaleX', -1 )
                elif mirror_axis == 'Z':
                    cmds.setAttr( f'{space_obj}.rotateY', 180 )
                    cmds.setAttr( f'{space_obj}.scaleX', -1 )
                cmds.matchTransform( offset, ref_obj )
                
                target_scale = cmds.getAttr( f'{target}.scale' )[0]
                target_scale = [target_scale[0], target_scale[1], target_scale[2]] #Manually convert to a list as sometimes it refuses to convert tuple into list
                i = 0
                for c_axis in target_scale:
                    target_scale[i] = c_axis * -1
                    i+=1
                cmds.setAttr( f'{offset}.scale', *target_scale )
                # Done
                if self.ui_data[0]['mirror_offmtd'] != 4: #Set offset back to None if wasn't created to not be renamed twice
                    offset = None
        else:
            #Mirror position and eventually align axes
            cmds.connectAttr( f'{uvpin}.outputMatrix[{co_idx}]', f'{target_mirror}.offsetParentMatrix' )
            
            if self.ui_data[0]['mirror_bhv'] == 2:
                # Align axes
                cmds.matchTransform( target_mirror, ref_obj, position=True, rotation=True )
            else:
                # No extra axis alignement
                if cmds.nodeType( target_mirror ) == 'joint':
                    _Clear_Transform( target_mirror, ('jointOrient',) )
                else:
                    _Clear_Transform( target_mirror )
                cmds.matchTransform( target_mirror, ref_obj, position=True )
                cmds.matchTransform( target_mirror, target, rotation=True )
        
        #Rename
        if do_rename:
            new_name = None
            if self.ui_data[0]['mirror_name_type'] == 2:
                #Prefix
                # Root
                if target_mirror.startswith( self.ui_data[0]['mirror_name_source'] ):
                    new_name = _Remove_Dupli_Suffix( target_mirror, target )
                    target_mirror = cmds.rename( target_mirror, f"{self.ui_data[0]['mirror_name_target']}{new_name.removeprefix(self.ui_data[0]['mirror_name_source'])}" )
                    
                    # Offset
                    if offset is not None:
                        new_name = _Remove_Dupli_Suffix( offset.removesuffix('_orig'), target )
                        offset = cmds.rename( offset, f"{self.ui_data[0]['mirror_name_target']}{new_name.removeprefix(self.ui_data[0]['mirror_name_source'])}_orig" )
                
                # Children
                target_children = cmds.listRelatives( target, allDescendents=True, fullPath=True )
                target_mirror_children = cmds.listRelatives( target_mirror, allDescendents=True, fullPath=True )
                i = 0
                for child in target_mirror_children:
                    child_path = _Split_FullPath( _Remove_Dupli_Suffix( child, target_children[i] ) )
                    
                    if child_path[1].startswith( self.ui_data[0]['mirror_name_source'] ):
                        cmds.rename( child, f"{self.ui_data[0]['mirror_name_target']}{child_path[1].removeprefix(self.ui_data[0]['mirror_name_source'])}" )
                    i+=1
            elif self.ui_data[0]['mirror_name_type'] == 3:
                #Suffix
                # Root
                new_name = _Remove_Dupli_Suffix( target_mirror, target )
                if new_name.endswith( self.ui_data[0]['mirror_name_source'] ):
                    target_mirror = cmds.rename( target_mirror, f"{new_name.removesuffix(self.ui_data[0]['mirror_name_source'])}{self.ui_data[0]['mirror_name_target']}" )
                    
                    # Offset
                    if offset is not None:
                        new_name = _Remove_Dupli_Suffix( offset.removesuffix('_orig'), target )
                        if new_name.endswith( self.ui_data[0]['mirror_name_source'] ):
                            offset = cmds.rename( offset, f"{new_name.removesuffix(self.ui_data[0]['mirror_name_source'])}{self.ui_data[0]['mirror_name_target']}_orig" )
                
                # Children
                target_children = cmds.listRelatives( target, allDescendents=True, fullPath=True )
                target_mirror_children = cmds.listRelatives( target_mirror, allDescendents=True, fullPath=True )
                i = 0
                for child in target_mirror_children:
                    child_path = _Split_FullPath( _Remove_Dupli_Suffix( child, target_children[i] ) )

                    if child_path[1].endswith( self.ui_data[0]['mirror_name_source'] ):
                        cmds.rename( child, f"{child_path[1].removesuffix(self.ui_data[0]['mirror_name_source'])}{self.ui_data[0]['mirror_name_target']}" )
                    i+=1
            elif self.ui_data[0]['mirror_name_type'] == 4:
                #First
                # Root
                if self.ui_data[0]['mirror_name_source'] in target_mirror:
                    new_name = _Remove_Dupli_Suffix( target_mirror, target )
                    target_mirror = cmds.rename( target_mirror, new_name.replace(self.ui_data[0]['mirror_name_source'], self.ui_data[0]['mirror_name_target'], 1) )
                    
                    # Offset
                    if offset is not None:
                        new_name = _Remove_Dupli_Suffix( offset.removesuffix('_orig'), target ) + '_orig'
                        offset = cmds.rename( offset, new_name.replace(self.ui_data[0]['mirror_name_source'], self.ui_data[0]['mirror_name_target'], 1) )
                
                # Children
                target_children = cmds.listRelatives( target, allDescendents=True, fullPath=True )
                target_mirror_children = cmds.listRelatives( target_mirror, allDescendents=True, fullPath=True )
                i = 0
                for child in target_mirror_children:
                    child_path = _Split_FullPath( _Remove_Dupli_Suffix( child, target_children[i] ) )

                    if self.ui_data[0]['mirror_name_source'] in child_path[1]:
                        cmds.rename( child, child_path[1].replace( self.ui_data[0]['mirror_name_source'], self.ui_data[0]['mirror_name_target'], 1 ) )
                    i+=1
            elif self.ui_data[0]['mirror_name_type'] == 5:
                #Last
                # Root
                if self.ui_data[0]['mirror_name_source'] in target_mirror:
                    new_name = _Remove_Dupli_Suffix( target_mirror, target ).rsplit(self.ui_data[0]['mirror_name_source'],1)
                    target_mirror = cmds.rename( target_mirror, f"{new_name[0]}{self.ui_data[0]['mirror_name_target']}{new_name[1]}" )
                    
                    # Offset
                    if offset is not None:
                        new_name = offset.removesuffix('_orig')
                        if self.ui_data[0]['mirror_name_source'] in new_name:
                            new_name = _Remove_Dupli_Suffix( new_name, target ).rsplit(self.ui_data[0]['mirror_name_source'],1)
                            offset = cmds.rename( offset, f"{new_name[0]}{self.ui_data[0]['mirror_name_target']}{new_name[1]}_orig" )
                
                # Children
                target_children = cmds.listRelatives( target, allDescendents=True, fullPath=True )
                target_mirror_children = cmds.listRelatives( target_mirror, allDescendents=True, fullPath=True )
                i = 0
                for child in target_mirror_children:
                    child_path = _Split_FullPath( _Remove_Dupli_Suffix( child, target_children[i] ) )

                    if self.ui_data[0]['mirror_name_source'] in child_path[1]:
                        child_path_temp = child_path[1].rsplit( self.ui_data[0]['mirror_name_source'], 1 )
                        if len(child_path_temp) == 1:
                            cmds.rename( child, f"{child_path_temp[0]}{self.ui_data[0]['mirror_name_target']}" )
                        else:
                            cmds.rename( child, f"{child_path_temp[0]}{self.ui_data[0]['mirror_name_target']}{child_path_temp[1]}" )
                    i+=1
            elif self.ui_data[0]['mirror_name_type'] == 6:
                #All
                # Root
                if self.ui_data[0]['mirror_name_source'] in target_mirror:
                    new_name = _Remove_Dupli_Suffix( target_mirror, target )
                    target_mirror = cmds.rename( target_mirror, new_name.replace(self.ui_data[0]['mirror_name_source'], self.ui_data[0]['mirror_name_target']) )
                    
                    # Offset
                    if offset is not None:
                        new_name = offset.removesuffix('_orig')
                        if self.ui_data[0]['mirror_name_source'] in new_name:
                            new_name = _Remove_Dupli_Suffix( new_name, target ) + '_orig'
                            offset = cmds.rename( offset, new_name.replace(self.ui_data[0]['mirror_name_source'], self.ui_data[0]['mirror_name_target']) )
                
                # Children
                target_children = cmds.listRelatives( target, allDescendents=True, fullPath=True )
                target_mirror_children = cmds.listRelatives( target_mirror, allDescendents=True, fullPath=True )
                i = 0
                for child in target_mirror_children:
                    child_path = _Split_FullPath( _Remove_Dupli_Suffix( child, target_children[i] ) )

                    if self.ui_data[0]['mirror_name_source'] in child_path[1]:
                        cmds.rename( child, child_path[1].replace( self.ui_data[0]['mirror_name_source'], self.ui_data[0]['mirror_name_target'] ) )
                    i+=1
        targets_mirror.append( target_mirror )
        co_idx+=1
    
    #Delete UV system
    cmds.delete( ref_obj, uv_tfmtx, uv_closestPoint, space_obj_offset, space_obj )

    if from_ui:
        cmds.select( targets_mirror )
        _Update_Start_Idx( self_idx, uvpin ) #Update start_idx
    return ( *targets, *targets_mirror )
#endregion - ** Tab Create **

#region - ** Tab Display **
# uvPin
def _Clear_ScrollArea( self ): #Clear scroll area children items
    """ Clear scroll area children items """
    if 'uvAttrFields' not in self.ui_items[1]:
        self.ui_items[1]['uvAttrFields'] = {}
    
    scrollLyt = self.ui_items[1]['scrollLyt']
    ui_items = cmds.scrollLayout( scrollLyt, query=True, childArray=True )
    if ui_items == None:
        return
    self.ui_items[1]['uvAttrFields'].clear()
    for ui_item in ui_items:
        path = cmds.layout( ui_item, query=True, fullPathName=True )
        cmds.deleteUI( path, layout=True )

def _Get_InOutputs( node:str, attr_base:str, attr_list:list, get_destination:bool ): #Get input or output plug connections from asked attributes on node
    """ Get input or output plug connections from asked attributes on node """
    i = 0
    for attr in attr_list:
        attr_info = cmds.connectionInfo( f'{node}.{attr_base}{attr}', destinationFromSource=True ) if get_destination else cmds.connectionInfo( f'{node}.{attr_base}{attr}', sourceFromDestination=True ) #Get connections
        if get_destination:
            attr_info = sorted( attr_info, key=lambda k: k.lower() )
        else: #If destinationFromSource, move string inside list
            attr_info = [ attr_info ]
        
        plugs = ''
        for plug in attr_info: #Transform list into formatted string
            plugs = f"{plugs}, '{plug}'" if plugs != '' else f"'{plug}'"
        plugs = f"[ {plugs} ]"
        plugs = 'None' if plugs == '[  ]' else plugs
        attr_list[i] = plugs
        i+=1
    return attr_list

def _Build_OutputsUI( self, idx:int, connections:list, parent:str, node:str ): #Build UI elements for a coordinate's output infos
    """ Build UI elements for a coordinate's output infos """
    ui_info = (f"Coordinate[{idx}]'s ", " connected to: ")
    items = (('outputMatrix',), ('outputTranslate','sep','outputTranslateX','outputTranslateY','outputTranslateZ'))
    ui_clmns = (5, 5)
    ui_widths = (398, 120, 89, 89, 89)
    outUIs = self.ui_items[1]['outUIs'][idx] = []
    i = 0
    i2 = 0
    for item in items:
        c_rowLyt = cmds.rowLayout(
            height=27, width=400,
            numberOfColumns=ui_clmns[i],
            parent=parent
        )
        for subitem in item:
            if subitem == 'sep':
                cmds.separator( height=1, width=3, style='none', backgroundColor=self.THEME['disp']['uvp_out_sep'], parent=c_rowLyt )
                continue
            lineback = '\n'
            info_anno = f"{ui_info[0]}{subitem}{ui_info[1]}\n\n{connections[i2].replace(', ', lineback).replace('[ ','').replace(' ]','')}"
            info_status = f"{ui_info[0]}{subitem}{ui_info[1]}{connections[i2]}"
            background = self.THEME['disp']['uvp_out_None_back'] if connections[i2] == 'None' else self.THEME['disp']['uvp_out_Connected_back']
            txtCtrl = cmds.textField(
                height=25, width=ui_widths[i2],
                editable=False, text=connections[i2],
                annotation=info_anno, statusBarMessage=info_status,
                backgroundColor=background,
                parent=c_rowLyt
            )
            if connections[i2] != 'None': #If has connections, build right-click menu UI
                coAndNode = f"{connections[i2][:2]}'{node}', {connections[i2][2:]}" #List with node and connections for selection
                fullCo = f"{subitem}[{idx}]" if i == 0 else f"{f'{subitem}[{idx}]' if i2 < 2 else f'outputTranslate[{idx}].{subitem}'}" #Full node output attribute rebuilt
                coPlural = '' if ',' not in connections[i2] else 's'
                pops = (
                    ("div_Select",),
                    (f"Select connection{coPlural}", f'cmds.select({connections[i2]}, replace=True)'),
                    (f"Select connection{coPlural} and uvPin node", f'cmds.select({coAndNode}, replace=True)'),
                    ("div_Manage",),
                    (f"Break connection{coPlural}", partial(_Break_Connections, None, self.SELF_IDX, f'{node}.{fullCo}', connections[i2], f'{txtCtrl}', idx, i2))
                )
                pop = _Build_PopupUI( txtCtrl, pops, True )
                outUIs.append(pop)
            else:
                outUIs.append(None)
            i2+=1
        i=1

def _Check_CoordinateChange( self, self_idx:int, uvpin:str, init=False ): #Compact every coordinate indexes into a list and return if has index changes with last stored value
    """
    Compact every coordinate indexes into a list and return if has index changes with last stored value\n
    ### Parameters:\n
    'uvpin' (str): uvPin node name\n
    'init' (bool): Only store value\n
    """
    if self is None:
        self = _Get_Instance( self_idx )
    
    coordinates = cmds.getAttr( f'{uvpin}.coordinate', multiIndices=True )
    if coordinates is None:
        return False
    coordinates_len = len(coordinates)

    compact_list = []
    last_co = coordinates[-1]
    item_idx = 0
    while item_idx < coordinates_len:
        start_co = coordinates[item_idx]
        is_last = True if start_co == last_co else False
        
        if not is_last: #Is not last
            continuous_value = start_co+1
            increment_count = 0
            last_co = None
            for next_co in coordinates[item_idx+1:]:
                if next_co != continuous_value: #If next coordinate index doesn't match increment
                    break
                continuous_value+=1
                increment_count+=1
                last_co = next_co
            
            if increment_count == 0:
                compact_list.append( start_co )
            else:
                compact_list.append( (start_co,last_co) )
            item_idx+=increment_count
        else: #Is last
            compact_list.append( start_co )
        item_idx+=1
    
    if init: #Only store value
        self.ui_data[1]['compact_idx'] = compact_list
    else: #Check if has changed, if so store new value, and return changed state
        has_changed = False
        if compact_list != self.ui_data[1]['compact_idx']:
            has_changed = True
            self.ui_data[1]['compact_idx'] = compact_list
        return has_changed

def _Build_UVPUI( self, node:str, skip_checks=False, get_from_self=False ): #Get uvPin's data and generate UI items under scroll area
    """ Get uvPin's data and generate UI items under scroll area """
    if not skip_checks:
        if not cmds.objExists( node ):
            cmds.error( f"[ISSUE]: Couldn't find node '{node}'!", noContext=True )
        if not cmds.objectType( node, isType='uvPin' ):
            cmds.error( f"[ISSUE]: '{node}' isn't an uvPin!", noContext=True )
    
    if get_from_self:
        node = self.ui_data[1]['uvpin']
    if self.ui_data[1]['uvpin'] != node or get_from_self:
        if not get_from_self:
            self.ui_data[1]['uvpin'] = node
        txt_node = node if len(node) < 51 else f"{node[:24]}...{node[-24:]}"
        cmds.text(
            self.ui_items[1]['node_txtCtrl'], edit=True, label=f"<font size=7>UVPIN: <i><font color={self.THEME['disp']['tb_uvpName_Found']}>{txt_node}</font>",
            annotation=f"uvPin node: '{node}'\n\n[Middle mouse]: Select node", statusBarMessage=f"uvPin node: '{node}'    [Middle mouse]: Select node  ",
            dragCallback=partial(_Select_Callback, self.SELF_IDX, 10)
        )
    self.ui_items[1]['outUIs'] = {}

    coordinates = None
    try:
        coordinates = cmds.getAttr( f'{node}.coordinate[*]' )
    except ValueError: #If uvPin has no coordinates
        cmds.warning( f"[ISSUE]: No coordinate item found on uvPin '{node}' !", noContext=True )
        _Clear_ScrollArea( self )
        self.ui_data[1]['page_current'] = 1
        self.ui_data[1]['page_count'] = 1
        self.ui_data[1]['item_count'] = 0
        cmds.intField( self.ui_items[1]['cPage_intFld'], edit=True, value=1 )
        cmds.text( self.ui_items[1]['pCount_txtCtrl'], edit=True, label="1" )
        cmds.text( self.ui_items[1]['inCount_txtCtrl'], edit=True, label="(0 total input)" )
        return
    coo_len = len( coordinates )
    max_count = self.ui_data[1]['item_per_page']
    page_count = math.ceil( coo_len / max_count ) #Round up division
    page_current = self.ui_data[1]['page_current']
    if page_current > page_count: #Clamp back to max page count
        page_current = page_count
    
    self.ui_data[1]['page_current'] = page_current
    self.ui_data[1]['page_count'] = page_count
    cmds.intField( self.ui_items[1]['cPage_intFld'], edit=True, value=page_current )
    cmds.text( self.ui_items[1]['pCount_txtCtrl'], edit=True, label=page_count )
    if self.ui_data[1]['item_count'] != coo_len:
        self.ui_data[1]['item_count'] = coo_len
        cmds.text( self.ui_items[1]['inCount_txtCtrl'], edit=True, label=f"({coo_len} total {'input' if coo_len < 2 else 'inputs'})" )
    
    added_item_count = 0
    starting_item_listidx = ((page_current -1) * max_count)
    item_max = (page_current * max_count) if coo_len >= (page_current * max_count) else coo_len+1
    valid_idx = cmds.getAttr( f'{node}.coordinate', multiIndices=True )[:item_max]
    if starting_item_listidx != 0:
        valid_idx = valid_idx[starting_item_listidx:]
    last_valid_idx = valid_idx[-1]

    _Clear_ScrollArea( self ) #Clear scroll area
    while added_item_count < item_max:
        #Get current existing coordinate idx
        i = valid_idx[0]
        valid_idx.remove(i)
        #Data
        c_name = f"Coordinate[{i}]"
        #uv = coordinates[i]
        #inputs = _Get_InOutputs( node, f'coordinate[{i}].coordinate', ['U','V'], False )
        outputs = _Get_InOutputs( node, 'output', [f'Matrix[{i}]',f'Translate[{i}]',f'Translate[{i}].outputTranslateX',f'Translate[{i}].outputTranslateY',f'Translate[{i}].outputTranslateZ'], True )

        #region - UI
        c_area_rowLyt = cmds.rowLayout(
            height=60,
            numberOfColumns=10,
            backgroundColor=self.THEME['disp']['uvp_back'],
            parent=self.ui_items[1]['scrollLyt']
        )
        cmds.separator( height=25, width=1, style='none', parent=c_area_rowLyt )
        cmds.symbolButton(
            height=25, width=25,
            image='smallTrash.png', command=partial(_Remove_Coordinate, None, self.SELF_IDX, node, i, False), dragCallback=partial(_Remove_Coordinate_Callback, self.SELF_IDX, node, i),
            annotation="Delete coordinate (as in Maya's UI)\n\n[Middle mouse]: Delete coordinate by shifting next coordinate(s)\none index lower instead of leaving an unused index",
            statusBarMessage="Delete coordinate    [Middle mouse]: Delete coordinate by shifting next coordinate(s) one index lower instead of leaving an unused index",
            backgroundColor=self.THEME['disp']['uvp_delete_back'],
            parent=c_area_rowLyt
        )
        cmds.separator( height=25, width=6, style='none', parent=c_area_rowLyt )
        co_TxtCtrl = cmds.text(
            height=25, width=150,
            label=c_name, align='right',
            annotation="Right-click for options", statusBarMessage="Right-click for options",
            backgroundColor=self.THEME['disp']['uvp_name_back'],
            parent=c_area_rowLyt
        )
        _Build_PopupUI( co_TxtCtrl, (
            ("div_Info",),
            ("Print UV values", partial(_Print_UV, f'{node}.coordinate[{i}].coordinate')),
            ("Print outputTransform values", partial(_Print_OutTrnsl, f'{node}.outputTranslate[{i}]')),
            ("Print outputMatrix value", partial(_Print_OutMtx, f'{node}.outputMatrix[{i}]'))
        ) )
        cmds.separator( height=25, width=1, style='none', parent=c_area_rowLyt )
        uv_fieldsClmnLyt = cmds.columnLayout(
            height=25, width=166,
            columnAttach=('left',-142),
            parent=c_area_rowLyt
        )
        uv_attrFields = cmds.attrFieldGrp(
            height=25,
            label="", columnAttach2=['left','left'],
            attribute=f'{node}.coordinate[{i}]', precision=3, numberOfFields=2,
            annotation="coordinateU and coordinateV value fields (Decimal visibility limited to three)", statusBarMessage="coordinateU and coordinateV value fields (Decimal visibility limited to three)",
            parent=uv_fieldsClmnLyt
        )
        self.ui_items[1]['uvAttrFields'][i] = uv_attrFields
        cmds.separator( height=25, width=4, style='none', parent=c_area_rowLyt )
        cmds.separator( height=25, width=2, style='none', backgroundColor=self.THEME['disp']['uvp_sep_back'], parent=c_area_rowLyt )
        cmds.separator( height=25, width=3, style='none', parent=c_area_rowLyt )
        c_out_flowLayout = cmds.flowLayout(
            height=55, width=400,
            vertical=True, wrap=False,
            backgroundColor=self.THEME['disp']['uvp_out_back'],
            parent=c_area_rowLyt
        )
        _Build_OutputsUI( self, i, outputs, c_out_flowLayout, node ) #Create outputs layout and fields
        #endregion - UI
        
        if i == last_valid_idx: #If was last existing idx, stop
            break
        added_item_count+=1
    _Check_CoordinateChange( self, self.SELF_IDX, node, True ) #Store compact indexes to later check changes not matching when UI was last built

def _Pick_UVPIN_Done_DISP( self_idx, skip_check=False ): #End function for uvPin pick
    """ End function for uvPin pick """
    self_idx = int(self_idx)
    self = _Get_Instance( self_idx )
    if self.callback_hook is not None: #Prevent function called twice
        self.callback_hook = None
    else:
        return
    
    if skip_check or (self.pick_sel != [] and self.pick_sel != None):
        sel = self.pick_sel[-1]
        
        self.ui_data[1]['uvpin'] = sel
        _Build_UVPUI( self, sel, True, True )
    self.pick_sel = None
    self.pick_selData = None
    self.pick_ui = None

# Options
def _Print_UV( attr:str, partial_empty=None ): #Print UV values from called coordinate attribute
    """ Print UV values from called coordinate attribute """
    u = cmds.getAttr( f'{attr}U' )
    v = cmds.getAttr( f'{attr}V' )
    print( f"\n[INFO]: Exact UV values for '{attr.rsplit('.',1)[0]}':\n U: {u}\n V: {v}" )

def _Print_OutTrnsl( attr:str, partial_empty=None ): #Print outputTranslate values from called coordinate attribute
    """ Print outputTranslate values from called coordinate attribute """
    out_trnsl = cmds.getAttr( attr )[0]
    print( f"\n[INFO]: outputTranslate values for '{attr.rsplit('.',1)[0]}.coordinate{attr[-3:]}':\n X: {out_trnsl[0]}\n Y: {out_trnsl[1]}\n Z: {out_trnsl[2]}" )

def _Print_OutMtx( attr:str, partial_empty=None ): #Print outputMatrix values from called coordinate attribute
    """ Print outputMatrix values from called coordinate attribute """
    out_mtx = cmds.getAttr( attr )
    print( f"\n[INFO]: outputMatrix value for '{attr.rsplit('.',1)[0]}.coordinate{attr[-3:]}':\n {out_mtx}" )

def _Remove_Coordinate( self, self_idx, node:str, uvp_idx:int, shift_next=False, partial_empty=None ): #Remove a specific coordinate on the uvPin node (actually shift connections and values unless they are locked)
    """ Remove a specific coordinate on the uvPin node (actually shift connections and values unless they are locked) """
    if self is None:
        self = _Get_Instance( self_idx )

    if _Check_CoordinateChange( self, self_idx, node, False ): #Check if current indexes are still has when UI was built, else warn user
        confirm_result = cmds.confirmDialog(
            title="Delete coordinate",
            message=f"Warning! Coordinate indexes have changed since the UI was built!\n\ncoordinate[{uvp_idx}] may not match anymore",
            button=["Reload page","Continue","Cancel"], defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
        )
        if confirm_result == "Reload page":
            cmds.evalDeferred( partial(_RefreshUI, None, self_idx) )
            return
        elif confirm_result == "Cancel":
            return
    
    if shift_next:
        coordinates = cmds.getAttr( f'{node}.coordinate', multiIndices=True ) #Get every uvp coordinate inputs
        if coordinates is None:
            cmds.error( f"[ISSUE]: No coordinate found on '{node}'", noContext=True )
        #coordinates = cmds.getAttr( f'{node}.coordinate[*]' ) #Get every uvp coordinate inputs
        coordinates_len = len(coordinates)
        if uvp_idx > coordinates_len:
            cmds.error( f"[ISSUE]: Coordinate index {uvp_idx} out of range on '{node}'", noContext=True )
        elif uvp_idx not in coordinates:
            cmds.error( f"[ISSUE]: Coordinate index {uvp_idx} not found on '{node}'", noContext=True )

        coordinates = coordinates[coordinates.index(uvp_idx):] #Remove indexes before the one to remove
        
        co_to_shift = {} #Store higher index connections while checking if none are locked and won't be reconnectable before doing changes
        #Inputs
        in_attrs = ( 'coordinate[<idx>]', 'coordinate[<idx>].coordinateU', 'coordinate[<idx>].coordinateV' )
        for co_idx in coordinates:
            co_to_shift[ co_idx ] = {}
            idx_str = f'{co_idx}'
            for attr in in_attrs:
                attr = attr.replace('<idx>',idx_str)
                attr_path = f'{node}.{attr}'
                if cmds.connectionInfo( attr_path, isLocked=True ): #Check if is locked
                    cmds.error( f"[ISSUE]: '{attr_path}' is locked!", noContext=True )
                plugged_to = cmds.connectionInfo( attr_path, sourceFromDestination=True )
                if plugged_to != '':
                    if cmds.connectionInfo( plugged_to, isLocked=True ): #Check if is locked
                        cmds.error( f"[ISSUE]: Source '{plugged_to}' for '{attr}' is locked!", noContext=True )
                else:
                    plugged_to = 'None'
                co_to_shift[ co_idx ][ attr ] = plugged_to
        #Outputs
        out_attrs = ( 'outputMatrix[<idx>]', 'outputTranslate[<idx>]', 'outputTranslate[<idx>].outputTranslateX', 'outputTranslate[<idx>].outputTranslateY', 'outputTranslate[<idx>].outputTranslateZ' )
        for co_idx in coordinates:
            idx_str = f'{co_idx}'
            for attr in out_attrs:
                attr = attr.replace('<idx>',idx_str)
                attr_path = f'{node}.{attr}'
                if cmds.connectionInfo( attr_path, isLocked=True ): #Check if is locked
                    cmds.error( f"[ISSUE]: '{attr_path}' is locked!", noContext=True )
                plugged_to = cmds.connectionInfo( attr_path, destinationFromSource=True )
                if plugged_to != []:
                    for dest in plugged_to:
                        if cmds.connectionInfo( dest, isLocked=True ): #Check if is locked
                            cmds.error( f"[ISSUE]: Destination '{dest}' for '{attr}' is locked!", noContext=True )
                else:
                    plugged_to = 'None'
                co_to_shift[ co_idx ][ attr ] = plugged_to
        
        #Apply idx shift
        matrix_zero = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)
        first = True
        last_co = coordinates[-1]
        co_item_idx = 0
        for co_item in co_to_shift.items(): #For each coordintates starting be the one to remove
            co_idx = co_item[0]
            new_idx = co_idx-1
            is_last = True if co_idx == last_co else False

            old_values = [] #Store non-connected input values as any connection or disconnection from one of the UV plug will reset to zero the other
            if not first:
                for old_co in co_item[1]:
                    if old_co.endswith('U') or old_co.endswith('V'): #Subattributes U/V that contains values
                        old_values.append( cmds.getAttr( f'{node}.{old_co}' ) )

            attr_idx = 0
            for old_co in co_item[1]: #For each connection in inputs and ouputs
                new_co = old_co.replace( f'[{co_idx}]', f'[{new_idx}]' )
                target_co = co_item[1][old_co]
                old_co_path = f'{node}.{old_co}'
                new_co_path = f'{node}.{new_co}'

                if target_co == 'None':
                    target_co = None
                
                if attr_idx < 3: #Inputs
                    has_value = True if (old_co.endswith('U') or old_co.endswith('V')) else False
                    if target_co != None: #Was connected
                        if not first: #To shift, connect from old_idx to new_idx
                            cmds.connectAttr( target_co, new_co_path, force=True )
                        if cmds.isConnected( target_co, old_co_path ): #If is still connected, disconnect
                            cmds.disconnectAttr( target_co, old_co_path )
                            if not is_last and has_value: #Set old intput to -1 so the coordinate's multi intput doesn't disappear
                                cmds.setAttr( old_co_path, -1 )
                    elif not first: #Later than first, set lower idx's values to current old values
                        if old_co.endswith('U'):
                            cmds.setAttr( new_co_path, old_values[0] )
                        elif old_co.endswith('V'):
                            cmds.setAttr( new_co_path, old_values[1] )
                        if is_last and has_value:
                            cmds.setAttr( old_co_path, 0 )
                else: #Outputs
                    if target_co != None: #Was connected
                        for c_target in target_co:
                            if not first: #Replace connection with old_idx to new_idx
                                cmds.connectAttr( new_co_path, c_target, force=True )
                            if cmds.isConnected( old_co_path, c_target ): #If is still connected, disconnect
                                cmds.disconnectAttr( old_co_path, c_target )
                                if first: #Set something back to target attr so it's multi input doesn't disappear
                                    if 'Translate' in old_co and '.' in old_co:
                                        cmds.setAttr( c_target, 0 )
                                    elif 'Matrix' in old_co:
                                        cmds.setAttr( c_target, matrix_zero, type="matrix" )
                attr_idx+=1
            if first:
                first = False
            if not is_last and coordinates[co_item_idx+1] != co_idx+1: #If next coordinate index isn't continous with this one, remove this coordinate index as it won't be overwritten
                cmds.removeMultiInstance( f'{node}.coordinate[{co_idx}]', b=True )
            co_item_idx+=1
        cmds.removeMultiInstance( f'{node}.coordinate[{last_co}]', b=True ) #Remove last index on coordinates
    else: #Only delete the specific index, as Maya's delete button on uvPin attribute editor tab
        #Disconnect idx's output attrs if they are connected and none are locked
        out_attrs = [ 'outputMatrix[<idx>]', 'outputTranslate[<idx>]', 'outputTranslate[<idx>].outputTranslateX', 'outputTranslate[<idx>].outputTranslateY', 'outputTranslate[<idx>].outputTranslateZ' ]
        uvp_idx_str = f'{uvp_idx}'
        for attr_ in out_attrs: #Check if no attr is locked
            attr = attr_.replace('<idx>', uvp_idx_str)
            if cmds.connectionInfo( f'{node}.{attr}', isLocked=True ):
                cmds.error( f"[ISSUE]: '{node}.{attr}' is locked!", noContext=True )
            plugged_to = cmds.connectionInfo( f'{node}.{attr}', destinationFromSource=True )
            if plugged_to != []:
                for dest in plugged_to:
                    if cmds.connectionInfo( dest, isLocked=True ): #Check if locked
                        cmds.error( f"[ISSUE]: Destination '{dest}' for '{attr}' is locked!", noContext=True )
        for attr_ in out_attrs: #Disconnect
            attr = attr_.replace('<idx>', uvp_idx_str)
            plugged_to = cmds.connectionInfo( f'{node}.{attr}', destinationFromSource=True )
            if plugged_to != []:
                for dest in plugged_to:
                    cmds.disconnectAttr( f'{node}.{attr}', dest )
        cmds.deleteUI( self.ui_items[1]['uvAttrFields'][uvp_idx], control=True ) #Delete coordinate's attribute field group so it doesn't keep the coordinate's index existing
        cmds.removeMultiInstance( f'{node}.coordinate[{uvp_idx}]', b=True )
    #Update UI
    page_current = self.ui_data[1]['page_current']
    _Set_Page( self, self_idx, page_current, True )

def _Remove_Coordinate_Callback( self_idx:int, node:str, uvpidx:int,    drgCllBck_drgCtrl=None, drgCllBck_x=None, drgCllBck_y=None, drgCllBck_mod=None ): #Call remove coordinate
    """ Call remove coordinate """
    cmds.evalDeferred( partial(_Remove_Coordinate, None, self_idx, node, uvpidx, True) ) #Call on deferred to prevent Maya crash

def _Break_Connections( self, self_idx, uvp_attr:str, connections, field_ui, co_idx, field_idx, partial_empty=None ): #Break connection(s) between an uvPin attribute and other attributes
    """ Break connection(s) between an uvPin attribute and other attributes """
    if self is None:
        self = _Get_Instance( self_idx )

    if connections is None:
        return
    else: #Convert connections str to list of each connection
        connections = connections[2:-2].split(', ')
        i = 0
        for co in connections:
            connections[i] = co[1:-1]
            i+=1
    allowed = False
    if self.ui_data[1]['break_co_safety']:
        confirm_result = cmds.confirmDialog(
            title="Confirmation",
            message="Are you sure you want to break connection(s) ?",
            button=["Yes","No"], defaultButton="No", cancelButton="No", dismissString="No"
        )
        if confirm_result == "Yes":
            allowed = True
    else:
        allowed = True
    if allowed:
        if cmds.connectionInfo( uvp_attr, isLocked=True ): #Check if is locked, if so skip directly everything
            cmds.warning( f"[ISSUE]: '{uvp_attr}' is locked!", noContext=True )
            return
        locked_co = False
        last_print_warns = False
        for co in connections:
            if cmds.isConnected( uvp_attr, co ):
                if cmds.connectionInfo( co, isLocked=True ): #Check if is locked, if so skip disconnect
                    cmds.warning( f"[ISSUE]: '{co}' is locked!", noContext=True )
                    locked_co = True
                    last_print_warns = True
                    continue
                cmds.disconnectAttr( uvp_attr, co )
                print( f"[INFO]: Disconnected '{uvp_attr}' and '{co}'" )
                last_print_warns = False
        if locked_co and not last_print_warns: #Warning(s) won't be visible if a print is executed after so make sure to display a warning after all prints to make user aware
            cmds.warning( f"[ISSUE]: Locked attribute(s) can't be disconnected, please open the Script Editor for their history", noContext=True )
        
        #Update UI
        co = cmds.listConnections( uvp_attr, fullNodeName=True ) #To make sure connections are actual
        co_txt = f'{co}'.split('[',1)[1].rsplit(']',1)[0] if co != None else 'None'
        lineback = '\n'
        info_status = cmds.textField( field_ui, query=True, annotation=True )
        info_anno = f"{info_status.split(':',1)[0]}:\n\n{co_txt.replace(', ',lineback)}"
        info_status = f"{info_status.split(':',1)[0]}: [ {co_txt} ]" if co != None else f"{info_status.split(':',1)[0]}: {co_txt}"

        if co is None:
            cmds.textField( field_ui, edit=True, text='None', annotation=info_anno, statusBarMessage=info_status, backgroundColor=self.THEME['disp']['uvp_out_None_back'] )
            #Delete popup menu as no connection options are useful anymore
            popMenu = self.ui_items[1]['outUIs'][co_idx][field_idx]
            cmds.deleteUI( popMenu, menu=True )
            self.ui_items[1]['outUIs'][co_idx][field_idx] = None
        else:
            cmds.textField( field_ui, edit=True, text=f"{co}", annotation=info_anno, statusBarMessage=info_status )

# Page
def _Set_Page( self, self_idx:int, page_value=None, force_refresh=False, partial_empty=None ): #Set current page
    """ Set current page """
    if self is None:
        self = _Get_Instance( self_idx )

    field = self.ui_items[1]['cPage_intFld']
    page_number = page_value if page_value != None else cmds.intField( field, query=True, value=True )
    fixed_page_number = False
    if page_number == self.ui_data[1]['page_current'] and not force_refresh: #Skip if already on this page
        return
    
    if page_number < 1: #Clamp min page
        page_number = 1
        fixed_page_number = True
    elif page_number > self.ui_data[1]['page_count']: #Clamp max page
        page_number = self.ui_data[1]['page_count']
        fixed_page_number = True
    
    if fixed_page_number:
        cmds.intField( field, edit=True, value=page_number )
    self.ui_data[1]['page_current'] = page_number
    if self.ui_data[1]['uvpin'] != None:
        _Build_UVPUI( self, self.ui_data[1]['uvpin'] ) #Rebuild UI

def _Set_PageBttn( self, self_idx:int, up:bool, partial_empty=None ): #Increment or decrement page number
    """ Increment or decrement page number """
    if self is None:
        self = _Get_Instance( self_idx )

    new_page = self.ui_data[1]['page_current']
    new_page = new_page+1 if up else new_page-1
    if new_page < 1 or new_page > self.ui_data[1]['page_count']: #Skip if going to ask for out of range to prevent unecessary UI rebuild
        return
    
    field = self.ui_items[1]['cPage_intFld'] #Update int field value
    cmds.intField( field, edit=True, value=new_page )
    _Set_Page( self, self_idx, new_page ) #Call field's command

def _Set_MaxPerPage( self, self_idx:int, partial_empty=None ): #Set maximum items per page
    """ Set maximum items per page """
    if self is None:
        self = _Get_Instance( self_idx )

    field = self.ui_items[1]['maxPPage_intFld']
    item_pp_Count = cmds.intField( field, query=True, value=True )
    fixed_item_pp_Count = False
    if item_pp_Count == self.ui_data[1]['item_per_page']: #Skip if already on this page
        return
    if item_pp_Count < 1:
        item_pp_Count = 1
        fixed_item_pp_Count = True
    
    if fixed_item_pp_Count:
        cmds.intField( field, edit=True, value=item_pp_Count )
    self.ui_data[1]['item_per_page'] = item_pp_Count
    if self.ui_data[1]['uvpin'] != None:
        _Build_UVPUI( self, self.ui_data[1]['uvpin'] ) #Rebuild UI

def _RefreshUI( self, self_idx, partial_empty=None ): #Refresh UI
    """ Refresh UI """
    if type(self_idx) != int:
        self_idx = int(self_idx)
    if self is None:
        self = _Get_Instance( self_idx )
    
    _Set_Page( self, self_idx, self.ui_data[1]['page_current'], True )

def _Refresh_Callback( self_idx:int, modifiers:int,    drgCllBck_drgCtrl=None, drgCllBck_x=None, drgCllBck_y=None, drgCllBck_mod=None ): #Call window resize
    """ Call window resize """
    if modifiers == 1: #Shift + Middle mouse
        _ResetWidowSize( None, self_idx, 1 )
    elif modifiers == 2: #Ctrl + Middle mouse
        _ResetWidowSize( None, self_idx, 2 )
    elif modifiers == 3: #Ctrl + Shift + Middle mouse
        _ResetWidowSize( None, self_idx, 3 )

def _ResetWidowSize( self, self_idx:int, axis=None ): #Reset window's size to default
    """ Reset window's size to default """
    if self is None:
        self = _Get_Instance( self_idx )

    #Break window's minimum size based on UI inside it, would require to rebuild the window itself and reapply UI changes
    
    if axis == 1: #Change width
        new_size = (self.WIN_SIZE_WH[0], cmds.window(self.WINDOW, query=True, widthHeight=True)[1])
        cmds.window( self.WINDOW, edit=True, widthHeight=new_size )
    elif axis == 2: #Change height
        new_size = (cmds.window(self.WINDOW, query=True, widthHeight=True)[0], self.WIN_SIZE_WH[1])
        cmds.window( self.WINDOW, edit=True, widthHeight=new_size )
    elif axis == 3: #Change both
        cmds.window( self.WINDOW, edit=True, widthHeight=self.WIN_SIZE_WH )
#endregion - ** Tab Display **

#region - * Public *
def Load( multi_windows=True, keep_win_pref=False, tab=1 ): #Load/Create UVPin_Global instance
    """
    Load/Create UVPin_Global instance\n
    ### Parameters:\n
    'multi_windows' (bool): Create a new window instance of the tool\n
    'keep_win_pref' (bool): Keep window preferences as position or size\n
      Note: If multiple windows, each one will have it's own window preferences saved following their incremented name\n
    'tab' (int): Define which tab to show after creating the window ( 1:Create UVPin, 2:Display UVPin )
    """
    if not multi_windows and global_win_count != 0: #If not multi_windows and instance 0 exists, replace it's window closeCommand to prevent executing Close() after creating the new instance object
        _Clear_WindowClose( 0, "[INFO]: Reloading instance index 0" )
    new_instance = UVPin_Global_Window( multi_windows, keep_win_pref, tab )

def Build_Window( self, self_idx:int, tab:int, partial_empty=None ): #Build instance window
    """
    Build instance window\n
    ### Parameters:\n
    'self' (None/UVPin_Global_Window): class object. If None, autofilled with the help of 'self_idx'\n
    'self_idx' (int): class object index in global_win_instances\n
    'tab' (int): Define which tab to show after creating the window ( 1:Create UVPin, 2:Display UVPin )\n
    'partial_empty' (bool): (To ignore) Extra 'False' argument from partial() when function call includes argument(s)
    """
    if self is None:
        self = _Get_Instance( self_idx )
    
    #region - init UI
    #Close old window at same name if exists and reset window pref is asked and exists
    if cmds.window( self.WIN_NAME, exists=True ):
        cmds.deleteUI( self.WIN_NAME, window=True )
    if not self.WIN_KEEP_PREF and cmds.windowPref( self.WIN_NAME, exists=True ):
        cmds.windowPref( self.WIN_NAME, remove=True )
    
    #Create new window
    self.WINDOW = cmds.window(
        self.WIN_NAME,
        title=self.WIN_TITLE,
        widthHeight=self.WIN_SIZE_WH,
        sizeable=self.WIN_SIZEABLE,
        closeCommand=partial(Close, self_idx),
        backgroundColor=self.THEME['main_back']
    )
    #endregion - init UI
    
    main_formLyt = cmds.formLayout()
    main_tabLyt = cmds.tabLayout(
        changeCommand=partial(_Tab_Change, self_idx),
        parent=main_formLyt
    )
    self.ui_items[2] = main_tabLyt

    #region - Tab Create
    crt_formLyt = cmds.formLayout(
        parent=main_tabLyt
    )
    crt_clmnLyt = cmds.columnLayout(
        adjustableColumn=True,
        parent=crt_formLyt
    )
    crt_title1_rowLyt = cmds.rowLayout(
        height=50,
        numberOfColumns=1, columnAttach1='left', columnOffset1=5,
        parent=crt_clmnLyt
    )
    cmds.text(
        height=50,
        label="<font size=7><i><b>CREATE</b></i></font>", align='left',
        parent=crt_title1_rowLyt
    )
    cmds.separator( height=3, style='none', parent=crt_clmnLyt )
    crt_create_clmnLyt = cmds.columnLayout(
        height=570,
        adjustableColumn=True, columnOffset=('left',15),
        backgroundColor=self.THEME['crt']['crt_clmn_back'],
        parent=crt_clmnLyt
    )
    cmds.separator( height=20, style='none', parent=crt_create_clmnLyt )

    #region - UVPin
    #uvPin
    crt_uvp_rowLyt = cmds.rowLayout(
        height=31,
        numberOfColumns=10,
        parent=crt_create_clmnLyt
    )
    cmds.text(
        height=30,
        label="<font size=6>UVPin node</font>", align='left',
        parent=crt_uvp_rowLyt
    )
    cmds.separator( height=30, width=20, style='none', parent=crt_uvp_rowLyt )
    uvpin_value = self.ui_data[0]['uvpin'] if self.ui_data[0]['uvpin'] is not None else 'None'
    self.ui_items[0]['uvp_picker_txtField'], self.ui_items[0]['uvp_picker_symbBttn'] = _Build_PickerBttn(
        crt_uvp_rowLyt, 30,
        (
            200, uvpin_value, True, partial(_Set_UVPIN, None, self_idx, False, None, False),
            "uvPin node\n\nSet the name of an uvPin to select or to create\n\n[Middle mouse]: Select uvPin node",
            "Set the name of an uvPin to select or to create  -  [Middle mouse]: Select uvPin node",
            self.THEME['crt']['main_option_back'],
            partial(_Select_Callback, self_idx, 0)
        ),
        8,
        (
            partial(_Pick_Init, self_idx, 1, _Pick_UVPIN_Done_CRT, 0, 'uvPin', True, True, False),
            "Pick tool for uvPin node\n\nIf none already selected will also look\non the active attribute editor tab\n\n(uvPin)",
            "Pick tool for uvPin node  -  If none already selected will also look on the active attribute editor tab  -  (uvPin)",
            self.THEME['crt']['pick_back_off']
        )
    )
    cmds.separator( height=30, width=5, style='none', parent=crt_uvp_rowLyt )
    #Reload
    cmds.symbolButton(
        height=30, width=30,
        image='CN_refresh', command=partial(_Reload_UVPin, self_idx),
        annotation="Reload uvPin node", statusBarMessage="Reload uvPin node",
        backgroundColor=self.THEME['crt']['pick_back_off'],
        parent=crt_uvp_rowLyt
    )
    cmds.separator( height=30, width=5, style='none', parent=crt_uvp_rowLyt )
    #State
    self.ui_items[0]['uvpin_state_txtCtrl'] = cmds.text(
        height=30,
        label=f"<font size=6>( <font color={self.THEME['crt']['uvpTxt_new']}>New</font color> )</font>",
        annotation="No uvPin node found at this name,\nthe uvPin will be created too", statusBarMessage="No uvPin node found at this name, the uvPin will be created too",
        parent=crt_uvp_rowLyt
    )
    cmds.separator( height=30, width=10, style='none', parent=crt_uvp_rowLyt ) #Side margin
    cmds.separator( height=20, style='none', parent=crt_create_clmnLyt )

    #Geometry
    crt_geo_rowLyt = cmds.rowLayout(
        height=31,
        numberOfColumns=8,
        parent=crt_create_clmnLyt
    )
    self.ui_items[0]['geo_rowLyt'] = crt_geo_rowLyt
    cmds.text(
        height=30,
        label="<font size=6>Geometry</font>", align='left',
        parent=crt_geo_rowLyt
    )
    cmds.separator( height=30, width=10, style='none', parent=crt_geo_rowLyt )
    self.ui_items[0]['geo_picker_txtField'], self.ui_items[0]['geo_picker_symbBttn'] = _Build_PickerBttn( #Picker
        crt_geo_rowLyt, 30,
        (
            150, "None", True, partial(_Set_Geo, self_idx, 0, False, None),
            "uvPin source geometry object\n\nThis field is to automatically set original and deformed geometry fields\nwith start and end deformation shapes found on the object\n[Middle mouse]: Select object",
            "uvPin source geometry object  -  This field is to automatically set original and deformed geometry fields with start and end deformation shapes found on the object  -  [Middle mouse]: Select object",
            self.THEME['crt']['main_option_back'], partial(_Select_Callback, self_idx, 1)
        ),
        3,
        (
            partial(_Pick_Init, self_idx, 1, _Pick_Geo_Done, 1, ('transform','mesh','nurbsSurface'), True, False, False),
            "Pick tool for uvPin source geometry object\n\nThis will automatically set original and deformed geometry fields\nwith start and end deformation shapes found on the object\n\n(transform, mesh or nurbsSurface)",
            "Pick tool for uvPin source geometry  -  This will automatically set original and deformed geometry fields with start and end deformation shapes found on the object  -  (transform, mesh, nurbsSurface)",
            self.THEME['crt']['pick_back_off']
        )
    )
    cmds.separator( height=30, width=5, style='none', parent=crt_geo_rowLyt )
    cmds.symbolCheckBox(
        height=30, width=10,
        onImage='closeBar.png', offImage='openBar.png', highlightColor=self.THEME['crt']['crt_clmn_back'],
        onCommand=partial(_Build_GeoExtraLyt, None, self_idx, True), offCommand=partial(_Build_GeoExtraLyt, None, self_idx, False),
        annotation="Click to expand or contract extra geometry options", statusBarMessage="Click to expand or contract extra geometry options",
        parent=crt_geo_rowLyt
    )
    #Init extra geometry UI variables
    self.ui_items[0]['geoOrig_picker_txtField'] = None
    self.ui_items[0]['geoDefo_picker_txtField'] = None
    self.ui_items[0]['geo_type_opMenu'] = None
    cmds.separator( height=20, style='none', parent=crt_create_clmnLyt )
    
    #Object
    crt_ctrlType_rowLyt = cmds.rowLayout(
        height=31,
        numberOfColumns=9,
        parent=crt_create_clmnLyt
    )
    cmds.text(
        height=30,
        label="<font size=6>Object</font>", align='left',
        parent=crt_ctrlType_rowLyt
    )
    cmds.separator( height=30, width=10, style='none', parent=crt_ctrlType_rowLyt )
    crt_type_opMenu = cmds.optionMenu(
        height=30, width=168,
        maxVisibleItems=11, changeCommand=partial(_Set_Obj, self_idx),
        annotation="Object(s) to receive new coordinate's output matrix", statusBarMessage="Object(s) to receive new coordinate's output matrix",
        backgroundColor=self.THEME['crt']['main_option_back'],
        parent=crt_ctrlType_rowLyt
    )
    self.ui_items[0]['obj_type_opMenu'] = crt_type_opMenu
    cmds.menuItem( label="None", parent=crt_type_opMenu )
    cmds.menuItem( label="Joint controller", parent=crt_type_opMenu )
    cmds.menuItem( label="Joint > Joint controller", parent=crt_type_opMenu )
    cmds.menuItem( divider=True, longDivider=True, parent=crt_type_opMenu )
    cmds.menuItem( label="Joint locator", parent=crt_type_opMenu )
    cmds.menuItem( label="Joint > Joint locator", parent=crt_type_opMenu )
    cmds.menuItem( divider=True, longDivider=True, parent=crt_type_opMenu )
    cmds.menuItem( label="Transform", parent=crt_type_opMenu )
    cmds.menuItem( label="Joint", parent=crt_type_opMenu )
    cmds.menuItem( divider=True, longDivider=True, parent=crt_type_opMenu )
    cmds.menuItem( label="Selection", parent=crt_type_opMenu )
    cmds.separator( height=30, width=7, style='none', parent=crt_ctrlType_rowLyt )
    # Object offset reference
    crt_off_ref_opMenu = cmds.optionMenu(
        height=30, width=1, visible=False,
        maxVisibleItems=3, changeCommand=partial(_Set_ObjOff, self_idx, 2),
        annotation="Get offset from:\n-Object, if object 'selection'\n-Match object, if match 'closest to'",
        statusBarMessage="Get offset from Object (if object 'selection') or Match object (if match 'closest to')",
        backgroundColor=self.THEME['crt']['extra_option_back'],
        parent=crt_ctrlType_rowLyt
    )
    self.ui_items[0]['obj_off_ref_opMenu'] = crt_off_ref_opMenu
    self.ui_items[0]['obj_off_ref_obj'] = cmds.menuItem( label="Object", parent=crt_off_ref_opMenu )
    self.ui_items[0]['obj_off_ref_match'] = cmds.menuItem( label="Match", parent=crt_off_ref_opMenu )
    cmds.separator( height=30, width=7, style='none', parent=crt_ctrlType_rowLyt )
    # Object offset position/rotation
    crt_off_opMenu = cmds.optionMenu(
        height=30, width=1, visible=False,
        maxVisibleItems=5, changeCommand=partial(_Set_ObjOff, self_idx, 0),
        annotation="Transform(s) to offset", statusBarMessage="Transform(s) to offset",
        backgroundColor=self.THEME['crt']['extra_option_back'],
        parent=crt_ctrlType_rowLyt
    )
    self.ui_items[0]['obj_off_opMenu'] = crt_off_opMenu
    cmds.menuItem( label="No offset", parent=crt_off_opMenu )
    cmds.menuItem( label="☐  Keep position", parent=crt_off_opMenu )
    cmds.menuItem( label="☐  Keep rotation", parent=crt_off_opMenu )
    cmds.menuItem( label="☐  Keep Scale", parent=crt_off_opMenu )
    cmds.menuItem( label="Keep both", parent=crt_off_opMenu )
    cmds.separator( height=30, width=7, style='none', parent=crt_ctrlType_rowLyt )
    # Object offset type
    crt_off_type_opMenu = cmds.optionMenu(
        height=30, width=1, visible=False,
        maxVisibleItems=3, changeCommand=partial(_Set_ObjOff, self_idx, 1),
        annotation="Method used to offset\n\nHierarchy:\nCreate a transform or joint parent\nwith offset in translate/rotate/scale\n\nSelection:\nAdd offset on object's\ntranslate/rotate/scale\n\nNode:\nCreate an intermediate multMatrix\nwith offset stored in",
        statusBarMessage="Method used to offset",
        backgroundColor=self.THEME['crt']['extra_option_back'],
        parent=crt_ctrlType_rowLyt
    )
    self.ui_items[0]['obj_off_type_opMenu'] = crt_off_type_opMenu
    cmds.menuItem( label="Hierarchy", parent=crt_off_type_opMenu )
    cmds.menuItem( label="Selection", parent=crt_off_type_opMenu )
    cmds.menuItem( label="Node", parent=crt_off_type_opMenu )
    cmds.separator( height=20, style='none', parent=crt_create_clmnLyt )
    
    #Match
    crt_match_rowLyt = cmds.rowLayout(
        height=31,
        numberOfColumns=5,
        parent=crt_create_clmnLyt
    )
    cmds.text(
        height=30,
        label="<font size=6>Match</font>", align='left',
        parent=crt_match_rowLyt
    )
    cmds.separator( height=30, width=10, style='none', parent=crt_match_rowLyt )
    match_opMenu = cmds.optionMenu(
        height=30, width=135,
        maxVisibleItems=10, changeCommand=partial(_Set_Match, self_idx),
        annotation="Method to determine the UV position", statusBarMessage="Method to determine the UV position",
        backgroundColor=self.THEME['crt']['main_option_back'],
        parent=crt_match_rowLyt
    )
    self.ui_items[0]['match_opMenu'] = match_opMenu
    cmds.menuItem( label="None", parent=match_opMenu )
    cmds.menuItem( label="Coordinate", parent=match_opMenu ) #UV field
    cmds.menuItem( label="Closest to other", parent=match_opMenu ) #Picker with field
    cmds.menuItem( label="Closest to selection", parent=match_opMenu ) #Option for alternating closest reference and selection
    cmds.separator( height=30, width=4, style='none', parent=crt_match_rowLyt )
    self.ui_items[0]['match_extraLyt'] = cmds.rowLayout(
        height=31, numberOfColumns=3, parent= crt_match_rowLyt
    )
    cmds.separator( height=20, style='none', parent=crt_create_clmnLyt )

    #Start index
    crt_match_rowLyt = cmds.rowLayout(
        height=31,
        numberOfColumns=5,
        parent=crt_create_clmnLyt
    )
    cmds.text(
        height=30,
        label="<font size=6>Start index</font>", align='left',
        parent=crt_match_rowLyt
    )
    cmds.separator( height=30, width=10, style='none', parent=crt_match_rowLyt )
    self.ui_items[0]['start_idx_intField'] = _Build_IntField(
        crt_match_rowLyt, 30,
        (
            60, True, partial(_Set_Start_Idx, self_idx, None, False, None), self.ui_data[0]['start_idx'], 0, None,
            "Coordinate index from which to start adding object(s)\n\nCaution!\nThis doesn't update after an undo or external change!\nPlease use the reload uvPin button above to update fields quickly",
            "Coordinate index from which to start adding object(s)"
        ),
        None,
        (
            12, 0, 2,
            partial(_Set_Start_Idx, self_idx, 0, False, None),
            partial(_Set_Start_Idx, self_idx, 1, False, None)
        ),
        self.THEME['crt']['main_option_back']
    )
    cmds.separator( height=50, style='none', parent=crt_create_clmnLyt )
    #endregion - UVPin

    # ---

    #region - Mirror
    #Mirror
    crt_mirror_rowLyt = cmds.rowLayout(
        height=30,
        numberOfColumns=3,
        parent=crt_create_clmnLyt
    )
    cmds.text(
        height=30,
        label="<font size=6>Mirror</font>", align='left',
        parent=crt_mirror_rowLyt
    )
    cmds.separator( height=30, width=5, style='none', parent=crt_mirror_rowLyt )
    cmds.symbolCheckBox(
        height=30, width=30,
        onImage='confirm.png', offImage='ghostingObjectTypeAll.png', highlightColor=self.THEME['crt']['crt_clmn_back'], value=self.ui_data[0]['mirror'],
        onCommand=partial(_Set_Mirror, self_idx, True), offCommand=partial(_Set_Mirror, self_idx, False),
        parent=crt_mirror_rowLyt
    )

    cmds.separator( height=15, style='none', parent=crt_create_clmnLyt )
    
    #Name
    crt_mirror_name_rowLayout = cmds.rowLayout(
        height=31,
        numberOfColumns=10,
        parent=crt_create_clmnLyt
    )
    cmds.separator( height=30, width=8, style='none', parent=crt_mirror_name_rowLayout )
    mirror_name_type_opMenu = cmds.optionMenu(
        height=30, width=65,
        maxVisibleItems=6, changeCommand=partial(_Set_MirrorParam, self_idx, 4, False, None),
        annotation="Replace on name\n\nNote: Children whose name ends with a number\nmay not have it incremented", statusBarMessage="Replace on name    Note: Children whose name ends with a number may not have it incremented",
        backgroundColor=self.THEME['crt']['main_option_back'],
        parent=crt_mirror_name_rowLayout
    )
    self.ui_items[0]['mirror_name_type_opMenu'] = mirror_name_type_opMenu
    cmds.menuItem( label="None", parent=mirror_name_type_opMenu )
    cmds.menuItem( label="Prefix", parent=mirror_name_type_opMenu )
    cmds.menuItem( label="Suffix", parent=mirror_name_type_opMenu )
    cmds.menuItem( label="First", parent=mirror_name_type_opMenu )
    cmds.menuItem( label="Last", parent=mirror_name_type_opMenu )
    cmds.menuItem( label="All", parent=mirror_name_type_opMenu )
    cmds.separator( height=30, width=5, style='none', parent=crt_mirror_name_rowLayout )
    self.ui_items[0]['mirror_name_source_txtField'] = cmds.textField(
        height=30, width=35,
        text=self.ui_data[0]['mirror_name_source'], changeCommand=partial(_Set_MirrorParam, self_idx, 5, False, None),
        backgroundColor=self.THEME['crt']['main_option_back'],
        parent=crt_mirror_name_rowLayout
    )
    cmds.symbolButton(
        height=30, width=20,
        image='moveUVRight.png', command=partial(_Flip_Mirror_Names, self_idx),
        annotation="Flip source and target values", statusBarMessage="Flip source and target values",
        parent=crt_mirror_name_rowLayout
    )
    self.ui_items[0]['mirror_name_target_txtField'] = cmds.textField(
        height=30, width=35,
        text=self.ui_data[0]['mirror_name_target'], changeCommand=partial(_Set_MirrorParam, self_idx, 6, False, None),
        backgroundColor=self.THEME['crt']['main_option_back'],
        parent=crt_mirror_name_rowLayout
    )
    
    cmds.separator( height=10, style='none', parent=crt_create_clmnLyt )

    #Axis
    crt_mirror_axis_rowLayout = cmds.rowLayout(
        height=31,
        numberOfColumns=10,
        parent=crt_create_clmnLyt
    )
    cmds.separator( height=30, width=8, style='none', parent=crt_mirror_axis_rowLayout )
    cmds.text(
        height=30,
        label="<font size=5>Axis:</font>",
        parent=crt_mirror_axis_rowLayout
    )
    cmds.separator( height=30, width=12, style='none', parent=crt_mirror_axis_rowLayout )
    mirror_axis_opMenu = cmds.optionMenu(
        height=30, width=100,
        maxVisibleItems=7, changeCommand=partial(_Set_MirrorParam, self_idx, 0, False, None),
        annotation="Mirror axis", statusBarMessage="Mirror axis",
        backgroundColor=self.THEME['crt']['main_option_back'],
        parent=crt_mirror_axis_rowLayout
    )
    self.ui_items[0]['mirror_axis_opMenu'] = mirror_axis_opMenu
    cmds.menuItem( label="+X to -X", parent=mirror_axis_opMenu )
    cmds.menuItem( label="+Y to -Y", parent=mirror_axis_opMenu )
    cmds.menuItem( label="+Z to -Z", parent=mirror_axis_opMenu )
    cmds.menuItem( divider=True, longDivider=True, parent=mirror_axis_opMenu )
    cmds.menuItem( label="-X to +X", parent=mirror_axis_opMenu )
    cmds.menuItem( label="-Y to +Y", parent=mirror_axis_opMenu )
    cmds.menuItem( label="-Z to +Z", parent=mirror_axis_opMenu )
    empty = self.ui_data[0]['mirror_axis']+1 if self.ui_data[0]['mirror_direction'] == -1 else self.ui_data[0]['mirror_axis'] + 5
    cmds.optionMenu( mirror_axis_opMenu, edit=True, select=empty )
    empty = False if self.ui_data[0]['mirror_space'] is None else True
    cmds.separator( height=30, width=5, style='none', parent=crt_mirror_axis_rowLayout )
    self.ui_items[0]['mirror_space_symbolChckBx'] = cmds.symbolCheckBox(
        height=30, width=30,
        onImage='polyLoopEdge.png', offImage='polyMirrorCut.png', value=empty,
        changeCommand=partial(_Set_MirrorParam, self_idx, 1, False, None),
        backgroundColor=self.THEME['crt']['main_option_back'], highlightColor=self.THEME['crt']['main_option_back'],
        parent=crt_mirror_axis_rowLayout
    )
    empty = 'None' if self.ui_data[0]['mirror_space'] is None else self.ui_data[0]['mirror_space']
    cmds.separator( height=30, width=5, style='none', parent=crt_mirror_axis_rowLayout )
    self.ui_items[0]['mirror_space_picker_txtField'], self.ui_items[0]['mirror_space_picker_symbBttn'] = _Build_PickerBttn(
        crt_mirror_axis_rowLayout, 30,
        (
            100, empty, True,
            partial(_Set_Mirror_SpaceObject, self_idx, False, None),
            "Object to use as space reference\n\n(Will require a matrix output attribute)\n[Middle mouse]: Select object",
            "Object to use as space reference    (Will require a matrix output attribute)    [Middle mouse]: Select object",
            self.THEME['crt']['extra_option_back'], partial(_Select_Callback, self_idx, 5)
        ),
        1,
        (
            partial(_Pick_Init, self_idx, 1, _Pick_Mirror_SpaceObj_Done, 4, None, True, False, True),
            "Pick tool for object to use as space reference\n\n(Will require a matrix output attribute)",
            "Pick tool for object to use as space reference    (Will require a matrix output attribute)",
            self.THEME['crt']['pick_back_off'], (25,25)
        )
    )
    empty = None
    _Set_MirrorParam( self_idx, 1 )
    cmds.separator( height=10, style='none', parent=crt_create_clmnLyt )

    #Behavior
    crt_mirror_bhv_rowLayout = cmds.rowLayout(
        height=31,
        numberOfColumns=4,
        parent=crt_create_clmnLyt
    )
    cmds.separator( height=30, width=8, style='none', parent= crt_mirror_bhv_rowLayout )
    cmds.text(
        height=30,
        label="<font size=5>Behavior:</font>",
        parent=crt_mirror_bhv_rowLayout
    )
    cmds.separator( height=30, width=12, style='none', parent=crt_mirror_bhv_rowLayout )
    mirror_bhv_opMenu = cmds.optionMenu(
        height=30, width=160,
        maxVisibleItems=3, changeCommand=partial(_Set_MirrorParam, self_idx, 2, False, None),
        annotation="Behavior to expect from mirrored object", statusBarMessage="Behavior to expect from mirrored object",
        backgroundColor=self.THEME['crt']['main_option_back'],
        parent=crt_mirror_bhv_rowLayout
    )
    self.ui_items[0]['mirror_bhv_opMenu'] = mirror_bhv_opMenu
    cmds.menuItem( label="Same", annotation="Mirror object to closest on geometry from mirror position\n\n- Both objects should move and rotate the same way without mirror\nbut alignements may not match depending on the normals from uvPin", parent=mirror_bhv_opMenu )
    cmds.menuItem( label="Mirror rotations", annotation="Mirror object to closest geometry from mirror position\nand add rotation offset values to match alignements of original object's axes\n\n- Both objects should move with the same alignements but in inverted directions\n- Both objects may not rotate in the same direction for two axes\n- No negative scale unlike 'Mirror all', can be necessary for some cases", parent=mirror_bhv_opMenu )
    cmds.menuItem( label="Mirror all", annotation="Mirror object to closest geometry from mirror position\nand add an offset to mirror original object's axes\n\n- Both objects should move and rotate with the same alignements and mirrored directions" )
    cmds.optionMenu( mirror_bhv_opMenu, edit=True, select=self.ui_data[0]['mirror_bhv'] )
    cmds.separator( height=10, style='none', parent=crt_create_clmnLyt )
    
    #Offset method
    crt_mirror_offmtd_rowLayout = cmds.rowLayout(
        height=31,
        numberOfColumns=4,
        parent=crt_create_clmnLyt
    )
    self.ui_items[0]['mirror_offmtd_layout'] = crt_mirror_offmtd_rowLayout
    cmds.separator( height=30, width=8, style='none', parent= crt_mirror_offmtd_rowLayout )
    cmds.text(
        height=30,
        label="<font size=5>Offset method:</font>",
        parent=crt_mirror_offmtd_rowLayout
    )
    cmds.separator( height=30, width=12, style='none', parent=crt_mirror_offmtd_rowLayout )
    mirror_type_opMenu = cmds.optionMenu(
        height=30, width=240,
        maxVisibleItems=11, changeCommand=partial(_Set_MirrorParam, self_idx, 3, False, None),
        annotation="Method used to add the offset allowing\nmirrored axis aligements and directions\n\nCaution changing uvPin normal/tangent axes may\nbreak behavior mirroring and will need to remirror object(s)",
        statusBarMessage="Method used to add the offset allowing mirrored axis aligements and directions  -  Caution changing uvPin normal/tangent axes may break behavior mirroring and will need to remirror object(s)",
        backgroundColor=self.THEME['crt']['main_option_back'],
        parent=crt_mirror_offmtd_rowLayout
    )
    self.ui_items[0]['mirror_offmdt_opMenu'] = mirror_type_opMenu
    empty = "\n\n[EXPERIMENTAL]: Method applying an inbetween(?) offset matrix\nbecause of relative parenting, may not be clean"
    cmds.menuItem( label="Parent space origin - Scale", annotation="Will apply on new offset/orig parent\n\nNo gimbal issue with added offset parent on no-offset parent object\nNeeds object space", parent=mirror_type_opMenu )
    cmds.menuItem( label="Object space origin - Scale", annotation="Will apply on object\n\nNo gimbal issue if object is an offset parent\nNeeds object space", parent=mirror_type_opMenu )
    cmds.menuItem( divider=True, longDivider=True,  parent=mirror_type_opMenu )
    cmds.menuItem( label="Parent flip - Rot/Scale [EXPERIMENTAL]", annotation=f"Will apply on new offset/orig parent\n\nNo gimbal issue\n\nJoint: Need to turn scale compensate off\nunless added orig parent will be the second orig parent{empty}", parent=mirror_type_opMenu ) #Joint too
    cmds.menuItem( label="Object flip - Rot/Scale [EXPERIMENTAL]", annotation=f"Will apply on object\n\nNo gimbal issue\n\nJoint: Need to turn scale compensate off\nunless it has two orig parents and object is the top orig{empty}", parent=mirror_type_opMenu ) #Joint too
    cmds.optionMenu( mirror_type_opMenu, edit=True, select=self.ui_data[0]['mirror_offmtd'] )
    if self.ui_data[0]['mirror_bhv'] != 3:
        cmds.layout( crt_mirror_offmtd_rowLayout, edit=True, enable=False )
    empty = None
    
    cmds.separator( height=20, style='none', parent=crt_create_clmnLyt )
    
    #Mirror selected
    crt_mirror_sel_rowLyt = cmds.rowLayout(
        height=31,
        numberOfColumns=3,
        parent=crt_create_clmnLyt
    )
    cmds.button(
        height=30, width=150,
        label="Mirror selected object(s)", command=partial(_Mirror, None, self_idx, None, None, True),
        annotation="Create uvPin mirror object(s) from selected object(s)\nfollowing above mirror options", statusBarMessage="Create uvPin mirror object(s) from selected object(s) following above mirror options",
        backgroundColor=self.THEME['crt']['mirror_sel_back'],
        parent=crt_mirror_sel_rowLyt
    )
    #endregion - Mirror
    cmds.separator( height=15, style='none', parent=crt_clmnLyt )
    
    #Create object
    crt_createBttn_clmnLyt = cmds.columnLayout(
        height=40,
        adjustableColumn=True, columnOffset=('both',115),
        parent=crt_clmnLyt
    )
    cmds.button(
        height=40,
        label="CREATE OBJECT", command=partial(_Create_UVPin, self_idx),
        backgroundColor=self.THEME['crt']['crt_bttn_back'],
        parent=crt_createBttn_clmnLyt
    )

    cmds.formLayout(
        crt_formLyt, edit=True,
        attachForm=(
            (crt_clmnLyt,'top',5), (crt_clmnLyt,'left',5), (crt_clmnLyt,'right',5), (crt_clmnLyt,'bottom',5)
        )
    )
    #endregion - Tab Create
    
    #region - Tab Display
    disp_formLyt = cmds.formLayout(
        margins=15,
        parent=main_tabLyt
    )
    disp_topBar_clmnLyt = cmds.columnLayout(
        height=89,
        adjustableColumn=True,
        parent=disp_formLyt
    )
    #region - Top bar
    disp_topBar_rowLyt = cmds.rowLayout(
        height=50,
        numberOfColumns=5,
        parent=disp_topBar_clmnLyt
    )
    
    self.ui_items[1]['uvp_picker_symbBttn'] = _Build_PickerBttn( #Picker
        disp_topBar_rowLyt, 50,
        None,
        None,
        (
            partial(_Pick_Init, self_idx, 1, _Pick_UVPIN_Done_DISP, 2, 'uvPin', True, True, False),
            "Click while having an uvPin node selected\nor the attribute editor open on an uvPin tab\n\nElse becomes a picker for next uvPin node selected",
            "Click while having an uvPin node selected or the attribute editor open on an uvPin tab.  -  Else becomes a picker for next uvPin node selected",
            self.THEME['disp']['tb_uvpBttn_back_off']
        ), 'teAdd.svg'
    )

    cmds.separator( height=50, width=8, style='none', parent=disp_topBar_rowLyt )
    cmds.separator( height=50, width=3, style='none', backgroundColor=self.THEME['disp']['tb_sep_back'], parent=disp_topBar_rowLyt )
    cmds.separator( height=50, width=12, style='none', parent=disp_topBar_rowLyt )
    disp_node_txtCtrl = cmds.text(
        height=50,
        label=f"<font size=7>UVPIN: <font color={self.THEME['disp']['tb_uvpName_None']}><i>None</font>", align='left', recomputeSize=True,
        annotation="No uvPin node\n\n[Middle mouse]: Select node", statusBarMessage="No uvPin node    [Middle mouse]: Select node",
        parent=disp_topBar_rowLyt
    )
    self.ui_items[1]['node_txtCtrl'] = disp_node_txtCtrl
    #endregion - Top bar

    cmds.separator( height=4, width=10, style='none', parent=disp_topBar_clmnLyt )

    #region - Pages bar
    disp_pagesBar_rowLyt = cmds.rowLayout( # Row
        height=32,
        numberOfColumns=17,
        backgroundColor=self.THEME['disp']['pb_back'],
        parent=disp_topBar_clmnLyt
    )
    self.ui_items[1]['pagesBar_rowLyt'] = disp_pagesBar_rowLyt
    #Current page UI
    cmds.separator( height=30, width=2, style='none', parent=disp_pagesBar_rowLyt )
    cmds.text(
        height=30, width=30,
        label="Page:", align='left',
        parent=disp_pagesBar_rowLyt
    )
    cmds.separator( height=30, width=2, style='none', parent=disp_pagesBar_rowLyt )
    
    disp_cPage_intFld = cmds.intField( # Current page field
        height=30, width=30,
        editable=True, value=self.ui_data[1]['page_current'], minValue=0, step=1,
        enableKeyboardFocus=False, changeCommand=partial(_Set_Page, None, self_idx, None, False),
        backgroundColor=self.THEME['disp']['pb_field_back'],
        parent=disp_pagesBar_rowLyt
    )
    self.ui_items[1]['cPage_intFld'] = disp_cPage_intFld
    
    #Up down page buttons
    disp_pagesBttns_flwLyt = cmds.flowLayout(
        height=30, width=15,
        vertical=True, wrap=False,
        parent=disp_pagesBar_rowLyt
    )
    cmds.symbolButton(
        height=14, width=14,
        image='moveUVUp.png', command=partial(_Set_PageBttn, None, self_idx, True),
        parent=disp_pagesBttns_flwLyt
    )
    cmds.symbolButton(
        height=14, width=14,
        image='moveUVDown.png', command=partial(_Set_PageBttn, None, self_idx, False),
        parent=disp_pagesBttns_flwLyt
    )
    cmds.separator( height=30, width=3, style='none', parent=disp_pagesBar_rowLyt )
    cmds.text( height=30, width=12, label="<font size=5>/</font>", align='left', parent=disp_pagesBar_rowLyt )
    disp_pageCount_txtCtrl = cmds.text( # Max pages text
        height=30,
        label=self.ui_data[1]['page_count'], align='left', recomputeSize=True,
        parent=disp_pagesBar_rowLyt
    )
    self.ui_items[1]['pCount_txtCtrl'] = disp_pageCount_txtCtrl
    cmds.separator( height=30, width=85, style='none', parent=disp_pagesBar_rowLyt )
    
    #Items per page UI
    cmds.text(
        height=30,
        label="Per page:", align='left',
        parent=disp_pagesBar_rowLyt
    )
    cmds.separator( height=30, width=2, style='none', parent=disp_pagesBar_rowLyt )
    disp_maxPPage_intFld = cmds.intField( # Max per page field
        height=30, width=40,
        editable=True, value=self.ui_data[1]['item_per_page'], minValue=1, step=1,
        enableKeyboardFocus=False, changeCommand=partial(_Set_MaxPerPage, None, self_idx),
        backgroundColor=self.THEME['disp']['pb_field_back'],
        parent=disp_pagesBar_rowLyt
    )
    self.ui_items[1]['maxPPage_intFld'] = disp_maxPPage_intFld
    cmds.separator( height=30, width=5, style='none', parent=disp_pagesBar_rowLyt )
    self_item_count = self.ui_data[1]['item_count']
    disp_inCount_txtCtrl = cmds.text( # UVPin inputs count text
        height=30,
        label=f"({self_item_count} total {'input' if self_item_count < 2 else 'inputs'})", align='left', font='obliqueLabelFont',
        parent=disp_pagesBar_rowLyt
    )
    self.ui_items[1]['inCount_txtCtrl'] = disp_inCount_txtCtrl
    cmds.separator( height=30, width=26, style='none', parent=disp_pagesBar_rowLyt )
    cmds.symbolButton(
        height=30, width=30,
        image='CN_refresh.png', command=partial(_RefreshUI, None, self_idx),
        annotation="Reload page",
        statusBarMessage="Reload page",
        backgroundColor=self.THEME['disp']['pb_bttn_back'],
        parent=disp_pagesBar_rowLyt
    )
    #endregion - Pages bar

    disp_scrollArea_scrollLyt = cmds.scrollLayout(
        height=10,
        borderVisible=False, childResizable=True, verticalScrollBarAlwaysVisible=True,
        backgroundColor=self.THEME['disp']['scrla_back'],
        parent=disp_formLyt
    )
    self.ui_items[1]['scrollLyt'] = disp_scrollArea_scrollLyt

    cmds.formLayout(
        disp_formLyt, edit=True,
        attachForm=(
            (disp_topBar_clmnLyt, 'top', 5), (disp_topBar_clmnLyt, 'left', 5), (disp_topBar_clmnLyt, 'right', 5),
            (disp_scrollArea_scrollLyt, 'top', 92), (disp_scrollArea_scrollLyt, 'left', 5), (disp_scrollArea_scrollLyt, 'right', 5), (disp_scrollArea_scrollLyt, 'bottom', 5)
        )
    )
    #endregion - Tab Display
    
    #region - End setup
    #Update main tabs
    cmds.tabLayout(main_tabLyt, edit=True, tabLabel=((crt_formLyt,"Create"),(disp_formLyt,"Display")))
    if tab < 1:
        tab = 1
    elif tab > 2:
        tab = 2
    cmds.tabLayout(main_tabLyt, edit=True, selectTabIndex=tab)
    cmds.formLayout(
        main_formLyt, edit=True,
        attachForm=(
            (main_tabLyt, 'top', 0), (main_tabLyt, 'left', 0), (main_tabLyt, 'right', 0), (main_tabLyt, 'bottom', 0)
        )
    )
    cmds.showWindow()
    cmds.setFocus('')
    #endregion - End setup

def Close( self_idx:int ): #Close a specific instance and it's window
    """
    Close a specific instance and it's window\n
    ### Parameters:\n
    'self_idx' (int): class object index in global_win_instances
    """
    global global_win_instances
    global global_win_count

    if global_win_instances[self_idx] is None:
        return
    if self_idx > len(global_win_instances):
        cmds.error( f"[ISSUE]: Instance index {self_idx} out of range!", noContext=True )
    _Pick_Cancel( None, self_idx )
    global_win_instances[self_idx] = None

    all_none = True
    for c_instance in global_win_instances:
        if c_instance is not None:
            all_none = False
            break
    if all_none:
        global_win_instances.clear()
        global_win_count = 0
    
def Close_All(): #Close all instances and their window
    """ Close all instances and their window """
    global global_win_instances
    global global_win_count
    
    for c_instance in global_win_instances:
        if c_instance is None:
            continue
        elif cmds.window( c_instance.WIN_NAME, query=True, exists=True ):
            cmds.deleteUI( c_instance.WIN_NAME, window=True )
    global_win_instances.clear()
    global_win_count = 0

def Print_Global(): #Print global window instances
    """ Print global window instances """
    print( global_win_count, global_win_instances )
    i = 0
    for c_instance in global_win_instances:
        print( i, c_instance )
        i+=1

def Print_Data( self_idx=None ): #Print data from each global window instances
    """
    Print data from each global window instances\n
    ### Parameters:\n
    'self_idx' (None/int): If None, print for every instances else the instance at called index
    """
    instances_list = None
    i = None
    #Get instance(s)
    if self_idx is None:
        instances_list = global_win_instances
        i = 0
    else:
        if self_idx != 0 and self_idx > global_win_count-1:
            cmds.error( f"[ISSUE]: Index {self_idx} out of range! (Range max: {global_win_count-1})", noContext=True )
        else:
            instances_list = (global_win_instances[self_idx],)
            i = self_idx
    #Print
    for c_instance in instances_list:
        if c_instance is None:
            print( f"Instance {i} data: None" )
        else:
            tabs = ('Create','Display')
            tab_idx = 0
            for c_tab in c_instance.ui_data:
                print( f"Instance {i} '{tabs[tab_idx]}' data:" )
                for c_data in c_tab.items():
                    print( f"  '{c_data[0]}': {c_data[1]}" )
                tab_idx+=1
        i+=1
#endregion - * Public *
#endregion --- Functions ---