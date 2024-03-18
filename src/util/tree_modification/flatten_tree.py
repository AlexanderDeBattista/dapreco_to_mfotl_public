from data_structure.rule_tree.rule_tree import RuleTree
from data_structure.rule_tree.branch_modifier import BranchModifier, Eventually, Historically, Once, TimeModifier, And, Implies, Or, Not
from atomic_concepts import Atom, Expression, Function, Var
from copy import deepcopy
from name_space.name_space import NameSpace
from atomic_concepts.relation import Relation

def flatten_tree(tree: RuleTree) -> RuleTree:
    #print(f"----- start ------\n{tree.printNTree()}")
    flat_tree = _flatten_tree(deepcopy(tree), [])
    
    #print(f"----- stop ------\n{flat_tree.printNTree()}")

    flat_tree = add_and_modifier_to_consequent(flat_tree)
    flat_tree = remove_and_modifiers(flat_tree)
    flat_tree = remove_branches_with_only_id(flat_tree)

    flat_tree = remove_r_exist_at_time(flat_tree)
    flat_tree = add_referenced_nodes(flat_tree, tree)
    flat_tree = rewrite_naf(flat_tree)
    flat_tree = unreify_reified_predicates(flat_tree)
    
    return flat_tree

def unreify_reified_predicates(tree: RuleTree):
    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        for child in curr.relations:
            queue.append(child)
        
        if isinstance(curr.parent_relation, Atom) and curr.parent_relation.is_reified():
            curr.parent_relation.un_reify()
    
    return tree
def rewrite_functions(tree: RuleTree):
    """Rewrites functions, or what DAPRECO refers to as 'functional terms', to predicates.
    A function like pred(f(x)) is rewritten to fun:f(x,y) AND pred(y)"""
    queue = [(tree, None)]
    mapper = {}
    while len(queue) > 0:
        curr,grandparent = queue.pop(0)
        for child in curr.relations:
            queue.append((child, curr))
        
            if isinstance(child.parent_relation, Atom) and isinstance(child.parent_relation.get_atom_content()[0], Relation):
                preds_to_add = []
                for content in child.parent_relation.get_atom_content()[0].get_rel_content():
                    if not isinstance(content, Expression):
                        continue
                    new_predicates = handle_function_rewrite(child.parent_relation, preds_to_add, mapper)
                    for new_pred in new_predicates:
                        if grandparent is not None and isinstance(curr.parent_relation, Not) and "fun" in new_pred.get_atom_content()[0].get_rel_name():
                            if isinstance(grandparent.parent_relation, Implies):
                                i = grandparent.relations.index(curr)
                                grandparent.relations[i] = RuleTree(None, And())
                                
                                
                                grandparent.relations[i].add_node(curr)
                                grandparent.relations[i].add_node(RuleTree(None, new_pred))
                            else:
                                grandparent.add_node(RuleTree(None, new_pred))
                        else:
                            curr.add_node(RuleTree(None, new_pred))
                        
    return tree  

def remove_duplicate_predicates(tree: RuleTree):
    """Given one 'layer' of the tree, remove all duplicate predicates in that layer"""
    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        seen_preds = []
        to_remove_index = []
        for i in range(len(curr.relations)):
            child = curr.relations[i]
            queue.append(child)
            child_par_rel = child.parent_relation
            
            if isinstance(child_par_rel, Atom) and child_par_rel in seen_preds:
                to_remove_index.append(i)
            elif isinstance(child_par_rel, Atom):
                seen_preds.append(child_par_rel)
        
        for i in to_remove_index[::-1]:
            del curr.relations[i]
    
    return tree
