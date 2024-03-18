import networkx as nx
import matplotlib.pyplot as plt

from name_space.name_space import NameSpace
from rule.rule import Rule
from data_structure.rule_tree.rule_tree import RuleTree
from data_structure.rule_tree.branch_modifier import And, Once, Eventually, Implies, Always, Historically
from atomic_concepts import Relation, Atom, Before, After, Expression, Var, Function
from util.legal_ml_parser.legal_ml_parser import get_legal_ml_root, get_rules_for_statement, get_gdpr

class RuleGraph():
    def __init__(self) -> None:
        self.graph = nx.DiGraph()
    

class TemporalRuleGraph(RuleGraph):
    
    def __init__(self) -> None:
        super().__init__()
        
    def add_time_identifier(self, time_identifier: str):
        self.graph.add_node(time_identifier, label="TimeIdentifier")
    
    def add_temporal_identifier(self, temporal_identifier: str):
        self.graph.add_node(temporal_identifier, label="TemporalIdentifier")
    
    def add_edge_temporal_and_time_identfier(self, temporal_identifier: str, time_identifier: str):
        self.graph.add_edge(temporal_identifier, time_identifier, label="TimeLinkedToTemporal")
    
    def add_edge_before_time_relation(self, time_identifier1: str, time_identifier2: str, if_or_then: str):
        self.graph.add_edge(time_identifier1, time_identifier2, label="TimeRelationBefore", if_or_then=if_or_then)
    
    def add_edge_after_time_relation(self, time_identifier1: str, time_identifier2: str, if_or_then: str):
        self.graph.add_edge(time_identifier1, time_identifier2, label="TimeRelationAfter", if_or_then=if_or_then)
    
    def add_function_edge(self, function_input: str, function_output: str):
        if not self.graph.has_node(function_output):
            self.graph.add_node(function_output)
        self.graph.add_edge(function_input, function_output, label=f"function")
    
    def add_implication(self, implication_name: str, antecedent: str, consequent: str):
        self.graph.add_node(implication_name, label="Implication")
        self.graph.add_edge(implication_name, antecedent, label="ImplicationAntecedent")
        self.graph.add_edge(implication_name, consequent, label="ImplicationConsequent")
    
    def add_and_node_and_edges(self, and_name: str, edges: [Var]):
        self.graph.add_node(and_name, label="And")
        for edge in edges:
            self.graph.add_edge(and_name, edge, label="AndEdge")
    
def _extract_temporal_operators(atoms: [Atom], exist_at_time_atoms: [], time_relations: [], obliged_at_time_atoms: []) -> None:
    for atom in atoms:
        if isinstance(atom.get_atom_content()[0], Relation):
            rel_name = atom.get_atom_content()[0].get_rel_name()
        
            if rel_name == (NameSpace.RIOONTO.value + ":RexistAtTime"):
                exist_at_time_atoms.append(atom)
            
            # TODO:Assume that "Obliged" and "Permitted" *SOMETIMES* defines a new timestamp
            # Very weird that this seems to be the case, but it is
            if rel_name in [(NameSpace.RIOONTO.value+ ":Obliged"), (NameSpace.RIOONTO.value+ ":Permitted"), (NameSpace.RIOONTO.value+ ":atTime")] and not atom.is_reified():
                obliged_at_time_atoms.append(atom)
        
        if isinstance(atom.get_atom_content()[0], (Before, After)):
            time_relations.append(atom)
def _add_time_identifier_and_time_stamp(new_graph: nx.DiGraph, exist_at_time_atoms: []):
    for exist_at_time_atom in exist_at_time_atoms:
        time_identifier = exist_at_time_atom.get_atom_content()[0].get_rel_content()[1]
        temporal_identifier = exist_at_time_atom.get_atom_content()[0].get_rel_content()[0]
        new_graph.add_time_identifier(time_identifier)
        new_graph.add_temporal_identifier(temporal_identifier)
        new_graph.add_edge_temporal_and_time_identfier(temporal_identifier, time_identifier)
        
