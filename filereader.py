import os
import json
from pathlib import Path

myProject = "UCF"
reposLocation = "/Users/tylerband/CALiveAPICreator.repository/teamspaces/default/apis"
#basepathUCF = '/Users/tylerband/CALiveAPICreator.repository/teamspaces/default/apis/UCF'
#basepath = '/Users/tylerband/CALiveAPICreator.repository/teamspaces/default/apis/demo'
basepath = f"{reposLocation}/{myProject}"
basepathUCF = f"{reposLocation}/UCF"

def to_camel_case(text):
    s = text.replace("-", " ").replace("_", " ")
    s = s.split()
    if len(text) == 0:
        return text
    r = s[0]+ ''.join(i.capitalize() for i in s[1:])
    return r[:1].capitalize() + r[1:]

def listDir(path):
    if path in [".DS_Store"]:
        return
    for entry in os.listdir(path):
        if os.path.isdir(os.path.join(path, entry)):
            print(f"DIR: {entry}")
            if entry not in [".DS_Store"]:
                for d in os.listdir(os.path.join(path, entry)):
                    if d not in [".DS_Store"]:
                        listFiles(os.path.join(path, entry)+"/"+d)

def listFiles(path):
    if path in [".DS_Store"]:
        return
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.name in [".DS_Store","apiversions.json"]:
                continue
            if entry.is_file():
                if entry.name.endswith(".json"):
                    print(f"     JSON: {entry.name}") 
                if entry.name.endswith(".js"):
                    print(f"     JS: {entry.name}")
                if entry.name.endswith(".sql"):
                    print(f"     SQL: {entry.name}") 
                '''
                else:
                    if entry.name in [".DS_Store"]:
                        continue
                    if entry.is_dir:
                        listDir(os.path.join(path, entry.name)) 
                '''
