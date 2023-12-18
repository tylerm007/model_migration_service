/**
 * posts to /cscom/v1/cs_REQUEST which logs and sends an email
 * to - array of email addresses, such as ['David Hewitt <david.hewitt.osv@fedex.com', 'Wynford Rees <wynford.rees@fedex.com']
 * cc - optional array of cc email addresses
 * bcc - optional array of bcc email addresses
 * from - currently ignored, future db schema change, use null for now
 * subject - text of subject
 * body - text of body
 * attachments - optional array of attachments.
 * such as
 *  [
 *   {
 *     name: 'foo.csv',
 *     contents: 'now,is\nthe,time\n0,1',
 *     mimeType: 'text/csv'
 *   },
 *   {
 *     name: 'foo.csv',
 *     contents: java byte array,
 *     mimeType: 'application/octet-stream'
 *   }
 * ]
 */
function sendEmailViaRequest(req, to, cc, bcc, from, subject, body, attachments) {
  // provides Base64Util.encodeString, encodeBytes, decodeBytes, decodeString
  var Base64Util = Java.type('com.kahuna.server.util.Base64Util');

  var emailTo = toArray(to).join(',');
  var emailCC = null === cc ? null : toArray(cc).join(',');
  var emailBCC = null === bcc ? null : toArray(bcc).join(',');

  var baseUrl = getBaseUrl(req);
  baseUrl = baseUrl.replace('/http/', '/rest/');

  var key = req.apiKey.apiKey;
  var headerSettings = {
    headers: {
      Authorization: 'CALiveAPICreator ' + key + ':1'
    }
  };

  var eventPostURL = baseUrl + '/cscom/v1/cs_REQUEST';

  var requestData = {
    EMAIL_TO_DESC: emailTo,
    EMAIL_SUBJECT_DESC: subject,
    EMAIL_BODY_DESC: body
  };

  if (null !== emailCC) {
    requestData.EMAIL_CC_DESC = emailCC;
  }

  if (null !== emailBCC) {
    requestData.EMAIL_BC_DESC = emailBCC;
  }

  if (null !== attachments) {
    requestData.ATTACHMENTS = [];
    for (var idx = 0; idx < attachments.length; ++idx) {
      var attachment = attachments[idx];
      var mimeType = attachment.mimeType || 'application/octet-stream';
      var attachmentName = attachment.name || 'NotProvided';
      var contents = attachment.contents;
      var attachmentDefn = {
        NAME: attachmentName,
        MIME_TYPE: mimeType
      };
      if ('string' === typeof contents) {
        attachmentDefn.CONTENTS_TEXT = contents;
      }
      else {
        // assume byte array
        attachmentDefn.CONTENTS_BINARY = 'b64:' + Base64Util.encodeBytes(contents);
      }

      requestData.ATTACHMENTS.push(attachmentDefn);
    }
  }

  var retJson = SysUtility.restPost(eventPostURL, '', headerSettings, requestData);
  var resultObject = JSON.parse(retJson);
  return resultObject;
}
