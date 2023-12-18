switch (logicContext.initialVerb) {
case 'INSERT':
  return req.apiKey.userIdentifier || 999999;
case 'UPDATE':
  return oldRow.CREATE_UID;
case 'DELETE':
  return row.CREATE_UID;
}
