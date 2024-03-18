from atomic_concepts.interfaces import AtomContent
from atomic_concepts import Var, Atom
from data_structure.rule_tree.branch_modifier import BranchModifier, TimeModifier, Implies, And, Or, Not
from name_space.name_space import NameSpace

class RuleTree():
    def __init__(self, var: Var, parent_relation: Atom, exists_var=[], all_var=[], extra_info=None) -> None:
        self.relations = []
        self.var = var
        self.parent_relation = parent_relation
        self.leaf = False
        if len(exists_var) == 0:
            self.exists_var = []
        else:
            self.exists_var = exists_var
        
        if len(all_var) == 0:
            self.all_var = []
        else:
            self.all_var = all_var
            
        if extra_info is not None:
            self.extra_info = extra_info
        else:
            self.extra_info = None
            
    def add_node(self, node):
        assert(isinstance(node, RuleTree))
        self.relations.append(node)
    
    def add_exists_var(self, var: Var):
        if var not in self.exists_var:
            self.exists_var.append(var)
    def add_all_var(self, var: Var):
        self.all_var.append(var)
        
    def set_is_leaf(self):
        self.leaf = True
        
    def is_leaf(self):
        return self.leaf
        
    def tree_size(self) -> int:
        relations_below = sum([x.tree_size() for x in self.relations])
        return 1 + len(self.relations) + relations_below

    def printNTree(self) -> str:
        return self._printNTree(0, [True] * (self.tree_size()), False)

        
    # Function to print the
    # N-ary tree graphically
    # Code borrowed from https://www.geeksforgeeks.org/print-n-ary-tree-graphically/
    def _printNTree(self, depth, flag, isLast) -> str:
        this_str = ""
        exists_string = ""
        always_string = ""
        extra_info = ""
        if self.extra_info is not None:
            extra_info = self.extra_info
        if len(self.exists_var) > 0:
            exists_string = "(EXISTS " + " . ".join([str(x) for x in self.exists_var])+")"
        var_string = ""
        if len(self.all_var) > 0:
            always_string = "(ALL " + " . ".join([str(x) for x in self.all_var])+")"
        if self.var is not None:
            var_string = str(self.var)
            
            
        
        relation_string = ""
        if self.parent_relation is not None:
            relation_string = str(self.parent_relation)
        # Loop to print the depths of the
        # current node
        for i in range(1, depth):
            # Condition when the depth
            # is exploring
            if flag[i]:
                this_str+= "|    "
            
            # Otherwise print
            # the blank spaces
            else:
                this_str += "     "
        
        # Condition when the current
        # node is the root node
        if depth == 0:
            this_str += f"{always_string} {exists_string} {var_string} {relation_string} {extra_info}\n"
        
        # Condition when the node is
        # the last node of
        # the exploring depth
        elif isLast:
            this_str += f"+--- {always_string} {exists_string} {var_string} {relation_string} {extra_info}\n"
            # No more childrens turn it
            # to the non-exploring depth
            flag[depth] = False
        else:
            this_str += f"+--- {always_string} {exists_string} {var_string} {relation_string} {extra_info}\n"

        it = 0
        for i in self.relations:
            it+=1
            
            # Recursive call for the
            # children nodes
            this_str += i._printNTree(depth + 1, flag, it == (len(self.relations)))
        flag[depth] = True
        
        return this_str

    def compare_tree_structure(self, other_tree):
        assert isinstance(other_tree, RuleTree)
        
        if len(self.relations) != len(other_tree.relations):
            return False
        if self.parent_relation != other_tree.parent_relation:
            return False
        for i in range(len(self.relations)):
            if not self.relations[i].compare_tree_structure(other_tree.relations[i]):
                return False
        
        return True

    def get_printable_flat_tree(self):
        flat_tree_str = self._get_printable_flat_tree([])
        flat_tree_str = flat_tree_str.replace("AND AND", "AND").replace("AND  AND", "AND").replace("AND   AND", "AND").replace("AND )", ")")
        return flat_tree_str
    
    def _get_printable_flat_tree(self, already_seen=[]):
        if isinstance(self.parent_relation, Atom) and self.parent_relation.get_atom_content()[0].get_rel_name() == (NameSpace.RIOONTO.value+":RexistAtTime"):
            return ""
        this_str = ""
        is_modifier = False
        if len(self.exists_var) > 0:
            this_str += "".join([f"EXISTS {str(x)} . " for x in self.exists_var])
        
        if isinstance(self.parent_relation, BranchModifier):
            if isinstance(self.parent_relation, Implies):
                assert len(self.relations) == 2
                return f"{this_str} ({self.relations[0]._get_printable_flat_tree(already_seen)}) IMPLIES ({self.relations[1]._get_printable_flat_tree([])})"
            elif isinstance(self.parent_relation, And):
                return f"{this_str}({' AND '.join([x._get_printable_flat_tree(already_seen) for x in self.relations])})"
            elif isinstance(self.parent_relation, Or):
                return f"{this_str}({') OR ('.join([x._get_printable_flat_tree(already_seen) for x in self.relations])})"
            else:
                is_modifier = True
                this_str += str(self.parent_relation) + "( "
        elif isinstance(self.parent_relation, Atom):
            if self.parent_relation not in already_seen:
                already_seen.append(self.parent_relation)
                this_str += str(self.parent_relation) + " AND "
        elif self.parent_relation == None:
            rel_strs = []
            for relation in self.relations:
                tmp_str = relation._get_printable_flat_tree(already_seen)
                if tmp_str != "":
                    rel_strs.append(tmp_str)
            
            # In some rare instances, there will be no logical connective at the root of the temporal tree
            # but instead just a collection of atoms. We want to "and" these together.
            if len(rel_strs) > 1:
                return f"({this_str} {' AND '.join(rel_strs)})"
            elif len(rel_strs) == 1:
                return f"({this_str} {rel_strs[0]})"
            else:
                return this_str
        else:
            raise Exception(f"Unknown parent relation type: {type(self.parent_relation)}")
        for i in range(len(self.relations)):
            child = self.relations[i]
            if child.parent_relation == self.parent_relation and child.var != self.var and len(child.relations) == 1:
                child = child.relations[0]
            child_str = child._get_printable_flat_tree(already_seen)
            this_str += child_str
        if is_modifier:
            this_str += ")"
        return this_str
    
    def get_printable_tree_with_duplicates(self) -> str:
        """Assumes a "flat" tree, where the only nesting is either logical connectives or temporal modifiers. 

        Returns:
            _type_: _description_
        """
        this_str = "".join([f" FORALL {var_val} . " for var_val in self.all_var])
        if Var(":t1") not in self.exists_var:
            return this_str + f"ALWAYS({self._get_printable_tree_with_duplicates()})"
        return this_str + f"{self._get_printable_tree_with_duplicates()}"
    
    def _get_printable_tree_with_duplicates(self) -> str:
        if isinstance(self.parent_relation, Atom) and self.parent_relation.get_atom_content()[0].get_rel_name() == (NameSpace.RIOONTO.value+":RexistAtTime"):
            return ""
        this_str = ""
        if len(self.exists_var) > 0:
            this_str += ""
            this_str += "".join([f" EXISTS {str(x)} . " for x in self.exists_var])
        if isinstance(self.parent_relation, BranchModifier):
            if isinstance(self.parent_relation, Implies):
                assert len(self.relations) == 2
                return f"{this_str} ({self.relations[0]._get_printable_tree_with_duplicates()}) IMPLIES ({self.relations[1]._get_printable_tree_with_duplicates()})"
            elif isinstance(self.parent_relation, And):
                children_str = [f"({x._get_printable_tree_with_duplicates()})"for x in self.relations if x._get_printable_tree_with_duplicates() != ""]
                if len(children_str) == 0:
                    return f"{this_str}"
                return this_str + " AND ".join(children_str)
            elif isinstance(self.parent_relation, Or):
                return this_str + " OR ".join([f"({x._get_printable_tree_with_duplicates()})"for x in self.relations])
            elif isinstance(self.parent_relation, Not):
                
                return this_str + " NOT " + "".join([f"({x._get_printable_tree_with_duplicates()})"for x in self.relations])
        if isinstance(self.parent_relation, TimeModifier):
            extra_time_relation_info = ""
            if self.extra_info is not None:
                split_info = self.extra_info.split(" ")
                if "fun" in split_info[-2]:
                    to_add = split_info[-1][:-2]
                    self.parent_relation.set_start(f"0")
                    self.parent_relation.set_end(f"{to_add}")
                extra_time_relation_info = f"({self.extra_info})"
            return f"{this_str} {self.parent_relation} ({''.join([x._get_printable_tree_with_duplicates() for x in self.relations])})"
        elif isinstance(self.parent_relation, Atom):
            self.parent_relation.un_reify()
            return this_str +  str(self.parent_relation)
        else:
            this_str += "".join([f"({x._get_printable_tree_with_duplicates()})"for x in self.relations])
            
        return this_str

    def get_whyenf_sig(self):
        seen_predicates = []
        sig_str = ""
        queue = [self]
        while len(queue) > 0:
            curr = queue.pop(0)
            for child in curr.relations:
                queue.append(child)
            if not isinstance(curr.parent_relation, Atom):
                continue
            pred_name = curr.parent_relation.get_atom_content()[0].get_rel_name() 
            if pred_name in seen_predicates:
                continue
            seen_predicates.append(pred_name)
            
            pred_content = curr.parent_relation.get_atom_content()[0].get_rel_content()
            
            sig_str += f"{pred_name}({', '.join([str(x)+':string' for x in pred_content])})\n"
            
        return sig_str
            