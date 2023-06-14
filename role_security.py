# Copyright (C) 2005-2024 the Archimedes authors and contributors
# <see AUTHORS file>
#
# This module is part of Archimedes and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
"""
This is a utility to read the CA Live API Creator file based repository and print a report that can be used to help migrate 
to API Logic Server (a Python API open-source tool) https://apilogicserver.github.io/Docs/
"""

class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class entityRole():
    
    def __init__ (
        self,
        entityName: str,
        accessLevels: list,
        rowFilter: any,
        columnFilter: any,
        description: str
    ):
        self.entityName = entityName
        self.accessLevels = accessLevels
        self.rowFilter = rowFilter
        self.columnFilter = columnFilter
        self.description = description
    
    
class Role():
    
    def __init__ (
        self,
        roleName: str
        ):
        
        self.roleName = roleName
        self.tablePermission = ""
        self.viewPermission = ""
        self.functionPermission = ""
        self.apiVisibility = {}
        self.entityRoleList: list["entityRole"] = []
        
    def printRole(self):
        print(f"\t{self.roleName} = '{self.roleName}'")
        
    def printGrants(self):
        for erl in self.entityRoleList:
            print(f"#Access Levels: {erl.accessLevels} TablePermissions: {self.tablePermission} description: {erl.description}")
            print(f"Grant(on_entity=models.{erl.entityName}, to_role=Roles.{self.roleName})")
            print("")
        
    def loadEntities(self, jsonObj: dict):
        jsonDict = DotDict(jsonObj)
        self.tablePermission = jsonDict.defaultTablePermission
        self.viewPermission = jsonDict.defaultViewPermission
        self.functionPermission = jsonDict.defaultFunctionPermission
        self.apiVisibility = jsonDict.apiVisibility
        entityRoles = []
        for entity in jsonDict.entityPermission:
            ent = jsonDict.entityPermission[entity]
            entName = ent["entity"].split(":")[1]
            entityRoleObj = entityRole(entityName=entName, accessLevels=ent['accessLevels'], rowFilter=ent['rowFilter'], columnFilter=ent['columnFilter'],description=entity)
            entityRoles.append(entityRoleObj)
            
        self.entityRoleList = entityRoles