def _add_time_relation(new_graph: nx.DiGraph, time_relations: [], if_or_then: str):
    for time_relation in time_relations:
        time_identifier1 = time_relation.get_atom_content()[0].t1
        time_identifier2 = time_relation.get_atom_content()[0].t2
        
        # Is an expression (containing a function)
        if isinstance(time_identifier2, Expression):
            time_identifier2 = time_identifier2.fun
            function_name = time_identifier2.fun_name
            variable = time_identifier2.arguments[0]
            ind_val = time_identifier2.arguments[1]
            
            new_graph.add_function_edge(variable, time_identifier2)
            
        if isinstance(time_relation.get_atom_content()[0], Before):
            new_graph.add_edge_before_time_relation(time_identifier1, time_identifier2, if_or_then)
        elif isinstance(time_relation.get_atom_content()[0], After):
            new_graph.add_edge_after_time_relation(time_identifier1, time_identifier2, if_or_then)
    
def rule_to_temporal_graph(rule: Rule) -> TemporalRuleGraph:
    new_graph = TemporalRuleGraph()
    if_exist_at_time_atoms = []
    if_obliged_at_time_atoms = []
    if_time_relations = []
    then_exist_at_time_atoms = []
    then_obliged_at_time_atoms = []
    then_time_relations = []
    
    _extract_temporal_operators(rule.if_atoms, if_exist_at_time_atoms, if_time_relations, if_obliged_at_time_atoms)
    _extract_temporal_operators(rule.then_atoms, then_exist_at_time_atoms, then_time_relations, then_obliged_at_time_atoms)
    # The following loop might look a bit funny, but it is needed in the cases where the consequent part 
    # defines a time relation between two timestamps that got defined in the antecedent part.
    # If such a time relation exists, then we duplicate the predicate where the timestamp was defined, to
    # the consequent part.
    # An example: This (ExistAtTime(a1, t1) AND ExistAtTime(a2,t2) AND before(t2, t1)) IMPLIES before(t2, function(add_time(t1, 1Month)))
    # Becomes this: (ExistAtTime(a1, t1) AND ExistAtTime(a2,t2) AND before(t2, t1)) IMPLIES (ExistAtTime(a2,t2) AND before(t2, function(add_time(t1, 1Month))))
    for time_relation in then_time_relations:
        # Extract the first timestamp identifier of all time relations in the consequent part
        time_identifier1 = time_relation.get_atom_content()[0].t1
        # If the first timestamp identifier is not defined in the antecedent part, then we can skip this
        if True not in [time_identifier1 in x for x in (if_exist_at_time_atoms+if_obliged_at_time_atoms)]:
            continue
        # Find the (hopefully only one) atom where this timestamp identifier is defined
        atom_where_defined = []
        for atom in (if_exist_at_time_atoms + if_obliged_at_time_atoms):
            if time_identifier1 in atom:
                atom_where_defined.append(atom)
        assert len(atom_where_defined) == 1
        atom_where_defined = atom_where_defined[0]
        
        # Duplicate the atom by adding it to the appropriate list
        if atom_where_defined in if_exist_at_time_atoms:
            then_exist_at_time_atoms.append(atom_where_defined)
        elif atom_where_defined in if_obliged_at_time_atoms:
            then_obliged_at_time_atoms.append(atom_where_defined)
        else:
            raise Exception("Atom not found in 'if' part of expression")
    
    _add_time_identifier_and_time_stamp(new_graph, if_exist_at_time_atoms)
    _add_time_identifier_and_time_stamp(new_graph, then_exist_at_time_atoms)
    _add_time_identifier_and_time_stamp(new_graph, if_obliged_at_time_atoms)
    _add_time_identifier_and_time_stamp(new_graph, then_obliged_at_time_atoms)

    _add_time_relation(new_graph, if_time_relations, "if")
    _add_time_relation(new_graph, then_time_relations, "then")
    
    if_temporal_identifiers = [x.get_atom_content()[0].get_rel_content()[0] for x in (if_exist_at_time_atoms+if_obliged_at_time_atoms)]
    then_temporal_identifiers = [x.get_atom_content()[0].get_rel_content()[0] for x in (then_exist_at_time_atoms+then_obliged_at_time_atoms)]
    
    conjunction_node_if = None
    conjunction_node_then = None
    # If the if or then part contains more than one temporal identifier, then we need to add a conjunction node
    if len(if_temporal_identifiers) > 1:
        conjunction_node_if = "ConjuctionOfIf"
        new_graph.add_and_node_and_edges(conjunction_node_if, if_temporal_identifiers)
    elif len(if_temporal_identifiers) == 1:
        conjunction_node_if = if_temporal_identifiers[0]
        
    if len(then_temporal_identifiers) > 1:
        conjunction_node_then = "ConjuctionOfThen"
        new_graph.add_and_node_and_edges(conjunction_node_then, then_temporal_identifiers)
    elif len(then_temporal_identifiers) == 1:
        conjunction_node_then = then_temporal_identifiers[0]
    
    if conjunction_node_if is not None and conjunction_node_then is not None:
        new_graph.add_implication("IfThenImplication", conjunction_node_if, conjunction_node_then)
        
    return new_graph
    