def dataSource(path):
    #print("=========================")
    #print("        SQL Tables ")
    #print("=========================")
    with os.scandir(path) as entries:
        for f in entries:
            if f in [ "ReadMe.md", ".DS_Store"]:
                continue
            #print ('|', len(path)*'---', f)
            fname = os.path.join(path,f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    db = j["databaseType"]
                    url = j["url"]
                    uname = j["username"]
                    schema = j ["schema"]
                    print("------------------------------------------------------------")
                    print(f"Database: {db} ")
                    print(f"  URL:{url} ")
                    print(f"  User: {uname} Schema: {schema}")
                    ti = j["tableIncludes"]
                    te = j["tableExcludes"]
                    if ti != None:
                        print(f"  TableIncludes: {ti}")
                    if te != None:
                        print(f"  TableExcludes: {te}")
                    print("------------------------------------------------------------")
                    #["metaHolder"] was prior to 5.4
                    for t in j["schemaCache"]["tables"]:
                        print()
                        print("create table " + t["name"] +" (")
                        sep = ""
                        for c in t["columns"]:
                            name = c["name"]
                            autoIncr = ""
                            if "isAutoIncrement" in c:
                                autoIncr = 'AUTO_INCREMENT' if c["isAutoIncrement"] == True else ''
                            baseType = c["attrTypeName"]
                                    #l = c["len"]
                            nullable = '' # 'not null' if c["nullable"] == False else ''
                            print(f"   {sep}{name} {baseType} {nullable} {autoIncr}")
                            sep = ","
                        print(")")
                        for k in t["keys"]:
                            c = k["columns"]
                            cols = f"{c}"
                            cols = cols.replace("[","")
                            cols = cols.replace("]","")
                            print("")
                            print(f"# PRIMARY KEY({cols})")
                            print("")
                            #["metaHolder"] was prior to 5.4
                    for fk in j["schemaCache"]["foreignKeys"]:
                        name = fk["name"]
                        parent = fk["parent"]["name"]   
                        child = fk["child"]["name"]
                        parentCol = fk["columns"][0]["parent"]
                        childCol = fk["columns"][0]["child"]
                        print("")
                        print(f"  ALTER TABLE ADD CONSTRAINT fk_{name} FOREIGN KEY {child}({childCol}) REFERENCES {parent}({parentCol})")
                        print("")

def resourceType(j):
    print(j)      
    
def securityRoles(thisPath):    
    path = f"{thisPath}/roles"
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split('/')
        for f in files:
            if f in [ "ReadMe.md", ".DS_Store"]:
                continue
            fname = os.path.join(dirpath,f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    name = j["name"]
                    tablePerm = j["defaultTablePermission"]
                    print(f"Role: {name} TablePermission: {tablePerm}")
                    
    path = f"{thisPath}/users"
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split('/')
        for f in files:
            if f in [ "ReadMe.md", ".DS_Store"]:
                continue
            
            fname = os.path.join(dirpath,f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    name = j["name"]
                    roles = j["roles"]
                    print(f"User: {name} Roles: {roles}")
                    

def printCols(jsonObj):
    entity = ""
    if jsonObj["resourceType"] == "TableBased":
        entity = jsonObj["entity"]
    attrs = ""
    join = ""
    filter = ""
    if "filter" in jsonObj:
        f =jsonObj["filter"]
        if f != None:
            filter = f"Filter: ({f})"
    if "join" in jsonObj:
        join = jsonObj["join"]
        join = join.replace("\\","", 10)
        join = f"Join: ({join})"
    if "attributes" in jsonObj:
        attributes = jsonObj["attributes"]
        sep = ""
        for a in attributes:
            attrs += sep + a["attribute"]
            sep = ","
        attrs = f"Attrs: ({attrs})"
    return  f"{entity} {join} {attrs}) {filter}"
      
def linkObjects(resList):  # sourcery skip: avoid-builtin-shadow
    resources = []
    # build root list first
    for r in resList:
        dp = r.parentName.split("/")
        #dir = dp[len(dp) - 1]
        isRoot = dp[len(dp) - 2] == "v1"  
        if isRoot:
            resources.append(r)
        
    return resources
                                
def resources(resPath):
   
    print("=========================")
    print("       RESOURCES ")
    print("=========================")
    resources = []
    parentPath = ""
    thisPath =  resPath + "/v1"
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split('/')
        dirName = path[len(path)-1]
        print ('|', len(path)*'---', 'D', dirName)
        for f in files:
            if f in [ "ReadMe.md", ".DS_Store"]:
                continue
            fname = os.path.join(dirpath,f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    data = myfile.read()
                    jsonObj = json.loads(data)
                    print ('|', len(path)*'---', 'F', f, "Entity:", printCols(jsonObj))
                    r = ResourceObj(dirpath, jsonObj, None)
                    # either add or link here
                    fn = jsonObj["name"].split(".")[0] + ".sql"
                    r.jsSQL = findInFiles(dirpath, files , fn)
                    r.jsObj = findInFiles(dirpath, files, "get_event.js")
                    resources.append(r)
                    parentRes = findParent(resources, dirpath, parentPath)
                    if parentRes != None:
                        parentRes.childObj.append(r)
            else:
                print ('|', len(path)*'---', 'F', f)
        parentPath = dirpath
                        
    return linkObjects(resources)
            
def printDir(resPath):
    resources = []
    thisPath =  resPath
    rootLen = len(thisPath.split("/")) + 1
    lastParent = ""
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split('/')
        parent = path[len(path)- 1]
        for f in files:
            if f in [ "ReadMe.md", ".DS_Store","apiversions.json"]:
                continue
            print ('|', len(path)*'---', "F", f)
            fname = os.path.join(dirpath,f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    
                                
    return resources

def relationships(relFile):
    print("=========================")
    print("    RELATIONSHIPS ")
    print("=========================")
    with open(relFile) as myfile:
        d = myfile.read()
        js = json.loads(d)
        for rel in js:
            parent = rel["parentEntity"]
            child = rel["childEntity"]
            roleToParent = rel["roleToParent"]
            roleToChild = rel["roleToChild"]
            parentColumns = rel["parentColumns"][0]
            childColumns = rel["childColumns"][0]
            #primaryjoin
            print(f"{roleToParent} = relationship('{parent}, remote_side=[{childColumns}] ,cascade_backrefs=True, backref='{child}')")
            print(f"{roleToChild} = relationship('{child}, remote_side=[{parentColumns}] ,cascade_backrefs=True, backref='{parent}')")
    
def ruleTypes(ro):
    j = ro.jsonObj
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
    
    # Define a function to use in the rule 
    if ro.jsObj != None:
        funName =  f"fn_{name}"
        print(f"def {funName}(row: models.{entity}, old_row: models.{entity}, logic_row: LogicRow):")
        print("     " + fixup(ro.jsObj))
    
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
        if qualification != None:
            print(f"Rule.sum(derive=models.{entity}.{attr}, as_sum_of=models.{roleToChildren}.{childAttr}, where=lamda row: {qualification} )")
        else:
            print(f"Rule.sum(derive=models.{entity}.{attr}, as_sum_of=models.{roleToChildren}.{childAttr})")
    elif ruleType == "formula":
        attr = j["attribute"]
        funName =  "fn_" + name.split(".")[0]
        print(f"Rule.formula(derive=models.{entity}.{attr}, calling={funName})")
    elif ruleType == "count":
        attr = j["attribute"]
        roleToChildren = to_camel_case(j["roleToChildren"]).replace("_","")
        qualification = j["qualification"]
        if qualification != None:
            print(f"Rule.count(derive=models.{entity}.{attr} ,as_count_of=models.{roleToChildren} , where=lamda row: {qualification} )")
        else:
            print(f"Rule.count(derive=models.{entity}.{attr} ,as_count_of=models.{roleToChildren} )")
    elif ruleType == "validation":
        errorMsg = j["errorMessage"]
        print(f"Rule.constraint(validate=models.{entity}, calling={funName}, error_msg=\"{errorMsg}\")")
    elif ruleType == "event":
        appliesTo = j["appliesTo"]
        print(f"#appliesTo: {appliesTo} ")
        print(f"Rule.row_event(lambda row: {name}, calling:{funName})")
    elif ruleType == "commitEvent":
        appliesTo = j["appliesTo"]
        print(f"Rule.commit_row_event(lambda row: {name}, appliesTo: {appliesTo} calling:{funName}")
    elif ruleType == "parentCopy":
        attr = j["attribute"]
        roleToParent = to_camel_case(j["roleToParent"]).replace("_","")
        parentAttr = j["parentAttribute"]
        print(f"Rule.copy(derive=models.{entity}.{attr}, from_parent=models.{roleToParent}.{parentAttr})")
    else: 
        print(f"#Rule.{ruleType}(...TODO...)")
        
    print("")

'''
Convert JavaScript LAC to ALS Python
'''
def fixup(str):
    newStr =  str.replace("oldRow","old_row",20)
    newStr = newStr.replace("logicContext","logic_row",20)
    newStr = newStr.replace("log.","logic_row.log.",20)
    newStr = newStr.replace("var","",20)
    newStr = newStr.replace("//","#",200)
    newStr = newStr.replace("createPersistentBean","logic_row.new_logic_row")
    newStr = newStr.replace(";","",200)
    newStr = newStr.replace("?"," if ",400)
    newStr = newStr.replace(":"," else ",400)
    newStr = newStr.replace("} else {","else:", 100)
    newStr = newStr.replace("}else {","else:", 100)
    newStr = newStr.replace(") {","):",40)
    newStr = newStr.replace("){","):",40)
    newStr = newStr.replace("function ","def ",40)
    newStr = newStr.replace("} else if","elif ")
    newStr = newStr.replace("}else if","elif ",20)
    newStr = newStr.replace("||","|",20)
    newStr = newStr.replace("&&","&",20)
    newStr = newStr.replace("}else{","else:", 20)
    newStr = newStr.replace("null","None",40)
    newStr = newStr.replace("===","==",40)
    newStr = newStr.replace("}","",40)
    newStr = newStr.replace("else  if ","elif", 20)
    newStr = newStr.replace("true","True", 30)
    newStr = newStr.replace("false","False", 30)
    newStr = newStr.replace("if (","if ", 30)
    newStr = newStr.replace("if(","if ",30)
    newStr = newStr.replace("):",":", 30)
    newStr = newStr.replace("logic_row.verb == \"INSERT\"","logic_row.is_inserted() ")
    newStr = newStr.replace("logic_row.verb == \"UPDATE\"","logic_row.is_updated()")
    newStr = newStr.replace("logic_row.verb == \"DELETE\"","logic_row.is_deleted()")
    newStr = newStr.replace("JSON.stringify","jsonify",20)
    newStr = newStr.replace("JSON.parse","json.loads",20)
    newStr = newStr.replace("/*","'''", 20)
    newStr = newStr.replace("*/", "'''",20)
    
    # SysUtility ???
    return newStr.replace("log.debug(","log(",20)

def functionList(thisPath):
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split('/')
        for f in files:
            if f in [ "ReadMe.md", ".DS_Store","prefixes.json","api.json", "apioptions.json"]:
                continue
            fname = os.path.join(dirpath,f)
            if fname.endswith(".js"):
                with open(fname) as myfile:
                    d = myfile.read()
                    #print("'''")
                    funName =  "fn_" + f.split(".")[0]
                    print(f"def {funName}:")
                    print("     " + fixup(d))
    
    
def rules(thisPath):
    #print("=========================")
    #print("        RULES ")
    #print("=========================")
    rules = []
    for dirpath, dirs, files in os.walk(thisPath):
        for f in files:
            if f in [ "ReadMe.md", ".DS_Store","prefixes.json"]:
                continue
            #print ('|', len(path)*'---', f)
            fname = os.path.join(dirpath,f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    #ruleTypes(j)
                    r = RuleObj(j, None)
                    fn = f.split(".")[0] + ".js"
                    ff = findInFiles(dirpath, files, fn)
                    r.jsObj = ff
                    rules.append(r)
    return rules

def entityList(rules):
    entityList = []
    for r in rules:
        entity = r.entity
        if entity not in entityList:
            entityList.append(entity)
    return entityList
    
def findInFiles(dirpath, files, fileName):
    for f in files:
        if f == fileName:
            fname = os.path.join(dirpath,f)
            with open(fname) as myfile:
                return myfile.read()
    return None
    
def findParent(objectList, dirList, parentDir):
    dl = dirList.split("/")
    if dl[len(dl) -2] == "v1":  
        return None #Root
    for l in objectList:
        if l.parentName == parentDir:
                return l
    return None

def findObjInPath(objectList, pathName, name):
    pn = pathName.replace(basepath+"/v1/","")
    nm = name.split(".")[0]
    for l in objectList:
        if l.parentName == pn:
            if l.name == nm:
                return l
    return None
        
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
        

def printChild(self):
    if self.childObj != None:
            print (f"     Name: {self.parentName} Entity: {self.entity} ChildName: {self.childObj.name} ChildPath: {self.childObj.parentName}")
            
            
class ResourceObj:
    def __init__(self, dirpath, jsonObj, jsObj):
        name = jsonObj["name"]
        self.parentName = dirpath
        self.name = name
        entity = to_camel_case(name)
        if "entity" in jsonObj:
            entity = to_camel_case(jsonObj["entity"])
        self.entity = entity
        self.ResourceType = jsonObj["resourceType"]
        self.jsonObj = jsonObj  
        self.jsObj = jsObj
        self.sqlObj = None
        self.childObj = []
        
    def addChildObj(co):
        self.childObj.append(co)
    
    def __str__(self):
        # switch statement for each Resource
        if self.childObj == []:
            return f"Name: {self.name} Entity: {self.entity} ResourceType: {self.ResourceType}"
        else:
            return f"Name: {self.name} Entity: {self.entity}  ResourceType: {self.ResourceType} ChildName: {self.childObj[0].name}" # {print(childObj[0]) for i in childObj: print(childObj[i])}
            
     
'''
interested details in rules, functions, resources
'''
def listExpanded(path):
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split('/')
        if os.path.basename(dirpath) in [ "filters", "request_events", "sorts" "timers","request_events"]:
            continue
        
        if os.path.basename(dirpath) == "rules":
            rules = rules(dirpath)
            for r in rules:
                print(f"Entity: {r.entity}, Name: {r.name}, RuleType: {r.ruleType}")
            #break
            continue
        
        if dirpath.endswith("data_sources"):
            dataSource(files)
            continue
        if os.path.basename(dirpath) == "resources":
            resList = resources(dirpath)
            print(len(resList))
            for r in resList:
                print(r)   
                printChild(r) 
            #break
            continue
        if os.path.basename(dirpath) == "security":
            securityRoles(dirpath)
            continue

        print ('|', (len(path))*'---', '[',os.path.basename(dirpath),']')
        for f in files:
            if f in ["apioptions.json", "ReadMe.md", ".DS_Store", "authtokens","filters", "request_events", "sorts", "timers","request_events"]:
                continue
            print ('|', len(path)*'---', f)
            fname = os.path.join(dirpath,f)
            if f == "relationships.json":
                relationships(fname)
                continue
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    print(d)
            if fname.endswith(".js"):
                with open(fname) as myfile:
                    d = myfile.read()
                    print(fixup(d))
            if fname.endswith(".sql"):
                with open(fname) as myfile:
                    d = myfile.read()
                    print(d)
                    
def printChildren(child, i):
    if len(child.childObj) > 0:
        for c in child.childObj:
            print((i)*'  ', c)
            printChildren(c, i+1)
def printResource(resList):
      for r in resList:
       
        name = r.name.lower()
        entity = r.entity
        print("'''")
        print(r)
        print(f"     @app.route('/{name}')")
        print(f"     def {name}:')")
        print("           db = safrs.DB")
        print(f"           {name}_id = request.args.get('Id')")
        print("           session = db.session")
        print(f"           {name} = session.query(models.{entity}).filter(models.{entity}.Id == {name}_id).one()")
        print(f"           result_std_dict = util.row_to_dict({name}, replace_attribute_tag='data', remove_links_relationships=True")
        print("           return result_std_dict")
        
        printChildren(r, 0)
        print("'''")
        print("")

def listDirs(path):
    for entry in os.listdir(path):
        #for dirpath, dirs, files in os.walk(basepath):
        if entry in ["api.json", "topics", "sorts","issues.json", "apioptions.json","filters", "timers", "exportoptions.json", ".DS_Store"]:
            continue
        filePath = f"{path}/{entry}"
        print("")
        print("=========================")
        print(f"       {entry} ")
        print("=========================")
        
        if entry == "rules":
            rulesList = rules(filePath)
            entities = entityList(rulesList)
            #Table of Contents
            for entity in entities:
                e = to_camel_case(entity)
                print(f"# ENTITY: {e}")
                print("")
                for r in rulesList:
                    if r.entity == entity:
                        ruleTypes(r)
            break;
        
        if entry == "resources":
            resList = resources(f"{path}/{entry}")
            printResource(resList)
            continue
        
        if entry == "data_sources":
            dataSource(filePath)
            continue
        
        if entry == "functions":
            functionList(filePath)
            continue
        
        if entry == "lbiraries":
            functionList(filePath)
            continue
        
        if entry == "request_events":
            functionList(filePath)
            continue
        
        if entry == "relationships.json":
            relationships(f"{path}/relationships.json")
            continue
        
        if entry == "security":
            securityRoles(filePath)
            continue
            
        printDir(f"{basepath}/{entry}")
        
listDirs(basepath)
#listExpanded(basepath)