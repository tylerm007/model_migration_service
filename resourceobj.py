from util import to_camel_case, fixup
import json


class ResourceObj:
    def __init__(
        self,
        dirpath,
        jsonObj: dict,
        jsObj: str = None,
        sqlObj: str = None,
        getJsObj: str = None,
        childObj: list[object] = None,
    ):
        if not jsonObj:
            raise ValueError("JSON Object [dict] is required for ResourceObj")
        self.jsonObj = jsonObj
        self.parentName = dirpath
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
        
    @classmethod
    def PrintResource(cls, r, version):
        # for r in resList:
        if not r.isActive:
            return
        space = "        "
        name = r.name.lower()
        entity = r.entity
        # print(f"#{r} s")
        print(f"    @app.route('/{name}')")
        print(f"    def {name}():")
        print(f'{space}root = UserResource(models.{entity},"{r.name}"')
        printResAttrs("root", r, version, 1)
        printGetFunc("root", r, 1)
        printChildren(r, "root", version, 1)
        print(f"{space})")
        print(f"{space}key = request.args.get(root.parentKey)")
        #print(f'{space}limit = request.args.get("page_limit")')
        #print(f'{space}offset = request.args.get("page_offset")')
        print(f"{space}result = root.execute(root, key")
        print('        return jsonify({"success": True, f"{root.name}": result})')
        print("")
        # these are the get_event.js
        
    def PrintResourceFunctions(self, version: str):
        """
        Print a python function based on fixed JavaScript - modification of Python still required
        Args:
            resource (ResourceObj):
        """
        if self.getJSObj is not None:
            name = self.name.lower()
            entity = self.entity.lower()
            space = "          "
            print(f"{space}def fn_{name}_{entity}_event(row: any):")
            print(f"{space}{space}pass")
            print("'''")
            print(f"{space}{self._getJSObj}")
            print("'''")
        if self.childObj is not None:
            for child in self.childObj:
                child.PrintResourceFunctions(version)
        
def printChildren(
    resource: ResourceObj, parent_name: str, version: str, i: int
):
    space = "        "
    for child in resource.childObj:
        cname = child._name
        childName = f"{cname}_{i}"
        print(i * f"{space}", f'include=[(models.{child.entity},"{cname}"')
        printResAttrs(childName, child, version, i)
        attrName = findAttrName(child)
        if attrName is not None:
            joinType = (
                "join"
                if child.jsonObj["isCollection"] is True
                else "joinParent"
            )
            if joinType == "joinParent":
                isCombined = (
                    "True" if child.jsonObj["isCombined"] is True else "False"
                )
                if not isCombined:
                    print(i * f"{space},isParent=True")
                #print(
                #   f"{space}Resource.{joinType}({parent_name}, {childName}, models.{resource.entity}.{attrName[1]}, {isCombined})"
                #)
            #else:
                #print(
                #    f"{space}Resource.{joinType}({parent_name}, {childName}, models.{child.entity}.{attrName[0]})"
                #)
        printGetFunc(childName, child, i + 1)
        printChildren(child, childName, version, i + 1)
        print(i * f"{space},  )")
        print(i * f"{space} ]")

def printResAttrs(name: str, resource: ResourceObj, version: str, i: int):
    if resource.jsonObj is None:
        return
    if "attributes" in resource.jsonObj:
        fields = ""
        sep = ""
        for attr in resource.jsonObj["attributes"]:
            space = "        "
            attrName = attr["attribute"] if version == "5.4" else  attr["alias"]
            fields +=  f'{sep} (models.{resource.entity}.{attrName}, "{attrName}")'
            sep = ","
            
        print(i * f"{space},fields=[{fields}]")

def printGetFunc(name: str, res: ResourceObj , i: int):
    if res._getJSObj is not None:
        fn = f"fn_{name}_{res.entity}_event"
        print(i * f"'     ',calling=({fn})")

def findAttrName(resObj: ResourceObj):
    if resObj.ResourceType == "TableBased":
        join = resObj.jsonObj["join"]
        if join is not None:
            ret = []
            join = join.replace('"', "", 10)
            join = join.replace("[", "")
            join = join.replace("]", "")
            join = join.replace(" ", "", 4)
            for j in join.split("="):
                ret.append(j)
            return ret
        
    


if __name__ == "__main__":
    jsonObj ={
        "name": "foo",
        "entity" : "bar",
        "resourceType": "TableBased",
        "attributes": [
        {
            "attribute": "CustomerID",
            "alias": "CustomerID",
            "description": "null",
            "isKey": False
        }
        ]
    }
    resObj = ResourceObj("",jsonObj,"","","","") 
    ResourceObj.PrintResource( resObj, "5.4")
    ResourceObj.PrintResourceFunctions(resObj, "5.4")