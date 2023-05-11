import os
import json
import sys
from pathlib import Path
from rule import RuleObj
from resourceobj import ResourceObj
from util import to_camel_case, fixup

def setVersion(path: Path):
    global version
    version = next(
        (
            "5.4"
            for dirpath, dirs, files in os.walk(path)
            if os.path.basename(dirpath) == "pipeline_events"
        ),
        "5.x",
    )

def listDir(path: Path):
    if path in [".DS_Store"]:
        return
    for entry in os.listdir(path):
        if os.path.isdir(os.path.join(path, entry)):
            print(f"DIR: {entry}")
            if entry not in [".DS_Store"]:
                for d in os.listdir(os.path.join(path, entry)):
                    if d not in [".DS_Store"]:
                        listFiles(f"{os.path.join(path, entry)}/{d}")

def listFiles(path: Path):
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
def dataSource(path: Path):
    #print("=========================")
    #print("        SQL Tables ")
    #print("=========================")
    tableList = []
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
                    tables = j["schemaCache"]["tables"] if version == "5.4"  else j["schemaCache"]["metaHolder"]["tables"]
                    for t in tables:
                        print("")
                        name = t["name"] if version == "5.4" else t["entity"]
                        tableList.append(name)
                        print(f"create table {schema}.{name} (")
                        sep = ""
                        for c in t["columns"]:
                            name = c["name"]
                            autoIncr = ""
                            if "isAutoIncrement" in c:
                                autoIncr = 'AUTO_INCREMENT' if c["isAutoIncrement"] == True else ''
                            baseType = c["attrTypeName"] if version == "5.4" else c["baseTypeName"]
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
                    if version == "5.4":
                        fkeys = j["schemaCache"]["foreignKeys"]
                    else:
                        fkeys = j["schemaCache"]["metaHolder"]["foreignKeys"]
                    for fk in fkeys:
                        if version == "5.4":
                            name = fk["name"]
                        else:
                            name = fk["entity"]
                        if version == "5.4":
                            parent = fk["parent"]["name"]   
                        else:
                            parent = fk["parent"]["object"]  
                        if version == "5.4":
                            child = fk["child"]["name"]
                        else:
                            child = fk["child"]["object"]
                        parentCol = fk["columns"][0]["parent"]
                        childCol = fk["columns"][0]["child"]
                        print("")
                        print(f"  ALTER TABLE ADD CONSTRAINT fk_{name} FOREIGN KEY {child}({childCol}) REFERENCES {parent}({parentCol})")
                        print("")
        # print curl test for root table API endpoints
        for tbl in tableList:
            print(f"ECHO calling endpoint: {tbl}")
            print(f"curl -X 'GET' \"http://localhost:5656/{tbl}\"")
            print("")

def resourceType(resource: object):
    print(resource)      
    
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
                    

def printCols(jsonObj: object):
    entity = "" if jsonObj["resourceType"] != "TableBased" else jsonObj["entity"]
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

def linkObjects(resList: object): 
    resources = []
    # build root list first
    for r in resList:
        dp = r.parentName.split("/")
        #dir = dp[len(dp) - 1]
        isRoot = dp[len(dp) - 2] == "v1"  
        if isRoot:
            resources.append(r)
        
    return resources
                                
def resources(resPath: str):
    #print("=========================")
    #print("       RESOURCES ")
    #print("=========================")
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
                    if "isActive" in jsonObj:
                        if jsonObj["isActive"] == False:
                            continue
                    print ('|', len(path)*'---', 'F', f, "Entity:", printCols(jsonObj))
                    resObj = ResourceObj(dirpath, jsonObj, None)
                    # either add or link here
                    fn = jsonObj["name"].split(".")[0] + ".sql"
                    resObj.jsSQL = findInFiles(dirpath, files , fn)
                    resObj.getJSObj = findInFiles(dirpath, files, "get_event.js")
                    fn = jsonObj["name"].split(".")[0] + ".js"
                    resObj.jsObj = findInFiles(dirpath, files, fn)
                    resources.append(resObj)
                    parentRes = findParent(resources, dirpath, parentPath)
                    if parentRes != None:
                        parentRes.childObj.append(resObj)
            else:
                print ('|', len(path)*'---', 'F', f)
        parentPath = dirpath
                        
    return linkObjects(resources)
            
def printDir(resPath: Path):
    """_summary_

    Args:
        resPath (Path): _description_

    Returns:
        _type_: _description_
    """
    thisPath =  resPath
    rootLen = len(thisPath.split("/")) + 1
    lastParent = ""
    resources = []
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

def relationships(relFile: str):
    #print("=========================")
    #print("    RELATIONSHIPS ")
    #print("=========================")
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

def functionList(thisPath: str):
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
                    print(f"     {fixup(d)}")
    
    
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
                    data = myfile.read()
                    jsonData = json.loads(data)
                    rule = RuleObj(jsonData, None)
                    fn = f.split(".")[0] + ".js"
                    javaScriptFile = findInFiles(dirpath, files, fn)
                    rule.jsObj = javaScriptFile
                    rules.append(rule)
    return rules

def entityList(rules: object):
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
    return next((l for l in objectList if l.parentName == parentDir), None)

def findObjInPath(objectList, pathName, name):
    pn = pathName.replace(f"{basepath}/v1/", "")
    nm = name.split(".")[0]
    return next(
        (l for l in objectList if l.parentName == pn and l.name == nm), None
    )
        

def printChild(self):
    if self.childObj != None:
            print (f"     Name: {self.parentName} Entity: {self.entity} ChildName: {self.childObj.name} ChildPath: {self.childObj.parentName}")
            
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
def listExpanded(path: str):
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
                