def handle_function_rewrite(atom: Atom, preds_to_add: [Atom], mapper: dict):    
    for i in range(len(atom.get_atom_content()[0].get_rel_content())):
        content = atom.get_atom_content()[0].get_rel_content()[i]
        if not isinstance(content, Expression):
            continue
        
        fun_pred_atom = Atom(False)
        preds_to_add.append(fun_pred_atom)
        fun_pred_name = f"fun:{content.fun.fun_name}"
        fun_rel = Relation(fun_pred_name) 
        fun_pred_atom.add_rel(fun_rel)
        
        output = None
        if fun_pred_name not in mapper:
            mapper[fun_pred_name] = f"f{chr(ord('a') + len(mapper))}"
        output = mapper[fun_pred_name]
        output_var = Var(f":{output}")
        
        
        if isinstance(content.fun.arguments[0], Expression):
            fun_fun_pred_atom = Atom(False)
            preds_to_add.append(fun_fun_pred_atom)
            
            fun_fun_name = f"fun:{content.fun.arguments[0].fun.fun_name}"
            fun_fun_rel = Relation(fun_fun_name)
            fun_fun_pred_atom.add_rel(fun_fun_rel)
            
            fun_fun_output = None
            if fun_fun_name not in mapper:
                mapper[fun_fun_name] = f"f{chr(ord('a') + len(mapper))}"
            fun_fun_output = mapper[fun_fun_name]
            fun_fun_output_var = Var(f":{fun_fun_output}")
            
            
            fun_fun_rel.add_relation_content(content.fun.arguments[0].fun.arguments[0])
            fun_fun_rel.add_relation_content(fun_fun_output_var)
            
            fun_rel.add_relation_content(fun_fun_output_var)
            fun_rel.add_relation_content(output_var)
            
            atom.get_atom_content()[0].get_rel_content()[i] = fun_fun_output_var
        else:
            fun_rel.add_relation_content(content.fun.arguments[0])
            fun_rel.add_relation_content(output_var)
            atom.get_atom_content()[0].get_rel_content()[i] = output_var
    
    return preds_to_add

def remove_redundant_predicates(tree: RuleTree):
    mapping = {
        "prOnto:nominates" : ["prOnto:Controller", "prOnto:Processor"],
        "prOnto:PersonalData": ["prOnto:DataSubject"],
        "dapreco:GiveConsent": ["prOnto:Consent"],
        "dapreco:Identify": ["prOnto:Controller", "prOnto:DataSubject"],
        "prOnto:Transmit": ["prOnto:Processor", "prOnto:PersonalData"],
    }
    
    pred_to_remove = {}
    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        for i in range(len(curr.relations)):
            child = curr.relations[i]
            queue.append(child)

            name = None
            if isinstance(child.parent_relation, Atom) and isinstance(child.parent_relation.get_atom_content()[0], Relation):
                name = child.parent_relation.get_atom_content()[0].get_rel_name()
            else:
                continue

            if name in mapping:
                for x in mapping[name]:
                    pred_to_remove[x] = True
    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        new_child_rel = []
        for child in curr.relations:
            queue.append(child)
            
            name = None
            if isinstance(child.parent_relation, Atom) and isinstance(child.parent_relation.get_atom_content()[0], Relation):
                name = child.parent_relation.get_atom_content()[0].get_rel_name()
            
            if name not in pred_to_remove:
                new_child_rel.append(child)
        
        # Don't want to remove all children, might cause errors in other parts of the code
        if not (len(new_child_rel) == 0):
            curr.relations = new_child_rel
    return tree

        
        
# Remove NAF and replace it with a "not" node with the contents of the NAF atom as its child
def rewrite_naf(tree: RuleTree):
    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        for i in range(len(curr.relations)):
            child = curr.relations[i]
            queue.append(child)
            if not isinstance(child.parent_relation, Atom) or not child.parent_relation.is_naf():
                continue
            child.parent_relation.set_naf(False)
            new_node = RuleTree(None, Not())
            new_node.relations = [child]
            curr.relations[i] = new_node
            
    return tree

