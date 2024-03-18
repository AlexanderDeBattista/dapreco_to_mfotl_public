from atomic_concepts.interfaces import AtomIterable
from atomic_concepts import Before, After, Relation, Var, Atom, Eventuality, Once, Ind

from rule.rule import Rule
from rule.logical_connectives import LogicalConnective, Or, Not, Implies

from util.legal_ml_parser import get_legal_ml_root, get_rules_for_statement

from name_space import NameSpace


#TODO: This method over-approximates the concepts that are related to a given variable, 
# which makes the overall program extremely slow. 
def get_vars_this_var_defines(atom_list: [], var: Var, vars_to_track: [], atoms_to_track: [], already_tracked: [], atom_already_tracked: []):
    """Given a list of atoms, a variable and two lists, iteratively find all variables and atoms that the input var defines. We consider a var to define the
    meaning of a predicate if it is the first variable. For example, in the predicate rioOnto:RexistAtTime(:a1 :t1), :a1 defines the predicate.

    Args:
        atom_list (_type_): _description_
        var (Var): _description_
        vars_to_track (_type_): _description_
        atoms_to_track (_type_): _description_
        already_tracked (_type_): _description_
    """    
    queue = atom_list.copy()
    while len(queue) > 0:
        # Order is important, pop first element of queue,not last
        curr = queue.pop(0)
        if not var in curr:
            continue
        if isinstance(curr, Atom):
            if isinstance(curr.atom_content[0], Relation):
                if len(curr.atom_content[0].get_rel_content()) == 0:
                    continue
                if not var == curr.atom_content[0].get_rel_content()[0]:
                    continue
            if not isinstance(curr.atom_content[0], Relation) or not var == curr.atom_content[0].get_rel_content()[0]:
                continue
            
            for item in curr.atom_content[0]:
                """if (len(already_tracked) == 1 and already_tracked[0] == item and item not in vars_to_track):
                    vars_to_track.append(item)
                    atoms_to_track.append(curr)
                    continue"""
                
                # This makes us include all leaf nodes, but it is INCREDIBLY ugly in practice
                # TODO: MAKES PROGRAM VERY SLOW!!
                if ((len(already_tracked) > 1 and already_tracked[-1] == item and not already_tracked[-2] == item)):# and curr != atom_already_tracked[-1])):
                    vars_to_track.append(item)
                    atoms_to_track.append(curr)
                    continue
                
                # TODO: Not skip ind? Should be fine, because IND are always leaves and never used to define anything
                if (item in already_tracked):
                    continue
                # Want to associate each var to an atom, so add both vars and atoms in this order
                vars_to_track.append(item)
                atoms_to_track.append(curr)
               
        elif isinstance(curr, AtomIterable):
            for item in curr:
                if isinstance(item, (Before, After)):
                    continue
                
                queue.append(item)
        
def get_one_level_neighbours(atom_list: [], var: Var, vars_to_track: [], atoms_to_track: [], already_tracked: []):
    """Given a list of atoms, a variable and two lists, iteratively find all variables and atoms that are related to the given variable.

    Args:
        atom_list (_type_): _description_
        var (Var): _description_
        vars_to_track (_type_): _description_
        atoms_to_track (_type_): _description_
        already_tracked (_type_): _description_
    """    
    queue = atom_list.copy()
    while len(queue) > 0:
        curr = queue.pop(0)
    
        if isinstance(curr, Var) and not curr in already_tracked:
            vars_to_track.append(curr)
            continue
            
        if not var in curr:
            continue

        if isinstance(curr, AtomIterable):
            for item in curr:
                if isinstance(item, (Before, After)):
                    continue
                # Want to avoid adding concepts related to a different timestamp.
                # This method implicitly assumes that we are only doing a search over one timestamp
                # TODO: Change this?
                if isinstance(item, Relation):
                    if item.get_rel_name() == (NameSpace.RIOONTO.value + ":and") and not item.get_rel_content()[0] == var:
                        continue
                
                queue.append(item)

        # TODO:Add more?
        if isinstance(curr, Relation):
            atoms_to_track.append(curr)
            
