// Common Functions:
// nullToBlank()
// toArray()
// getBaseUrl(req)
// encodeHtml(s)
// emailNewlineFixup(s)
// preferredFullName(lastName, firstName, preferredName)
// preferredFullNameFromRow(row)

/**
 * return the empty string for null or undefined
 */
function nullToBlank(s) {
  return (null === s || undefined === s) ? "" : s;
}

function toArray(obj) {
  if (null === obj || undefined === obj) {
    return obj;
  }
  else if (Array.isArray(obj)) {
    return obj;
  }
  else {
    return [obj];
  }
}

function getBaseUrl(req) {
  var baseUrl = String(req.fullBaseURL);
  baseUrl = baseUrl.substr(0, baseUrl.indexOf('/' + req.project.urlName + '/'));
  return baseUrl;
}

/**
 * Given an optional string, encode html entities
 * should be expanded overtime to include more entities.
 */
function encodeHtml(s) {
  if (null === s) {
    return null;
  }

  var result = '';
  for (var idx = 0; idx < s.length; ++idx) {
    var chr = s.charAt(idx);
    switch (chr) {
    case '<':
      result += '&lt;';
      break;
    case '>':
      result += '&gt;';
      break;
    case '&':
      result += '&amp;';
      break;
    default:
      result += chr;
      break;
    }
  }

  return result;
}

/**
 * Given an optional string, replace 'newlines' with <br> suitable for email
 */
function emailNewLineFixup(s) {
  if (null === s) {
    return null;
  }

  s = s.replaceAll('\r\n', '\n');
  s = s.replaceAll('\r', '\n');

  return s;
}

/**
 * generate a 'full name', using preferred name if given
 */
function preferredFullName(lastName, firstName, preferredName) {
  lastName = (lastName || 'unknown').trim();
  firstName = (firstName || '').trim();
  preferredName = (preferredName || '').trim();
  return (('' !== preferredName ? preferredName : firstName) + ' ' + lastName).trim();
}

function preferredFullNameFromRow(row) {
  var lastName = row.LAST_NM;
  var firstName = row.FIRST_NM;
  var preferredName = row.PREF_NM;
  return preferredFullName(lastName, firstName, preferredName);
}
