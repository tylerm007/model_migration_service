# filereader.py
# Copyright (C) 2005-2021 the Archimedes authors and contributors
# <see AUTHORS file>
#
# This module is part of Archimedes and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
"""
This is a utility to read the CA Live API Creator file based repository and print a report that can be used to help migrate 
to API Logic Server (a Python API open-source tool) https://apilogicserver.github.io/Docs/
"""
import os
import json
import sys
import argparse
from pathlib import Path
from rule import RuleObj
from resourceobj import ResourceObj
from util import to_camel_case, fixup

global version
global tableAlias

def main(calling_args=None):
    if calling_args:
        args = calling_args
    else:
        parser = argparse.ArgumentParser(description="Generate a report of an existing CA Live API Creator Repository ")
        parser.add_argument("--repos", help="Full path to /User/guest/caliveapicreator.repository", type=str)
        parser.add_argument("--project", help="The name of the LAC project (teamspace/api) default: demo", default="demo", type=str)
        parser.add_argument("--section", help="The api directory name to process [rules, resources, functions, etc.] default: all", default="all",type=str)
        parser.add_argument("--version", action="store_true", help="print the version number and exit")
      
        args = parser.parse_args()
        
        if args.version:
            version = "1.0" # TODO
            print(version)
            return
        if not args.repos:
            print('Please supply a --repos location\n', file=sys.stderr)
            parser.print_help()
            return
        
        projectName = args.project or "demo"
        reposLocation = args.repos
        sections = args.section or "all"
       
        basepath = f"{reposLocation}/{apiroot}/{projectName}"
    try:
        readTableAlias()
        listDirs(basepath, sections)
    except Exception as ex:
        print(f"Error running  {ex}")

def readTableAlias():
    """
    Read a list of generated tables from ALS to use in the translation
    TableName = AliasName
    """
    tableAlias = []
    
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
            if entry.name in [".DS_Store", "apiversions.json"]:
                continue
            if entry.is_file():
                if entry.name.endswith(".json"):
                    print(f"     JSON: {entry.name}")
                if entry.name.endswith(".js"):
                    print(f"     JS: {entry.name}")
                if entry.name.endswith(".sql"):
                    print(f"     SQL: {entry.name}")
                """
                else:
                    if entry.name in [".DS_Store"]:
                        continue
                    if entry.is_dir:
                        listDir(os.path.join(path, entry.name)) 
                """