def recursive_evaulation_of_graph(graph: nx.DiGraph, root, if_or_then: str = "if", top_of_tree: bool = True) -> RuleTree:
    """Given a graph and a root, return the corresponding rule tree of the graph.
    This method assumes that the initial root is a "IfThenImplication" node, and that this implication can 
    points to a "ConjuctionOfIf", a "ConjuctionOfThen", or temporal identifier node node. 
    Conjuctions can point to  temporal identifiers, which in turn points to timestamps.
    Timestamps may point to relations between themselves, or to functions which define new timestamps.

    Assume we are in "if" part of the expression, unless otherwise specified.
    Args:
        graph (nx.DiGraph): _description_
        root (_type_): _description_
        if_or_then (str, optional): _description_. Defaults to None.

    Raises:
        Exception: _description_

    Returns:
        RuleTree: _description_
    """    
    new_tree = None
    # Check what type of node we are dealing with
    if root == "IfThenImplication":
        new_tree = RuleTree(None, Implies())
        # If we have not defined if or then yet (which part of the expression we are in), then we do it now
        if_str = if_or_then
        then_str = if_or_then
        if top_of_tree is True:
            if_str = "if"
            then_str = "then"
        # Recursively evaluate the antecedent and consequent
        antecedent = recursive_evaulation_of_graph(graph, [x for x in graph.out_edges(root, data=True) if x[2]["label"]=="ImplicationAntecedent"][0][1], if_str, False)
        consequent = recursive_evaulation_of_graph(graph, [x for x in graph.out_edges(root, data=True) if x[2]["label"]=="ImplicationConsequent"][0][1], then_str, False)
        # Add the antecedent and consequent to the new tree in this particular order (antecedent first, then consequent)
        new_tree.add_node(antecedent)
        new_tree.add_node(consequent)
        
    elif root in ["ConjuctionOfIf", "ConjuctionOfThen"]:
        new_tree = RuleTree(None, And())
        # Append all children to the "and" tree
        for child in graph.successors(root):
            new_tree.add_node(recursive_evaulation_of_graph(graph, child, if_or_then, False))
    # We have reached a temporal identifier, needs special care
    elif isinstance(root, Var):
        
        temporal_id_tree = RuleTree(root, None)
        # Retrieve timestamp connected to this temporal identifier
        time_stamp = [x for x in graph.out_edges(root, data=True) if x[2]["label"] == "TimeLinkedToTemporal"][0][1]
        time_stamp_edges = graph.out_edges(time_stamp, data=True)
        # One timestamp might have multiple time relations, so we want to determine if we are in the "if" or "else" part
        time_stamp_before_edges = [x for x in time_stamp_edges if (
            x[2]["label"] == "TimeRelationBefore" and 
            x[2]["if_or_then"] == if_or_then)
        ]
        time_stamp_after_edges = [x for x in time_stamp_edges if (
            x[2]["label"] == "TimeRelationAfter" and 
            x[2]["if_or_then"] == if_or_then)
        ]
        # Excplicitly assume that time-zero/now-time is equal to t1
        t1_var = Var(":t1")
        # If we have a "before" relation, then we want to add a "once" node
        if len(time_stamp_before_edges) == 1 and len(time_stamp_after_edges) == 0:
            extra_info= f"{time_stamp_before_edges[0][0]} {time_stamp_before_edges[0][2]['label']} {time_stamp_before_edges[0][1]}"
            if time_stamp_before_edges[0][0].defined_now:
                if time_stamp_before_edges[0][1]:
                    new_tree = RuleTree(None, Historically(None, None), extra_info=extra_info)
                elif isinstance(time_stamp_before_edges[0][1], Function) and t1_var in time_stamp_before_edges[0][1]:
                    new_tree = RuleTree(None, Historically(Var(":0"), time_stamp_before_edges[0][1].arguments[1]), extra_info=extra_info)
                else:
                    new_tree = RuleTree(None, Historically(time_stamp_before_edges[0][0], time_stamp_before_edges[0][1]), extra_info=extra_info)
            else:
                if time_stamp_before_edges[0][1]:
                    new_tree = RuleTree(None, Once(None, None), extra_info=extra_info)
                elif isinstance(time_stamp_before_edges[0][1], Function) and t1_var in time_stamp_before_edges[0][1]:
                    new_tree = RuleTree(None, Once(Var(":0"), time_stamp_before_edges[0][1].arguments[1]), extra_info=extra_info)
                else:
                    new_tree = RuleTree(None, Once(time_stamp_before_edges[0][0], time_stamp_before_edges[0][1]), extra_info=extra_info)
            new_tree.add_node(temporal_id_tree)
        
        # If we have an "after" relation, then we want to add an "eventually" node
        elif len(time_stamp_before_edges) == 0 and len(time_stamp_after_edges) == 1:    
            extra_info=f"{time_stamp_after_edges[0][0]} {time_stamp_after_edges[0][2]['label']} {time_stamp_after_edges[0][1]}"
            if time_stamp_after_edges[0][0].defined_now:     
                if time_stamp_after_edges[0][1] == t1_var:
                    new_tree = RuleTree(None, Always(None, None),extra_info=extra_info)
                elif isinstance(time_stamp_after_edges[0][1], Function) and t1_var in time_stamp_after_edges[0][1]:
                    new_tree = RuleTree(None, Always(Var(":0"), time_stamp_after_edges[0][1].arguments[1]),extra_info=extra_info)
                else:
                    new_tree = RuleTree(None, Always(time_stamp_after_edges[0][1], time_stamp_after_edges[0][0]),extra_info=extra_info)
            else:
                if time_stamp_after_edges[0][1] == t1_var:
                    new_tree = RuleTree(None, Eventually(None, None), extra_info=extra_info)
                elif isinstance(time_stamp_after_edges[0][1], Function) and t1_var in time_stamp_after_edges[0][1]:
                    new_tree = RuleTree(None, Eventually(Var(":0"), time_stamp_after_edges[0][1].arguments[1]),extra_info=extra_info)
                else:
                    new_tree = RuleTree(None, Eventually(time_stamp_after_edges[0][1], time_stamp_after_edges[0][0]),extra_info=extra_info)
            new_tree.add_node(temporal_id_tree)
       
        # Rare case when we have both a before and after relation for the same timestamp
        elif len(time_stamp_after_edges) == 1 and len(time_stamp_before_edges) == 1:
            extra_info = f"{time_stamp_before_edges[0][0]} {time_stamp_before_edges[0][2]['label']} {time_stamp_before_edges[0][1]} AND {time_stamp_after_edges[0][0]} {time_stamp_after_edges[0][2]['label']} {time_stamp_after_edges[0][1]}"
            new_tree = RuleTree(None, Eventually(Var(":0"), time_stamp_before_edges[0][1].arguments[1]), extra_info=extra_info)
            new_tree.add_node(temporal_id_tree)
        # If neither before nor after, then we assume that there is no time-relation associated to this temporal identifier's timestamps
        elif len(time_stamp_before_edges) == 0 and len(time_stamp_after_edges) == 0:
            new_tree = temporal_id_tree
        else:
            raise Exception("Unknown time relation")
        
    else:
        raise Exception(f"Unknown node type {root}")
    
    return new_tree
    
