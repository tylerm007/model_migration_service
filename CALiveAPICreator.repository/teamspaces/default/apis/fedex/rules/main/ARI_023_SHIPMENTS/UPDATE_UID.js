switch (logicContext.initialVerb) {
case 'INSERT':
case 'UPDATE':
  return req.apiKey.userIdentifier || 999999;
default:
  return row.UPDATE_UID;
}