def get_concepts_related_to(rule: Rule, var: Var, already_tracked: [], if_atoms: bool = True, then_atoms: bool = True):
    """Given a rule and a variable, return a list of all variables and concepts needed to express the given variable.
    
    For example, given rule RULE(rioOnto:RexistAtTime :a1 :t1) & (rioOnto:and' :a1 :ep :edp) & ... ) and VAR(a1), we
    first need to find the predicates where a1 is used as an eventuality (when the predicate is reified) or a1 is the
    first variable in a non-reified predicate. If a1 exists, then we also know that also [t1, ep, edp] needs to exist.
    Recursively evaluate over the new variables that also needs to exist to eventually end up with a list of all predicates and variables
    that needs to exist if the input variable exists.

    Args:
        rule (Rule): _description_
        var (Var): _description_
        already_tracked (List): _description_

    Returns:
        _type_: _description_
    """    
    vars_to_track = []
    atoms_to_track = []
    
    if if_atoms:
        get_one_level_neighbours(rule.if_atoms, var, vars_to_track, atoms_to_track, already_tracked)
    if then_atoms:
        get_one_level_neighbours(rule.then_atoms, var, vars_to_track, atoms_to_track, already_tracked)
    
    # Remove duplicates
    vars_to_track = list(dict.fromkeys(vars_to_track))
    already_tracked.append(var)
    
    for new_var in vars_to_track:
        atoms, vars = get_concepts_related_to(rule, new_var, already_tracked, if_atoms, then_atoms)
        [atoms_to_track.append(x) for x in atoms if x not in atoms_to_track]
        [vars_to_track.append(x) for x in vars if x not in vars_to_track]

    return (atoms_to_track, vars_to_track)

def remove_relation_reification(atom: Atom):
    #print(atom.get_atom_content()[0])
    atom.un_reify()
    #atom.get_atom_content()[0].update_content(atom.get_atom_content()[0].get_rel_content()[1:])
    #print(atom.get_atom_content()[0])
    
    
def remove_reification_for_rexist_and(rule: Rule):
    queue = rule.if_atoms.copy()
    r_exist_atom = None
    and_atom = None
    while len(queue) > 0:
        curr_item = queue.pop(0)
        if isinstance(curr_item, AtomIterable):
            for item in curr_item:
                queue.append(item)
        if isinstance(curr_item, Atom):
            if ( curr_item.get_atom_content()[0].get_rel_name() == (NameSpace.RIOONTO.value + ":RexistAtTime") 
            and queue[0].get_atom_content()[0].get_rel_name() == (NameSpace.RIOONTO.value + ":and")):
                r_exist_atom = curr_item
                and_atom = queue[0]
        
    if r_exist_atom is None or and_atom is None:
        return
    
    to_remove = [r_exist_atom, and_atom]
    # We don't nececarilly want to remove all vars related to the and relation, but for sure we want to remove the time variable and reification of "and"
    vars_to_remove = [to_remove[0].get_atom_content()[0].get_rel_content()[1], to_remove[1].get_atom_content()[0].get_rel_content()[0]]
                
    remove_relation_reification(and_atom)
    
    # Iterate over variables in the "and" relation, and remove the reification from relations that use reifications from the "and"
    for var in and_atom.get_atom_content()[0].get_rel_content():
        for second_atom in rule.if_atoms[2:]:
            if not isinstance(second_atom, Atom) or not second_atom.is_reified():
                continue
            if second_atom.get_atom_content()[0].get_rel_content()[0] == var:
                second_atom.get_atom_content()[0].get_rel_content()
                remove_relation_reification(second_atom)
                break
        
        for second_atom in rule.then_atoms:
            if not isinstance(second_atom, Atom) or not second_atom.is_reified():
                continue
            if second_atom.get_atom_content()[0].get_rel_content()[0] == var:
                remove_relation_reification(second_atom)
                break
        
    
    # Remove marked atoms from the rule
    new_if_atoms = []
    for atom in rule.if_atoms:
        if atom not in to_remove:
            new_if_atoms.append(atom)
    
    new_then_atoms = []
    for atom in rule.then_atoms:
        if atom not in to_remove:
            new_then_atoms.append(atom)

    new_if_exists = []    
    # Remove these variables from the "exist" part of the rule
    for var in rule.if_exist:
            if var not in vars_to_remove:
                new_if_exists.append(var)
        
    rule.if_exist = new_if_exists
            
    rule.if_atoms = new_if_atoms
    rule.then_atoms = new_then_atoms
    return rule