def get_temporal_rule_tree_str(rule_tree: RuleTree):
    assert isinstance(rule_tree, RuleTree)
    parent_rel = rule_tree.parent_relation
    tree_var = rule_tree.var
    if isinstance(parent_rel, And):
        return f"And({', '.join([get_temporal_rule_tree_str(x) for x in rule_tree.relations])})"
    elif isinstance(parent_rel, (Once, Eventually)):
        assert len(rule_tree.relations) == 1
        return f"{parent_rel}({get_temporal_rule_tree_str(rule_tree.relations[0])})"
    elif isinstance(parent_rel, Implies):
        return f"({get_temporal_rule_tree_str(rule_tree.relations[0])}) IMPLIES ({get_temporal_rule_tree_str(rule_tree.relations[1])})"
    elif isinstance(parent_rel, Atom):
        return str(parent_rel)
    elif isinstance(tree_var, Var):
        return str(tree_var)
    else:
        raise Exception(f"Unknown type {parent_rel}")

def get_temporal_rule_graph_structure(rule_graph: nx.DiGraph, rule: Rule) -> RuleTree:
    time_relations = []
    for node_from, node_to, d in rule_graph.edges(data=True):
        if d['label'] == "TimeRelationBefore":
            time_relations.append((node_from, node_to, "Before"))
        elif d['label'] == "TimeRelationAfter":
            time_relations.append((node_from, node_to, "After"))
    
    time_relations_str = []
    for time_relation in time_relations:
        if time_relation[2] == "Before":
            time_relations_str.append(f"{time_relation[0]} <= {time_relation[1]}")
        elif time_relation[2] == "After":
            time_relations_str.append(f"{time_relation[0]} >= {time_relation[1]}")
        else:
            raise Exception(f"Unknown time relation {time_relation[2]}")
         
    
    root = [node for node in rule_graph.nodes if rule_graph.in_degree(node) == 0]
    assert len(root) == 1
    root = root[0]
    rule_tree = recursive_evaulation_of_graph(rule_graph, root)
    
    # Add existential and universal quantifier
    exist_at_time = []
    obliged_at_time = []
    all_atoms = rule.if_atoms.copy() + rule.then_atoms.copy()
    _extract_temporal_operators(all_atoms, exist_at_time, [], obliged_at_time)
    for atom in exist_at_time + obliged_at_time:
        if atom.get_atom_content()[0].get_rel_content()[1] in (rule.if_exist) and atom.get_atom_content()[0].get_rel_content()[1] not in rule_tree.exists_var:
            rule_tree.exists_var.append(atom.get_atom_content()[0].get_rel_content()[1])
        if atom.get_atom_content()[0].get_rel_content()[1] in (rule.then_exist) and atom.get_atom_content()[0].get_rel_content()[1] not in rule_tree.exists_var:
            if len(rule_tree.relations) == 0:
                # In some rare cases the consequent part is the only temporally quantified part of the expression.
                # Such as in statements124
                rule_tree.exists_var.append(atom.get_atom_content()[0].get_rel_content()[1])
            # If we have a "then" relation, we need to add it to the "then"/consequent part of the tree
            else:
                rule_tree.relations[1].exists_var.append(atom.get_atom_content()[0].get_rel_content()[1])
        elif atom.get_atom_content()[0].get_rel_content()[1] not in rule_tree.exists_var and atom.get_atom_content()[0].get_rel_content()[1] not in rule_tree.all_var:
            rule_tree.all_var.append(atom.get_atom_content()[0].get_rel_content()[1])
    return rule_tree

def rule_to_temporal_tree(rule: Rule) -> RuleTree:
    temp_rule_graph = rule_to_temporal_graph(rule)
    if len(temp_rule_graph.graph.nodes) == 0:
        return RuleTree(None, None)
    temporal_tree = get_temporal_rule_graph_structure(temp_rule_graph.graph, rule)
    return temporal_tree

if __name__ == "__main__":
    root = get_legal_ml_root("rioKB_GDPR.xml")
    rules = get_rules_for_statement("statements65", root) #get_rules_for_statement("statements37", root)
    
    temp_rule_graph = rule_to_temporal_graph(rules[0])
    temporal_tree = get_temporal_rule_graph_structure(temp_rule_graph.graph, rules[0])
    print(temporal_tree.printNTree())
    pos = nx.shell_layout(temp_rule_graph.graph)

    nx.draw_networkx(temp_rule_graph.graph, pos)

    edge_labels = dict([((n1, n2), d['label'])
                    for n1, n2, d in temp_rule_graph.graph.edges(data=True)])

    nx.draw_networkx_edge_labels(temp_rule_graph.graph, pos, font_size=6, edge_labels=edge_labels)
    plt.show()
    