from util import to_camel_case, fixup

class RuleObj:
    
    def __init__(self, jsonObj, jsObj): 
        self.name = jsonObj["name"]
        self.entity = jsonObj["entity"]
        self.ruleType = jsonObj["ruleType"]
        self.jsonObj =jsonObj
        self.jsObj = jsObj
        self.sqlObj = None
        
    def __str__(self):
        # switch statement for each ruleType
        return f"Name: {self.name} Entity: {self.entity} RuleType: {self.ruleType}"
    
    
    def ruleTypes(ruleObj: object):
        """

        Args:
            RuleObj (object): _description_
        """
        j = ruleObj.jsonObj
        isActive = j["isActive"]
        # No need to print inactive rules
        if isActive == False:
            return
        name = j["name"]
        entity = ""
        if "entity" in j:
            entity = to_camel_case(j["entity"])
        ruleType = ""
        if "ruleType" in j:
            ruleType = j["ruleType"]
        title =""
        if "title" in j:
            title = j["title"]
        funName = "fn_" + name.split(".")[0]
        comments = j["comments"]
        appliesTo = ""
        if "appliesTo" in j:
            appliesTo = j["appliesTo"]
        
        # Define a function to use in the rule 
        ruleJSObj = None if ruleObj.jsObj is None else fixup(ruleObj.jsObj)
        if ruleJSObj is not None:
            funName =  f"fn_{name}"
            print(f"def {funName}(row: models.{entity}, old_row: models.{entity}, logic_row: LogicRow):")
            ## print("     if LogicRow.isInserted():")
            if len(appliesTo) > 0:
                print(f"     #AppliesTo: {appliesTo}")
            print("     " + fixup(ruleObj.jsObj))
        
        print("'''")
        print(f"     RuleType: {ruleType}")
        print(f"     Title: {title}")
        print(f"     Name: {name}")
        print(f"     Entity: {entity}")
        print(f"     Comments: {comments}")
        print("'''")
        if ruleType == "sum":
            attr = j["attribute"]
            roleToChildren = to_camel_case(j["roleToChildren"]).replace("_","")
            childAttr = j["childAttribute"]
            qualification = j["qualification"]
            print(f"Rule.sum(derive=models.{entity}.{attr}, ")
            print(f"         as_sum_of=models.{roleToChildren}.{childAttr},")
            if qualification != None:
                qualification = qualification.replace("!=", "is not")
                qualification = qualification.replace("==", "is")
                qualification = qualification.replace("null", "None")
                print(f"         where=lambda row: {qualification} )")
        elif ruleType == "formula":
            attr = j["attribute"]
            funName =  "fn_" + name.split(".")[0]
            print(f"Rule.formula(derive=models.{entity}.{attr},")
            if ruleJSObj is not None and len(ruleJSObj) > 80:
                print(f"         calling={funName})")
            else:
                ruleJSObj = ruleJSObj.replace("return","lambda row: ")
                print(f"         as_expression={ruleJSObj})")
        elif ruleType == "count":
            attr = j["attribute"]
            roleToChildren = to_camel_case(j["roleToChildren"]).replace("_","")
            qualification = j["qualification"]
            if qualification != None:
                qualification = qualification.replace("!=", "is not")
                qualification = qualification.replace("==", "is")
                qualification = qualification.replace("null", "None")
                print(f"Rule.count(derive=models.{entity}.{attr},")
                print(f"         as_count_of=models.{roleToChildren},")
                print(f"         where=Lambda row: {qualification})")
            else:
                print(f"Rule.count(derive=models.{entity}.{attr},")
                print(f"         as_count_of=models.{roleToChildren})")
        elif ruleType == "validation":
            errorMsg = j["errorMessage"]
            print(f"Rule.constraint(validate=models.{entity},")
            print(f"         calling={funName},")
            print(f"         error_msg=\"{errorMsg}\")")
        elif ruleType == "event":
            print(f"Rule.row_event(on_class=models.{entity},")
            print(f"         calling={funName})")
        elif ruleType == "commitEvent":
            print(f"Rule.commit_row_event(on_class=models.{entity},")
            print(f"         calling={funName}")
        elif ruleType == "parentCopy":
            attr = j["attribute"]
            roleToParent = to_camel_case(j["roleToParent"]).replace("_","")
            parentAttr = j["parentAttribute"]
            print(f"Rule.copy(derive=models.{entity}.{attr},")
            print(f"         from_parent=models.{roleToParent}.{parentAttr})")
        else: 
            print(f"#Rule.{ruleType}(...TODO...)")
            
        print("")
