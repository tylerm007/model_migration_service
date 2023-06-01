from util import to_camel_case, fixup, fixupSQL
import json
"""
Resources defined in LAC - TableBased only (SQL and JS)

Raises:
    ValueError: JSON Object (from file system)
    
Returns:
    _type_: RuleObj
"""
class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class JoinObj:
    # parent object, child object, and join operator from Resource join attribute
    def __init__ (
        self,
        parent: str,
        child: str,
        op: str = None,
    ):
        self.parent = parent
        self.child = child
        self.op = op
    
    def __str__(self):
        print(f"parent {self.parent} op {self.op} = child [{self.child}]")
    
class ResourceObj:
    def __init__(
        self,
        parentName: str,
        parentDir: str,
        jsonObj: dict,
        jsObj: str = None,
        sqlObj: str = None,
        getJsObj: str = None,
        childObj: list[object] = None,
    ):
        if not jsonObj:
            raise ValueError("JSON Object [dict] is required for ResourceObj")
        self.jsonObj = jsonObj
        self.parentName = parentName
        self.parentDir = parentDir
        self._name = jsonObj["name"]
        entity = to_camel_case(self._name)
        if "entity" in jsonObj:
            entity = to_camel_case(jsonObj["entity"])
        self.entity = entity
        self.ResourceType = jsonObj["resourceType"]
        self._jsObj = None if jsObj is None else jsObj
        self._getJSObj = None if getJsObj is None else getJsObj
        self.sqlObj = None if sqlObj is None else sqlObj
        self.isActive = True
        self.childObj = [] if childObj is None else childObj

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if not name:
            raise ValueError("ResourceObj name is required")
        self._name = name

    @property
    def jsObj(self):
        return self._jsObj

    @jsObj.setter
    def jsObj(self, js: str):
        self.jsObj = fixup(js)

    @property
    def getJSObj(self):
        return self._getJSObj

    @getJSObj.setter
    def getJsObj(self, js: str):
        self._getJSObj = fixup(js)
        

    def PrintResource(self, version: str, apiURL: str = ""):
        # for r in resList:
        if not self.isActive or self.ResourceType != "TableBased":
            #print(f"    #Skipping resource: {self._name} ResourceType: {self.ResourceType} isActive: {self.isActive}")
            self.printFreeSQL(apiURL)
            return
        space = "        "
        name = self.name.lower()
        entity = self.entity
        # print(f"#{r} s")
        print(f"    @app.route('{apiURL}/{name}')")
        print(f"    def {name}():")
        print(f'{space}root = UserResource(models.{entity},"{self.name}"')
        self.printResAttrs(version, 1)
        self.printGetFunc(name, 1)
        self.printChildren(name, version, 1)
        print(f"{space})")
        print(f"{space}return root.Execute(request.args)")
        print("")
        

    def PrintResourceFunctions(self, parentName: str, version: str):
        """
        Print a python function based on fixed JavaScript - modification of Python still required
        Args:
            resource (ResourceObj):
        """
        if self.getJSObj is not None:
            name = self.name.lower()
            entity = self.entity.lower()
            space = "          "
            print(f"{space}def fn_{parentName}_{name}_{entity}_event(row: dict, tableRow: dict, parentRow: dict):")
            print(f"{space}{space}pass")
            print("'''")
            js = fixup(self._getJSObj)
            print(f"{space}{js}")
            print("'''")
        if self.childObj is not None:
            for child in self.childObj:
                child.PrintResourceFunctions(parentName, version)

    def printChildren(self, parentName: str, version: str, i: int):
        space = "        "
        multipleChildren = True if len(self.childObj) > 1 else False
        childCnt = 0
        for child in self.childObj:
            if child.ResourceType != "TableBased":
                continue
            cname = child._name
            childName = f"{cname}"
            childName = childName.replace("_","",2)
            attrName = child.findAttrName()
            fkey = child.createJoinOrForeignKey()
            include = "include=" if childCnt == 0  else ""
            openBracket = "[" if childCnt == 0  else ""
            print(i * f'{space}',f',{include}UserResource{openBracket}(model_class=models.{child.entity},alias="{cname}" {fkey}', end="\n")
            child.printResAttrs(version, i)
            childCnt = childCnt + 1
            if attrName is not None:
                joinType = (
                    "join" if child.jsonObj["isCollection"] is True else "joinParent"
                )
                # if joinType == "joinParent":
                if not child.jsonObj["isCollection"]:
                    print(i * f"{space}",f",isParent=True")
                if version != "5.4" and child.jsonObj["isCombined"]:
                    print(i * f"{space}",f",isCombined=True")
                
            child.printGetFunc(parentName, i)
            child.printChildren(parentName, version, i + 1)
            #print(f"{space},")
        if childCnt > 1:
            print(i * f"{space}","]")

    def createJoinOrForeignKey(self):
        attrName = self.findAttrName()
        result = ""
        if len(attrName) == 1:
            result = f",join_on=models.{self.entity}.{attrName[0].child}" 
        elif len(attrName) > 1:
            result = ",join_on=["    
            sep = ""        
            for join in attrName:
                result += f"{sep}(models.{self.entity}.{join.parent}, models.{self.entity}.{join.child})" 
                sep = ","
            result += "]"
        return result
    
    def printResAttrs(self, version: str, i: int):
        if self.jsonObj is None:
            return
        jDict = DotDict(self.jsonObj)
        if jDict.useSchemaAttributes:
            return
        if jDict.attributes is not None:
            fields = ""
            sep = ""
            for attr in jDict.attributes:
                attrName = attr["attribute"] if version == "5.4" else attr["alias"]
                fields += f'{sep} (models.{self.entity}.{attrName}, "{attrName}")'
                sep = ","
            space = "        "
            print(i * f"{space}",f",fields=[{fields}]")
        if jDict.filter is not None:
            print(i * f"{space}",f"#,filter_by=({jDict.filter})")
        order = jDict.order if version == '5.4' else jDict.sort
        if version == '5.4' and jDict.order is not None:
             print(i * f"{space}",f",order_by=(models.{self.entity}.{order})")
        if version != '5.4' and jDict.sort is not None:
             print(i * f"{space}",f",order_by=(models.{self.entity}.{order})")

    def printGetFunc(self, parentName: str, i: int):
        space = "        "
        if self._getJSObj is not None:
            fn = f"fn_{parentName}_{self._name}_{self.entity}_event"
            print(i * f"{space}",f",calling=({fn.lower()})")


    def findAttrName(self) -> list:
        #if join is a =[b] and c = [d]
        # return [(a=b),(c=d)]
        ret = [] 
        if "join" in self.jsonObj:
            joinStr = self.jsonObj["join"]
            if joinStr is not None:
                for join in joinStr.split("and"):
                    join = join.replace('"', "", 10)
                    join = join.replace("[", "")
                    join = join.replace("]", "")
                    join = join.replace(" ", "", 4)
                    j = join.split("=")
                    #p = j[1]
                    #p = p[:-1] + p[-1:].lower()
                    jo = JoinObj(j[0], j[1], "=")
                    ret.append(jo)
        return ret
    
    def printFreeSQL(self, apiURL: str = ""):
        # Return the SQL statement used by a FreeSQL query
        if self.ResourceType != "FreeSQL" or not self.isActive:
            return
        print(f"    #FreeSQL resource: {self._name} ResourceType: {self.ResourceType} isActive: {self.isActive}")
        name = self.name.lower()
        space = "        "
        print(f"    @app.route('{apiURL}/{name}')")
        print(f"    def {name}():")
        print(f'{space}sql = get_{self.name}(request.args)')
        print(f'{space}return FreeSQL(sqlExpression=sql).execute(request.args)')
        print("")
       
        print(f"def get_{name}(*args):")
        print(f'{space}pass')
        print(f'{space}#argValue = args.get("argValueName")')
        print(f'{space}"""')
        print(f"{space}return {fixupSQL(self.jsSQL)}")
        print(f'{space}"""')
        print("")

if __name__ == "__main__":
    jsonObj = {
        "name": "foo",
        "entity": "bar",
        "resourceType": "TableBased",
        "attributes": [
            {
                "attribute": "CustomerID",
                "alias": "CustomerID",
                "description": "null",
                "isKey": False,
            }
        ],
    }
    resObj = ResourceObj(parentName="v1", parentDir="", jsonObj=jsonObj)
    resObj.PrintResource("5.4","/rest/default/nw/v1")
    resObj.PrintResourceFunctions("root", "5.4")
    resObj.printFreeSQL("/rest/default/nw/v1")