def rewrite_non_delayed(tree: RuleTree) -> None:
    """Assumes a flat tree where "nonDelayed" has no children. It then removes the "nonDelayed" node and
    modifies the time modifier to include the contents of the "nonDelayed" modifier

    Args:
        tree (RuleTree): _description_

    Returns:
        _type_: _description_
    """
    _rewrite_non_delayed(tree)

    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        for i in range(len(curr.relations)):
            child = curr.relations[i]
            if isinstance(child.parent_relation, Atom) and isinstance(child.parent_relation.get_atom_content()[0], Relation) and child.parent_relation.get_atom_content()[0].get_rel_name() == "dapreco:nonDelayed":
                del curr.relations[i]
                break
            queue.append(child)
            
    return tree

def _rewrite_non_delayed(tree: RuleTree) -> Relation:
    if tree is None:
        return None

    if isinstance(tree.parent_relation, Atom) and isinstance(tree.parent_relation.get_atom_content()[0], Relation) and tree.parent_relation.get_atom_content()[0].get_rel_name() == "dapreco:nonDelayed":
        return tree.parent_relation.get_atom_content()[0]
    
    if len(tree.relations) == 0:
        return None
    
    non_delayed = None
    # TODO: Probably rewrite this function 
    # Right now the loop terminates on the first instance of a non-delayed modifier it finds,
    # which means that if there exists multiple non-delayed modifiers, only the first one will be rewritten
    # Start at the end of the relations tree, because then we will analyze the consequent before the antecedent.
    for i in range(len(tree.relations)-1,-1,-1):
        child = tree.relations[i]
        res = _rewrite_non_delayed(child)
        if res is not None:
            non_delayed = res

    if non_delayed is None:
        return None

    
    type_of_parent = None 
      
    if isinstance(tree.parent_relation, (Eventually, Historically, Once)):
        type_of_parent=type(tree.parent_relation)
    else:
        return non_delayed
    new_parent = None
    start_time = "0" if tree.parent_relation.get_start() is None else tree.parent_relation.get_start()
    stop_time = "" if tree.parent_relation.get_end() is None else tree.parent_relation.get_end()
    if len(non_delayed.get_rel_content()) == 1:
        new_parent = type_of_parent(f"{start_time}", f"{stop_time}NonDelayed")
    elif len(non_delayed.get_rel_content()) == 2:
        new_parent = type_of_parent(f"{start_time}", f"{stop_time}{non_delayed.get_rel_content()[1]}")
        
    tree.parent_relation = new_parent
    
    return tree