def dataSource(path: Path):
    print("# This is informational only of the database schema, tables, columns")
    # print("=========================")
    # print("        SQL Tables ")
    # print("=========================")
    tableList = []
    with os.scandir(path) as entries:
        for f in entries:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue
            # print ('|', len(path)*'---', f)
            fname = os.path.join(path, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    db = j["databaseType"]
                    url = j["url"]
                    uname = j["username"]
                    schema = j["schema"]
                    print(
                        "------------------------------------------------------------"
                    )
                    print(f"Database: {db} ")
                    print(f"  URL:{url} ")
                    print(f"  User: {uname} Schema: {schema}")
                    ti = j["tableIncludes"]
                    te = j["tableExcludes"]
                    if ti != None:
                        print(f"  TableIncludes: {ti}")
                    if te != None:
                        print(f"  TableExcludes: {te}")
                    print(
                        "------------------------------------------------------------"
                    )
                    # ["metaHolder"] was prior to 5.4
                    tables = (
                        j["schemaCache"]["tables"]
                        if version == "5.4"
                        else j["schemaCache"]["metaHolder"]["tables"]
                    )
                    for t in tables:
                        print(" ")
                        name = t["name"] if version == "5.4" else t["entity"]
                        tableList.append(name)
                        print(f"create table {schema}.{name} (")
                        sep = ""
                        for c in t["columns"]:
                            name = c["name"]
                            autoIncr = ""
                            if "isAutoIncrement" in c:
                                autoIncr = (
                                    "AUTO_INCREMENT"
                                    if c["isAutoIncrement"] == True
                                    else ""
                                )
                            baseType = (
                                c["attrTypeName"]
                                if version == "5.4"
                                else c["baseTypeName"]
                            )
                            # l = c["len"]
                            nullable = (
                                ""  # 'not null' if c["nullable"] == False else ''
                            )
                            print(f"   {sep}{name} {baseType} {nullable} {autoIncr}")
                            sep = ","
                        print(")")
                        for k in t["keys"]:
                            c = k["columns"]
                            cols = f"{c}"
                            cols = cols.replace("[", "")
                            cols = cols.replace("]", "")
                            print("")
                            print(f"# PRIMARY KEY({cols})")
                            print("")
                            # ["metaHolder"] was prior to 5.4
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
                        print(
                            f"  ALTER TABLE ADD CONSTRAINT fk_{name} FOREIGN KEY {child}({childCol}) REFERENCES {parent}({parentCol})"
                        )
                        print("")
        print("=============================================================================================")
        print("    CURL tests for each table endpoint ?page[limit]=10&page[offset]=00&filter[key]=value")
        print("=============================================================================================")
        for tbl in tableList:
            name = singular(tbl)
            print(f"ECHO calling endpoint: {name}?page[limit]=1")
            print(f"curl \"http://localhost:5656/api/{name}?page%5Blimit%5D=1\" \\")
            print("         -H 'accept: application/vnd.api+json' \\")
            print("         -H 'Content-Type: application/json' ")
            print("")
            print("")

def singular(name: str) -> str:
    #return name[:-1] if name.endswith("s") else name  # singular names only
    return name


def resourceType(resource: object):
    print(resource)


def securityRoles(thisPath):
    path = f"{thisPath}/roles"
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split("/")
        for f in files:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    name = j["name"]
                    tablePerm = j["defaultTablePermission"]
                    print(f"Role: {name} TablePermission: {tablePerm}")

    path = f"{thisPath}/users"
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split("/")
        for f in files:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue

            fname = os.path.join(dirpath, f)
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
        f = jsonObj["filter"]
        if f != None:
            filter = f"Filter: ({f})"
    if "join" in jsonObj:
        join = jsonObj["join"]
        join = join.replace("\\", "", 10)
        join = f"Join: ({join})"
    if "attributes" in jsonObj:
        attributes = jsonObj["attributes"]
        sep = ""
        for a in attributes:
            attrs += sep + a["attribute"]
            sep = ","
        attrs = f"Attrs: ({attrs})"
    return f"{entity} {join} {attrs}) {filter}"


def linkObjects(resList: object):
    resources = []
    # build root list first
    for r in resList:
        dp = r.parentName.split("/")
        # dir = dp[len(dp) - 1]
        isRoot = dp[len(dp) - 2] == "v1"
        if isRoot:
            resources.append(r)

    return resources


def resources(resPath: str):
    # print("=========================")
    # print("       RESOURCES ")
    # print("=========================")
    resources = []
    parentPath = ""
    thisPath = f"{resPath}{os.sep}v1"
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split(f"{os.sep}")
        dirName = path[len(path) - 1]
        print("|", len(path) * "--", "D", dirName)
        for f in files:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    data = myfile.read()
                    jsonObj = json.loads(data)
                    if "isActive" in jsonObj:
                        if jsonObj["isActive"] == False:
                            continue
                    print("|", len(path) * "---", "F", f, "Entity:", printCols(jsonObj))
                    resObj = ResourceObj(dirpath, jsonObj)
                    # either add or link here
                    fn = jsonObj["name"].split(".")[0] + ".sql"
                    resObj.jsSQL = findInFiles(dirpath, files, fn)
                    resObj._getJSObj = findInFiles(dirpath, files, "get_event.js")
                    fn = jsonObj["name"].split(".")[0] + ".js"
                    resObj._jsObj = findInFiles(dirpath, files, fn)
                    resources.append(resObj)
                    parentRes = findParent(resources, dirpath, parentPath)
                    if parentRes != None:
                        parentRes.childObj.append(resObj)
            else:
                print("|", len(path) * "---", "F", f)
        parentPath = dirpath

    return linkObjects(resources)


def printDir(resPath: Path):
    """_summary_

    Args:
        resPath (Path): 
    """
    thisPath = resPath
    rootLen = len(thisPath.split(os.sep)) + 1
    lastParent = ""
    resources = []
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split("/")
        parent = path[len(path) - 1]
        for f in files:
            if f in ["ReadMe.md", ".DS_Store", "apiversions.json"]:
                continue
            print("|", len(path) * "---", "F", f)
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)

    return resources


