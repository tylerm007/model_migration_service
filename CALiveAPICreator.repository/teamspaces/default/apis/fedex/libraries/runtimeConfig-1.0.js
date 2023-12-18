function commonRuntimeConfiguration() {
  var RestRequest = Java.type('com.kahuna.server.rest.RestRequest');
  var req = RestRequest.getCurrentRestRequest();
  var Project = Java.type("com.kahuna.admin.entity.Project");
  var Resource = Java.type("com.kahuna.admin.entity.Resource");

  var accountIdent = req.account.ident;
  var commonProject = Project.getByUrlName(accountIdent, "cscom");
  var resource = Resource.getByName(commonProject, "runtime", "configuration");

  return JSON.parse(resource.getExtendedPropertiesJSON());
}