def add_referenced_nodes(flat_tree: RuleTree, nested_tree: RuleTree):
    """Often when a formula is nested, such as with a not, we only want to negate the predicate itself, not
    all of the predicates that are referenced in the negaated predicate. 
    I.e. If we have a formula like "not(b) AND B(b,c) AND C(c)", it should be represented as "NOT(B(b,c)) AND C(c)"
    

    Args:
        flat_tree (_type_): _description_
    """
    
    if isinstance(flat_tree.parent_relation, Implies):
        # Edge case where ONE STUPID RULE doesn't use time, and this circumvents the weird structure caused by this
        if len(flat_tree.relations) == 1:
            flat_tree.add_node(RuleTree(None, And()))
        flat_tree.relations = [add_referenced_nodes(flat_tree.relations[0], nested_tree.relations[0]), add_referenced_nodes(flat_tree.relations[1], nested_tree.relations[1])]
        return flat_tree

    all_atoms = []
    flat_tree_atoms = []
    
    queue = [nested_tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        if isinstance(curr.parent_relation, Atom) and curr.parent_relation not in all_atoms:
            all_atoms.append(curr.parent_relation)
        
        for child in curr.relations:
            queue.append(child)

    queue = [flat_tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        if isinstance(curr.parent_relation, Atom) and curr.parent_relation not in flat_tree_atoms:
            flat_tree_atoms.append(curr.parent_relation)
        
        for child in curr.relations:
            queue.append(child)
    
    only_non_referenced_atoms = [x for x in all_atoms if x not in flat_tree_atoms]
    
    
    if (flat_tree.parent_relation is None or isinstance(flat_tree.parent_relation, TimeModifier)) and len(flat_tree.relations) > 0 and isinstance(flat_tree.relations[0].parent_relation, BranchModifier):
        if not isinstance(flat_tree.relations[0].parent_relation, And):
            tmp_tree = RuleTree(None, And())
            tmp_tree.add_node(flat_tree.relations[0])
            flat_tree.relations[0] = tmp_tree
        for atom in only_non_referenced_atoms:
            flat_tree.relations[0].add_node(RuleTree(None, atom))
    elif isinstance(flat_tree.parent_relation, BranchModifier):
        for atom in only_non_referenced_atoms:
            flat_tree.add_node(RuleTree(None, atom))
    else:
        return flat_tree
    
    return flat_tree
    
def add_and_modifier_to_consequent(tree: RuleTree):
    """In some cases, the consequent of the rule will have multiple predicates, but no "and" connective.
    This function adds an "and" connective to the consequent if this is the case.

    Args:
        tree (RuleTree): _description_
    Returns:
        tree (RuleTree): The same tree, but with an "and" modifier added to the consequent if necessary
    """
    
    if not isinstance(tree.parent_relation, Implies):
        return tree

    assert len(tree.relations) == 2
    
    if isinstance(tree.relations[1].parent_relation, And):
        return tree
    if isinstance(tree.relations[1].parent_relation, TimeModifier) and len(tree.relations[1].relations) > 0 and tree.relations[1].relations[0].parent_relation is None:
        if tree.relations[1].relations[0].var is not None:
            tree.relations[1].relations[0].parent_relation = And()
            return tree
        else:
            and_node = RuleTree(None, And())
            and_node.relations = tree.relations[1].relations
            tree.relations[1].relation = [and_node]
        return tree

    return tree
def remove_r_exist_at_time(tree: RuleTree):
    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        deleted_num = 0
        for i in range(len(curr.relations)):
            child = curr.relations[i-deleted_num]
            if isinstance(child.parent_relation, Atom) and child.parent_relation.get_atom_content()[0].get_rel_name() == (NameSpace.RIOONTO.value + ":RexistAtTime"):
                del curr.relations[i-deleted_num]
                deleted_num += 1
            else:
                queue.append(child)
                
    
    return tree
def remove_and_modifiers(tree: RuleTree):
    # Handle case where root of tree is an "and"
    if isinstance(tree.parent_relation, And):
        tree.parent_relation = None
    return _remove_and_modifiers(tree)

def _remove_and_modifiers(tree: RuleTree):
    # IF there are two consecutive "and" modifiers, merge them together by moving the
    # content of the "inner" and to the "outer" and
    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        to_add = []
        if not isinstance(curr.parent_relation, And):
            [queue.append(x) for x in curr.relations]
            continue
        for i in range(len(curr.relations)):
            child = curr.relations[i]
            if isinstance(child.parent_relation, And):
                [to_add.append(x) for x in child.relations]
            else:
                to_add.append(child)
            queue.append(child)
        curr.relations = to_add
    return tree


def remove_branches_with_only_id(tree: RuleTree):
    return _remove_branches_with_only_id(tree)
def _remove_branches_with_only_id(tree: RuleTree):
    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        to_add = []
        for i in range(len(curr.relations)):
            child = curr.relations[i]
            if child.parent_relation is None and child.all_var == [] and child.exists_var == []:
                [to_add.append(x) for x in child.relations]
            else:
                to_add.append(child)
            queue.append(child)
        
        curr.relations = to_add
    return tree

def _flatten_tree(tree: RuleTree, already_seen: [Atom]):
    this_level_flat_tree = RuleTree(tree.var, tree.parent_relation, tree.exists_var, tree.all_var, tree.extra_info)
    # We consider one "level" to all predicates that are connected by the same logical operator (and, nor, or, imply)
    seen_this_level = []
    next_level_queue = []
    
    this_level_queue = [x for x in tree.relations]
    while len(this_level_queue) > 0:
        child = this_level_queue.pop(0)
        if  isinstance(child.parent_relation, BranchModifier) or child.parent_relation is None:
            next_level_queue.append(child)
        elif isinstance(child.parent_relation, Atom):
            if child.parent_relation in already_seen:
                continue
            seen_this_level.append(child)
            #for grandchild in child.relations:
            #    this_level_queue.append(grandchild)
        else:
            raise Exception(f"Unknown parent relation type, {child.parent_relation}")
    
    # Remove trees that reference the same predicate
    seen_this_level_no_dup = []
    seen_pred_this_level = []
    for item in seen_this_level:
        if item.parent_relation not in seen_pred_this_level:
            seen_this_level_no_dup.append(item)
            item.relations = []
            item.var = None
            item.parent_relation.un_reify()
            seen_pred_this_level.append(item.parent_relation)
    
    # Ensure correct formatting if there are multiple children to the "not" node
    tmp_tree = None    
    if isinstance(tree.parent_relation, Not) and len(seen_this_level_no_dup) > 1:
        new_tree = RuleTree(None, Or())
        for seen in seen_this_level_no_dup:
            new_tree.add_node(seen)
        this_level_flat_tree.add_node(new_tree)
        tmp_tree = this_level_flat_tree
        this_level_flat_tree = new_tree
    else:
        [this_level_flat_tree.add_node(x) for x in seen_this_level_no_dup]
        
    # TODO: This if-else checks if the current tree references an implication
    # If it does, then only the antecedant, and not the consequent, get's the old "already_seen" list
    # We do this because in some cases the consequent exclusively references objects in the antecedant, and by allowing
    # duplicated predicates in the consequent, we can ensure that original meaning of the antecedenant is preserved.
    # This is an illegal operation as of now, we need to ensure that the duplicated predicates reference the same arguments - change this
    if isinstance(tree.parent_relation, Implies):
        [already_seen.append(x) for x in seen_pred_this_level]
        #this_level_flat_tree.add_node(_flatten_tree(next_level_queue[0], already_seen))
        #this_level_flat_tree.add_node(_flatten_tree(next_level_queue[1], already_seen))
        print(tree.printNTree())
        print([str(x.parent_relation) for x in next_level_queue])
        print([str(x.parent_relation) for x in seen_this_level_no_dup])   
        this_level_flat_tree.add_node(_flatten_tree(next_level_queue[0], []))
        this_level_flat_tree.add_node(_flatten_tree(next_level_queue[1], []))
        consequent = this_level_flat_tree.relations[1]
        # Check if consequent is empty, if it is, then we clear the "already seen" list so that the consequent won't be empty
        # If this is true, it means that the consequent exclusively references objects in the antecedant
        if consequent.parent_relation is None and consequent.relations == [] and consequent.exists_var == [] and consequent.all_var == []:
            this_level_flat_tree.relations[1].add_node(RuleTree(None, And()))
            this_level_flat_tree.relations[1].relations[0].add_node(_flatten_tree(next_level_queue[1], []))
        # Sometimes if the consequent only refers back to previously defined predicates, then multiple 
        # consequences will exist. In this case, we need to add an "and" node to the consequent, and move all the 
        # consequences to children of the "and" node.
        elif len(this_level_flat_tree.relations[1].relations) > 1:
            tmp_nodes = this_level_flat_tree.relations[1].relations[1:]
            and_node = RuleTree(None, And())
            and_node.relations = tmp_nodes
            this_level_flat_tree.relations[1].relations = [and_node]
    else:
        [already_seen.append(x) for x in seen_pred_this_level]
        for child in next_level_queue:
            #this_level_flat_tree.add_node(_flatten_tree(child, already_seen))
            this_level_flat_tree.add_node(_flatten_tree(child, []))
            
    if tmp_tree is not None:
        return tmp_tree
    return this_level_flat_tree