def relationships(relFile: str):
    print("# This is informational only")
    # print("=========================")
    # print("    RELATIONSHIPS ")
    # print("=========================")
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
            # primaryjoin
            print(
                f"{roleToParent} = relationship('{parent}, remote_side=[{childColumns}] ,cascade_backrefs=True, backref='{child}')"
            )
            print(
                f"{roleToChild} = relationship('{child}, remote_side=[{parentColumns}] ,cascade_backrefs=True, backref='{parent}')"
            )


def functionList(thisPath: str):
    """
    LAC has many different JavaScript functions, libraries, pipelines (aka request_response)
    Many of these cannot be converted directly since they may use utilities or functions
    not available (e.g. SysUtility) or expect state information (logic_row) 
    Recommendation: refactor the JS to match the desired result in ALS
    Args:
        thisPath (str): 
    """
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split(os.sep)
        for f in files:
            if f in [
                "ReadMe.md",
                ".DS_Store",
                "prefixes.json",
                "api.json",
                "apioptions.json",
            ]:
                continue
            fname = os.path.join(dirpath, f)
            if fname.endswith(".js"):
                with open(fname) as myfile:
                    fn = myfile.read()
                    print("")
                    fn = fixup(fn)
                    funName = "fn_" + f.split(".")[0]
                    print(f"def {funName}(row: models.TableName, old_row: models.TableName, logic_row: LogicRow):")
                    #print("     return")
                    print(f"     {fn}")


def rules(thisPath) -> list:
    # print("=========================")
    # print("        RULES ")
    # print("=========================")
    '''
    Collect all of the rules definitions and JS info and stash in a list of RuleObj objects
    The object itself (rule.py) has print functions that do the transforms
    '''
    rules = []
    for dirpath, dirs, files in os.walk(thisPath):
        for f in files:
            if f in ["ReadMe.md", ".DS_Store", "prefixes.json"]:
                continue
            # print ('|', len(path)*'---', f)
            fname = os.path.join(dirpath, f)
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
            fname = os.path.join(dirpath, f)
            with open(fname) as myfile:
                return myfile.read()
    return None


def findParent(objectList, dirList, parentDir):
    dl = dirList.split(os.sep)
    if dl[len(dl) - 2] == "v1":
        return None  # Root
    return next((l for l in objectList if l.parentName == parentDir), None)


def findObjInPath(objectList, pathName, name):
    pn = pathName.replace(f"{basepath}{os.sep}v1{os.sep}", "")
    nm = name.split(".")[0]
    return next((l for l in objectList if l.parentName == pn and l.name == nm), None)

def printChild(self):
    if self.childObj != None:
        print(
            f"     Name: {self.parentName} Entity: {self.entity} ChildName: {self.childObj.name} ChildPath: {self.childObj.parentName}"
        )

    def addChildObj(co):
        self.childObj.append(co)

    def __str__(self):
        # switch statement for each Resource
        if self.childObj == []:
            return f"Name: {self.name} Entity: {self.entity} ResourceType: {self.ResourceType}"
        else:
            return f"Name: {self.name} Entity: {self.entity}  ResourceType: {self.ResourceType} ChildName: {self.childObj[0].name}"  # {print(childObj[0]) for i in childObj: print(childObj[i])}


