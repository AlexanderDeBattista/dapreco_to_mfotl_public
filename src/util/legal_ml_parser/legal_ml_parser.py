import xml.etree.ElementTree as ET
from name_space import NameSpace

from atomic_concepts import Atom, Var, Function, Expression, Relation, After, Before, Ind
from rule.rule import Rule
from rule.gdpr import GDPR
    

def get_var_exist(statement: ET.Element) -> [str]:
    """Given an input or output, returns a list of variables that are existentially quantified in the expression

    Args:
        statement (ET.Element): _description_

    Returns:
        [str]: List of exisentially quantified variables in expression
    """    
    
    
    exists = statement.find(NameSpace.RULEML.value + "Exists")
    if exists is None:
        # Nothing is existentially quantified
        return []
    vars = []
    # Loop over existentially quantified variables
    for exist in exists:
        if exist.tag == (NameSpace.RULEML.value + "Var"):
            # Tag all variables in this phase as "defined now", as they might get referenced again later.
            vars.append(Var(exist.attrib["key"], defined_now=True))
    return vars

def parse_after(after_statement: ET.Element) -> After:
    t1, t2 = parse_time_statement(after_statement)
    return After(t1, t2)

def parse_before(before_statement: ET.Element) -> After:
    t1, t2 = parse_time_statement(before_statement)
    return Before(t1, t2)

def parse_ind(ind_statement: ET.Element):
    return Ind(ind_statement.text)

def parse_expression(expression: ET.Element) -> Expression:
    """ Given an expression, which necessarily contains a function, return a parsed expression object

    Args:
        expression (ET.Element): An expression tag

    Returns:
        Expression: An Expression object that contains the parsed expression
    """    
    fun_name = expression.find(NameSpace.RULEML.value + "Fun").attrib["iri"]
    arguments = []
    for arg in expression:
        if arg.tag == (NameSpace.RULEML.value + "Expr"):
            arguments.append(parse_expression(arg))
        elif arg.tag == (NameSpace.RULEML.value + "Var"):
            arguments.append(parse_var(arg))
        elif arg.tag == (NameSpace.RULEML.value + "Ind"):
            arguments.append(parse_ind(arg))        

    return Expression(Function(fun_name, arguments))

def parse_time_statement(before_statement: ET.Element) -> (str, str):
    """Given a time statement that concerns some relation between two timestamps,
    for example (BEFORE T1 T2) where T1 is a timestamp before T2, return the two timestamps

    Args:
        before_statement (ET.Element): A time statement defining some relation between two timestamps
    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        (str, str): A tuple of two timestamps, (t1, t2) 
    """    
    
    # A timestamp, t1 and t2, are either defined as expressions or variables. Handle each case accordingly
    if before_statement[0].tag == (NameSpace.RULEML.value + "Expr"):
        t1 = parse_expression(before_statement[0])
    
    elif before_statement[0].tag == (NameSpace.RULEML.value + "Var"):
        t1 = parse_var(before_statement[0])
    
    else:
        raise Exception(f"Unknown tag when parsing 'before', {before_statement[0].tag}")

    if before_statement[1].tag == (NameSpace.RULEML.value + "Expr"):
        t2 = parse_expression(before_statement[1])
    
    elif before_statement[1].tag == (NameSpace.RULEML.value + "Var"):
        t2 = parse_var(before_statement[1])
    
    else:
        raise Exception(f"Unknown tag when parsing 'before', {before_statement[1].tag}")
    
    return (t1, t2)

def parse_var(var_statement: ET.Element) -> Var:
    """A variable is either defined now, or reference an earlier defined variable. 
    Returns a Var object that correctly infers whether a variable got defined now or referenced.

    Args:
        var_statement (ET.Element): A var tag

    Returns:
        Var: A Var object with the correct "defined_now" attribute
    """    
    if "keyref" in var_statement.attrib:
        return Var(var_statement.attrib["keyref"], defined_now=False)
    else:
        return Var(var_statement.attrib["key"], defined_now=True)
    