def handle_then_time_relation(rule: Rule):
    then_atoms = rule.then_atoms
    exist_in_time = False
    exist_temporal_relation = False
    timestamp_name = None
    temporal_variable = None
    temporal_relation = None
    
    # Get timestamps from "if" part of rule.
    if_timestamps = []
    stack = rule.if_atoms.copy()
    while len(stack) > 0:
        curr = stack.pop(0)
        if isinstance(curr, Relation):
            if curr.get_rel_name() == (NameSpace.RIOONTO.value + ":RexistAtTime"):
                if_timestamps.append(curr.get_rel_content()[1])
        if isinstance(curr, AtomIterable):
            for item in curr:
                stack.append(item)
    
    # Check if the "then" part of the rule contains a temporal relation and a timestamp.
    stack = rule.then_atoms.copy()
    while len(stack) > 0:
        curr = stack.pop(0)
        # TODO: Currently the "RexistAtTime" is expected to be the first relation in the "then" part of the rule.
        # I Think this is always the case for DAPRECO, but not in general
        if isinstance(curr, Relation):
            if curr.get_rel_name() == (NameSpace.RIOONTO.value + ":RexistAtTime"):
                exist_in_time = True
                timestamp_name = curr.get_rel_content()[1]
                temporal_variable = curr.get_rel_content()[0]
                
        if isinstance(curr, (Before, After)):
            if timestamp_name in curr:
                exist_temporal_relation = True
                temporal_relation = curr
        if isinstance(curr, AtomIterable):
            for item in curr:
                stack.append(item)
    # If the "then" part of the rule does not contain a temporal relation or a timestamp, we do not need to do anything. 
    if not exist_in_time or not exist_temporal_relation:
        return

    # The first variable in the temporal relation should be a be the recently defined. 
    # I.e. if t2 just got defined, we expect a temporal relation like this After(t1,t2), because it defined t2 in relation to t1.
    assert temporal_relation.t1 == timestamp_name
    
    if isinstance(temporal_relation, Before):
        rule.then_atoms = [Once(temporal_relation.t1, temporal_relation.t2, rule.then_atoms)]
        
    elif isinstance(temporal_relation, After):
        rule.then_atoms = [Eventuality(temporal_relation.t1, temporal_relation.t2, rule.then_atoms)]
    else:
        # Should not happen
        raise Exception(f"Unknown temporal relation {type(temporal_relation)}")
    
def remove_unreified_connective(rule: Rule, connective_name: str, new_connective: LogicalConnective):
    """Look for unreified connectives in the rule, and replace 

    Args:
        rule (Rule): _description_
        connective_name (str): _description_
        new_connective (LogicalConnective): _description_

    Returns:
        _type_: _description_
    """    
    queue = rule.if_atoms.copy()
    for atom in rule.then_atoms:
        queue.append(atom)
    
    variables = []
    while len(queue) > 0:
        curr = queue.pop(0)
        
        if isinstance(curr, AtomIterable):
            for item in curr:
                queue.append(item)
        
        if isinstance(curr, Atom) and not curr.is_reified() and curr.get_atom_content()[0].get_rel_name() == connective_name:
            # Found matching connective
            # Now add all the related variables to a list, and find all the atoms that these variables define

            for var in curr.get_atom_content()[0].get_rel_content()[1:]:
                variables.append(var)
            
            rule.if_atoms.remove(curr)

    atoms_related_to_var = []
    
    for var_to_look_for in variables:
        queue = rule.if_atoms.copy()
        for atom in rule.then_atoms:
            queue.append(atom)

        while len(queue) > 0:
            curr = queue.pop(0)
            
            if isinstance(curr, AtomIterable):
                for item in curr:
                    queue.append(item)
            if isinstance(curr, Atom) and isinstance(curr.get_atom_content()[0], Relation) and curr.get_atom_content()[0].get_rel_content()[0] == var_to_look_for:
                atoms_related_to_var.append(curr)
    
    for atom in atoms_related_to_var:
        atom.un_reify()
        rule.if_atoms.remove(atom)
    rule.if_atoms.append(new_connective(atoms_related_to_var))
            
    return rule
    