"""
interested details in rules, functions, resources
"""


def listExpanded(path: str):
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split(os.sep)
        if os.path.basename(dirpath) in [
            "filters",
            "request_events",
            "sorts" "timers",
            "request_events",
        ]:
            continue

        if os.path.basename(dirpath) == "rules":
            rules = rules(dirpath)
            for r in rules:
                print(f"Entity: {r.entity}, Name: {r.name}, RuleType: {r.ruleType}")
            # break
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
            # break
            continue
        if os.path.basename(dirpath) == "security":
            securityRoles(dirpath)
            continue

        print("|", (len(path)) * "---", "[", os.path.basename(dirpath), "]")
        for f in files:
            if f in [
                "apioptions.json",
                "ReadMe.md",
                ".DS_Store",
                "authtokens",
                "filters",
                "request_events",
                "sorts",
                "timers",
                "request_events",
            ]:
                continue
            print("|", len(path) * "---", f)
            fname = os.path.join(dirpath, f)
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


def printCurlTests(resObj: ResourceObj):
    print("")
    print("CURL TESTS")
    if resObj.isActive:
        name = resObj.name.lower()
        entity = resObj.entity
        filter_by = "?page%5Blimit%5D=1" # page[offset]=0&filter[key]=value"
        print(f"ECHO calling Entity {entity} using: {name}{filter_by}")
        print("curl \"http://localhost:5656/{name}{filter_by}\"\\")
        print("         -H 'accept: application/vnd.api+json' \\")
        print("         -H 'Content-Type: application/json'")
        print("")


def listDirs(path: Path, section: str = "all"):
    setVersion(path)
    print(f"LAC Version: {version}")
    for entry in os.listdir(path):
        # for dirpath, dirs, files in os.walk(basepath):
        if section.lower() != "all" and entry != section:
            continue

        filePath = f"{path}{os.sep}{entry}"
        if entry in [
            "api.json",
            "issues.json",
            "apioptions.json",
            "exportoptions.json",
            ".DS_Store",
        ]:
            continue
        print("")
        print("=========================")
        print(f"       {entry.upper()} ")
        print("=========================")

        if entry == "resources":
            resList: ResourceObj = resources(f"{path}{os.sep}{entry}")
            print("#Copy this section to ALS api/customize_api.py")
            for resObj in resList:
                resObj.PrintResource(version)
            for resObj in resList:
                resObj.PrintResourceFunctions(resObj._name, version)
            print("===============================================")
            print("    CURL tests for each UserResource endpoint")
            print("================================================")
            for resObj in resList:
                printCurlTests(resObj)
            
            print("#FreeSQL TODO section to ALS api/customize_api.py")
            for resObj in resList:
                resObj.printFreeSQL()
            continue

        if entry == "rules":
            rulesList = rules(filePath)
            entities = entityList(rulesList)
            # Table of Contents
            print("#Copy this section to ALS logic/declare_logic.py")
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

        if entry in ["request_events" ,"pipelines", "libraries", "functions"]:
            print(f"#These are JavaScript {entry} can be called by rules and resources")
            functionList(filePath)
            continue

        if entry == "relationships.json":
            relationships(f"{path}{os.sep}relationships.json")
            continue

        if entry == "security":
            securityRoles(filePath)
            continue

        printDir(f"{basepath}{os.sep}{entry}")


"""
    projectName = demo
    reposLocation = f"{reposLocation}/{projectName}"
 = ~/CALiveAPICreator.repository
"""
apiroot = "teamspaces/default/apis"
projectName = "b2bderbynw"
reposLocation = "/Users/tylerband/CALiveAPICreator.repository"
basepath = f"{reposLocation}/{apiroot}/{projectName}"
version = "5.4"
command = "not set"
section = "all" # all is default or resources, rules, etc.s

if __name__ == "__main__":
    main()
#lse:  
#    local testing and debugging
#    listDirs(basepath, section)