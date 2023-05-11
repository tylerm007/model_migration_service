from util import to_camel_case


class ResourceObj:
    
    def __init__(self, dirpath, jsonObj: object, jsObj: any = None):
        name = jsonObj["name"]
        self.parentName = dirpath
        self._name = name
        entity = to_camel_case(name)
        if "entity" in jsonObj:
            entity = to_camel_case(jsonObj["entity"])
        self.entity = entity
        self.ResourceType = jsonObj["resourceType"]
        self.jsonObj = jsonObj
        self.jsObj = jsObj
        self.getJSObj = None
        self.sqlObj = None
        self.isActive = True
        self.childObj = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