def parse_atom(atom: ET.Element)-> Atom:
    """ Parses an atomic tag, and returns an Atom element

    Args:
        atom (ET.Element): An atomic tag

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        Atom: Parsed atomic statement
    """ 
    is_reified = False   
    # If an atom includes a "keyref" attribute, it indicates that it is a reified atom
    if "keyref" in atom.attrib:
        is_reified = True    
    new_atom = Atom(is_reified)
    if atom[0].tag == (NameSpace.RULEML.value + "Rel"):
        new_relation = Relation(atom.find(NameSpace.RULEML.value + "Rel").attrib["iri"])

        for item in atom:
            if item.tag == (NameSpace.RULEML.value + "Var"):
                new_relation.add_relation_content(parse_var(item))
            elif item.tag == (NameSpace.RULEML.value + "After"):
                new_relation.add_relation_content(parse_after(item))
            elif item.tag == (NameSpace.RULEML.value + "Before"):
                new_relation.add_relation_content(parse_before(item))
            elif item.tag == (NameSpace.RULEML.value + "Expr"):
                new_relation.add_relation_content(parse_expression(item))
            elif item.tag == (NameSpace.RULEML.value + "Ind"):
                new_relation.add_relation_content(parse_ind(item))
            elif item.tag != (NameSpace.RULEML.value + "Rel"):
                raise Exception(f"Error! Found foreign tag {item.tag}")

        new_atom.add_rel(new_relation)
    
    else:
        for item in atom:
            if item.tag == (NameSpace.RULEML.value + "Var"):
                new_atom.add_var(parse_var(item))
            elif item.tag == (NameSpace.RULEML.value + "After"):
                new_atom.add_after(parse_after(item))
            elif item.tag == (NameSpace.RULEML.value + "Before"):
                new_atom.add_before(parse_before(item))
            # TODO: Add support for equal tag
            #elif item.tag == (NameSpace.RULEML.value + "Equal"):
            #    new_atom.add_before(parse_before(item))
            elif item.tag == (NameSpace.RULEML.value + "Expr"):
                new_atom.add_expression(parse_expression(item))
            elif item.tag == (NameSpace.RULEML.value + "Ind"):
                new_atom.add_ind(parse_ind(item))
            elif item.tag != (NameSpace.RULEML.value + "Rel"):
                raise Exception(f"Error! Found foreign tag {item.tag}")
        

    return new_atom



def get_atomic_predicates(statement: ET.Element) -> [Atom]:
    """Given the either the "input" or "output" part of a rule, get a list of atomic predicates 

    Args:
        statement (ET.Element): Either the "input" or "output" part of a rule

    Returns:
        [Atom]: A list of atomic predicates
    """    
    atomic_predicates = []
    if statement.find(NameSpace.RULEML.value + "Exists") is not None:
        return get_atomic_predicates(statement.find(NameSpace.RULEML.value + "Exists"))
    
    if statement.find(NameSpace.RULEML.value + "Atom") is not None:
        atomic_predicates.append(parse_atom(statement.find(NameSpace.RULEML.value + "Atom")))
    if statement.find(NameSpace.RULEML.value + "Naf") is not None:
        #print("Ignoring negation as failure")
        atomic_predicates.append(parse_atom(statement.find(NameSpace.RULEML.value + "Naf").find(NameSpace.RULEML.value + "Atom")))
        atomic_predicates[-1].set_naf(True)

    and_tag = statement.find(NameSpace.RULEML.value + "And")
    if and_tag is None:
        return atomic_predicates
    
    for atom in and_tag:
        if atom.tag == (NameSpace.RULEML.value + "Atom"):
            atomic_predicates.append(parse_atom(atom))
        elif atom.tag == (NameSpace.RULEML.value + "Naf"):
                #print("ignoring negation as failure")
                atomic_predicates.append(parse_atom(atom.find(NameSpace.RULEML.value + "Atom")))
                atomic_predicates[-1].set_naf(True)
        else:
            print(f"Unknown tag {atom.tag}")
            
    return atomic_predicates
    
def parse_rule_advanced(statement: ET.Element) -> Rule:
    """ Parses an individual rule from the Dapreco knowledge base, which is represtented through LegalRuleMl.

    Args:
        statement (ET.Element): Expects a RuleML:Rule root
    """    
    # A rule in I/O logic should exist of first and "if" which implies the "then"
    
    # First fetch the existential quantifiers for "if" and "then"
    if_exist = get_var_exist(statement.find(NameSpace.RULEML.value + "if"))
    then_exist = get_var_exist(statement.find(NameSpace.RULEML.value + "then"))
    
    # Get atomic predicates for "if" and "then"
    atomic_if_predicates = get_atomic_predicates(statement.find(NameSpace.RULEML.value+"if"))
    atomic_then_predicates = get_atomic_predicates(statement.find(NameSpace.RULEML.value+"then"))
    
    # Construct a complete rule based on existential quantifiers and atomic predicates
    rule = Rule(if_exist, then_exist, atomic_if_predicates, atomic_then_predicates)

    return rule
    