def remove_unreified_not(rule):
    return remove_unreified_connective(rule, (NameSpace.RIOONTO.value + ":not"), Not())
def remove_unreified_or(rule):
    return remove_unreified_connective(rule, (NameSpace.RIOONTO.value + ":or"), Or())
def remove_unreified_imply(rule):
    return remove_unreified_connective(rule, (NameSpace.RIOONTO.value + ":imply"), Implies())

def handle_time_relations(rule: Rule):
    # Handle if part
    seen_timestamps = []
    seen_time_relations = []
    queue = rule.if_atoms.copy()
    while len(queue) > 0:
        curr = queue.pop(0)
        if isinstance(curr, Relation):
            if curr.get_rel_name() == (NameSpace.RIOONTO.value + ":RexistAtTime"):
                seen_timestamps.append(curr)
        if isinstance(curr, (Before, After)):
            seen_time_relations.append(curr)
        if isinstance(curr, AtomIterable):
            for item in curr:
                queue.append(item)
    
    related_concepts_dict = {}
    for timestamp in seen_timestamps:
        for time_relation in seen_time_relations:
            if timestamp.get_rel_content()[1] in time_relation:
                related_concepts = get_concepts_related_to(rule, timestamp.get_rel_content()[0], [], if_atoms=True, then_atoms=False)
                related_concepts_dict[timestamp.get_rel_content()[1]] = related_concepts[0]

    
    for time_relation in seen_time_relations:
        t1 = time_relation.t1
        t2 = time_relation.t2
        
        if not isinstance(t2, Var):
            for key in related_concepts_dict.keys():
                if key in t2:
                    t2 = key
                    break
                
        #TODO: Which atoms should we move into the new temporal relation?
        #Right now we only move the concepts that are strictly related to t2, but we might want to duplicate some?
        t2_t1_difference = difference_of_concepts(related_concepts_dict[t2], related_concepts_dict[t1])

        i = 0
        # Remove concepts we will move to a temporal relation
        while i > len(rule.if_atoms):
            if rule.if_atoms[i] in t2_t1_difference:
                rule.if_atoms.pop(i)
            else:
                i += 1
            
        mfotl_time_relation = None
        if isinstance(time_relation, Before):
            mfotl_time_relation = Once(t1, t2, t2_t1_difference)
        elif isinstance(time_relation, After):
            mfotl_time_relation = Eventuality(t1, t2, t2_t1_difference)
        else:
            raise Exception(f"Unknown temporal relation {type(time_relation)}")

        rule.if_atoms.append(mfotl_time_relation)
    print(f"Seen timestamps: {[str(x) for x in seen_timestamps]}")
    print(f"Seen time relations: {[str(x) for x in seen_time_relations]}")
    
def intersections_of_concepts(concept_list_1, concept_list_2):
    return [x for x in concept_list_1 if x in concept_list_2]

def difference_of_concepts(concept_list_1, concept_list_2):
    return [x for x in concept_list_1 if x not in concept_list_2]
    
    
if __name__ == "__main__":
    root = get_legal_ml_root("rioKB_GDPR.xml")
    rules = get_rules_for_statement("statements83", root)
    print(rules[0])
    print(remove_reification_for_rexist_and(rules[0]))

    print("\n--- GET CONCEPTS RELATED TO SOME VARIABLE ---\n")
    rules = get_rules_for_statement("statements34", root)#("statements1", root)

    related_concepts_and_vars_if = get_concepts_related_to(rules[0], rules[0].if_atoms[0].get_atom_content()[0].get_rel_content()[0], [])
    related_concepts_and_vars_then = get_concepts_related_to(rules[0], rules[0].then_atoms[0].get_atom_content()[0].get_rel_content()[0], [])

    print([str(x) for x in intersections_of_concepts(related_concepts_and_vars_if[0], related_concepts_and_vars_then[0])])

    print("\n--- Given before/after in 'then' part of rule, do appropriate implication with eventuality, etc. ---\n")

    handle_then_time_relation(rules[0])
    print(rules[0])

    rules = get_rules_for_statement("statements34", root)
    handle_time_relations(rules[7])