def printCurlTests(resList):
    print("")
    print("CURL TESTS")
    for r in resList:
        if r.isActive:
            name = r.name.lower()
            entity = r.entity
            print(f"ECHO {name}")
            print(f"curl -X 'GET' \"http://localhost:5656/{name}\"")
            print("")
    
def printResource(resList):
    space = "        "
    for r in resList:
        if r.isActive:
            name = r.name.lower()
            entity = r.entity
            #print(f"#{r} s")
            print(f"    @app.route('/{name}')")
            print(f"    def {name}():")
            print(f'{space}root = Resource.create(models.{entity},"{r.name}")')
            printResAttrs("root", r)
            printGetFunc("root", r)
            printChildren(r,"root", 1)
            print("")
            print(f'{space}key = request.args.get(root.parentKey)')
            print(f'{space}limit = request.args.get("page_limit")')
            print(f'{space}offset = request.args.get("page_offset")')
            print(f'{space}result = Resource.execute(root, key, limit, offset)')
            print('        return jsonify({"success": True, f"{root.name}": result})')
            print("")
            # these are the get_event.js 
    for r in resList:
        if r.isActive:
            printResourceFunctions(r)

def printChildren(resource: object,parent_name: str, i: int):
    space = "        "
    for child in resource.childObj:
        cname = child.name
        childName = f"{cname}_{i}"
        print("")
        print(f'{space}{childName} = Resource(models.{child.entity},"{cname}")')
        printResAttrs(childName, child)
        attrName = findAttrName(child)
        if attrName is not None:
            joinType = "join" if child.jsonObj["isCollection"] is True  else "joinParent"
            if joinType == "joinParent":
                isCombined = "True" if child.jsonObj["isCombined"] is True  else "False"
                print(f'{space}Resource.{joinType}({parent_name}, {childName}, models.{resource.entity}.{attrName[1]}, {isCombined})')
            else:
                print(f'{space}Resource.{joinType}({parent_name}, {childName}, models.{child.entity}.{attrName[0]})')
        printGetFunc(childName, child)
       
        printChildren(child, childName, i + 1)
       
            
def  printResAttrs(name: str, resource: object):
    if resource.jsonObj is None:
        return
    if "attributes" in resource.jsonObj:
        for attr in resource.jsonObj["attributes"]:
            space = "        "
            if version == "5.4":
                attrName = attr["attribute"]
            else:
                attrName = attr["alias"]
                
            print(f'{space}Resource.alias({name},models.{resource.entity}.{attrName}, \"{attrName}\")')

def printGetFunc(name: str, res: object):
    if res.getJSObj is not None:
        space = "        "
        fn = f"fn_{res.entity}_event"
        print(f"{space}Resource.calling({name}, {fn})")
        
def printResourceFunctions(resource: object):
    name = resource.name.lower()
    entity = resource.entity
    if resource.getJSObj is not None:
        space = "          "
        print(f"{space}def fn_{entity}_event(row: any):")
        print(f"{space}{space}pass")
        print("'''")
        print(f"{space}" + fixup(resource.getJSObj))
        print("'''")
    if resource.childObj is not None:
        for child in resource.childObj:
            printResourceFunctions(child)
            
def findAttrName(resourceObj: object):
    if resourceObj.ResourceType == "TableBased":
       join = resourceObj.jsonObj["join"]
       if join is not None:
            ret = []
            join = join.replace("\"","",10)
            join = join.replace("[","")
            join = join.replace("]","")
            join = join.replace(" ","",4)
            for j in join.split("="):
                ret.append(j)
            return ret
 

def listDirs(path: Path, section: str = "all"):

    setVersion(path)
    print(version)
    for entry in os.listdir(path):
        #for dirpath, dirs, files in os.walk(basepath):
        if section.lower() != "all" and entry != section:
                continue
       
        filePath = f"{path}/{entry}"
        if entry in ["api.json", "issues.json", "apioptions.json", "exportoptions.json", ".DS_Store"]:
            continue
        print("")
        print("=========================")
        print(f"       {entry.upper()} ")
        print("=========================")
        
        if entry == "resources":
            resList = resources(f"{path}/{entry}")
            printResource(resList)
            printCurlTests(resList)
            continue
        
        if entry == "rules":
            rulesList = rules(filePath)
            entities = entityList(rulesList)
            #Table of Contents
            for entity in entities:
                entityName = to_camel_case(entity)
                print(f"# ENTITY: {entityName}")
                print("")
                for rule in rulesList:
                    if rule.entity == entity:
                        RuleObj.ruleTypes(rule)
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
        
"""
    projectName = demo
    reposLocation = f"{reposLocation}/{projectName}"
 = ~/CALiveAPICreator.repository
"""        
apiroot = "teamspaces/default/apis"
projectName = "demo"
reposLocation = "/Users/tylerband/CALiveAPICreator.repository"
basepath = f"{reposLocation}/{apiroot}/{projectName}"
version = "5.4"
command = "not set"
sections = "rules"

if __name__ == '__main__':
    commands = sys.argv
    if len(sys.argv) < 3:
        print('\nCommand Line Arguments: python3 reposreader.py apiProjectName LACReposLocation [section=all| rule| resources| etc...]')
    
    else:
        if len(sys.argv) == 3:
            projectName = sys.argv[1]
            reposLocation = sys.argv[2]
        if len(sys.argv) == 4:
            sections = sys.argv[3]
        print(sys.argv)   
        basepath = f"{reposLocation}/{apiroot}/{projectName}"
    
    listDirs(basepath, sections)