def parse_rule(statement: ET.Element) -> str:
    """_summary_

    Args:
        statement (ET.Element): _description_

    Returns:
        str: _description_
    """    
    tag = statement.tag.split("}")[1]
    expression = tag + "( "
    
    for child in statement:
        to_append = ""
        if child.tag.split("}")[1] == "Var":
            if "key" in child.attrib:
                to_append = child.attrib["key"][1:]
            else:
                to_append = child.attrib["keyref"][1:]
        elif child.tag.split("}")[1] == "Rel":
            to_append = child.attrib["iri"]
        else:
            to_append = parse_rule(child)
            
        expression += to_append + ", "
    
    expression = expression[:-2]
    expression += ")"
    return expression

def get_legal_ml_root(filename: str) -> ET.Element:
    """Given an XML file, the root is returned

    Args:
        filename (str): path to XML file to open

    Returns:
        root (ET.Element): Root of xml 
    """  
    legal_ml_file = ET.parse(filename)
    root = legal_ml_file.getroot()
    
    return root
    

                
def get_rules_for_statement(statement_str, root: ET.Element) -> [Rule]:
    for child in root.findall(NameSpace.LRML.value + "Statements"):
        # Specifies which statement to parse
        if child.attrib["key"] == statement_str: #"statements83": #"statements15":#"statements244": #"statements7":
        # One statement is potentially made up of several Constitutive Statements
            rules = []
            for constitutive_statements in child.findall(NameSpace.LRML.value +"ConstitutiveStatement"):
                # One Constitutive Statement is potentially made up of several rules
                for rule in constitutive_statements:
                    # Pass rule to parser
                    rules.append(parse_rule_advanced(rule))
    return rules

def get_gdpr(root: ET.Element) -> GDPR:
    gdpr = GDPR()

    rule_interpretation_mapping = {}
    legal_reference_mapping = {}
    statement_to_legal_reference_mapping = {}

    for context in root.findall(NameSpace.LRML.value + "Context"):
        for in_scope in context:
            if not in_scope.tag == (NameSpace.LRML.value + "inScope"):
                continue
        
            rule_interpretation_mapping[in_scope.attrib["keyref"][1:]] = context.attrib["type"]


    for legal_reference in root.find(NameSpace.LRML.value + "LegalReferences"):
        legal_reference_mapping[legal_reference.attrib["refersTo"]] = legal_reference.attrib["refID"]
        ref_id_split = legal_reference.attrib["refID"].split("__")
        
        if len(ref_id_split) == 2:
            gdpr.add_paragraph(ref_id_split[0], ref_id_split[1])
        elif len(ref_id_split) == 5:
            gdpr.add_list_point(ref_id_split[0], ref_id_split[1], ref_id_split[3], ref_id_split[4])

    for association in root.find(NameSpace.LRML.value + "Associations"):
        if not association.tag == (NameSpace.LRML.value + "Association"):
            continue
        
        if  association.find(NameSpace.LRML.value + "toTarget") is None or  association.find(NameSpace.LRML.value + "appliesSource") is None:
            continue
        statement = association.find(NameSpace.LRML.value + "toTarget").attrib["keyref"][1:]
        legal_reference = association.find(NameSpace.LRML.value + "appliesSource").attrib["keyref"][1:]
        
        statement_to_legal_reference_mapping[statement] = legal_reference

    for statements in root.findall(NameSpace.LRML.value + "Statements"):
        formulas_in_statement = []
        for constitutive_statements in statements.findall(NameSpace.LRML.value +"ConstitutiveStatement"):
            # One Constitutive Statement is potentially made up of several rules
            for rule in constitutive_statements:
                # Pass rule to parser
                parsed_rule = parse_rule_advanced(rule)     
                statement_formula_id = constitutive_statements.attrib["key"]
                rule_type = rule_interpretation_mapping[statement_formula_id]
                print(rule_type)
                formulas_in_statement.append([parsed_rule, statement_formula_id, rule_type])
        
        statement_id = statements.attrib["key"]
        
        if not statement_id in statement_to_legal_reference_mapping:
            continue
        
        gdpr_id = legal_reference_mapping[statement_to_legal_reference_mapping[statement_id]]
        if gdpr_id is None:
            continue
        
        gdpr_id_list = gdpr_id.split("__")
        for formula_in_statement in formulas_in_statement:
            if len(gdpr_id_list) == 2:
                gdpr.add_statement(gdpr_id_list[0], gdpr_id_list[1], None, None, formula_in_statement)
            else :
                gdpr.add_statement(gdpr_id_list[0], gdpr_id_list[1], gdpr_id_list[3], gdpr_id_list[4], formula_in_statement)
    return gdpr
    
                    
                    
if __name__ == "__main__":
    statements_by_ontology = {}
    root = get_legal_ml_root("rioKB_GDPR.xml")
    
    print(get_rules_for_statement("statements83", root)[0])
    print(get_gdpr(root).articles)