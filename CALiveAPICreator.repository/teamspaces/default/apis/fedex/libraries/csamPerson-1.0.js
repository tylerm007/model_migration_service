// getCommonPersonColumns
// getPersonByFedExIdNbr
// getPersonsByJobNbrs
// getPersonsByOrgCdJobNbrPairs
// getPersonJobTypeForPerson(personRow)

/**
 * return most commonly used person columns
 */
function getCommonPersonColumns() {
  return ['FEDEX_ID_NBR', 'FIRST_NM', 'LAST_NM', 'PREF_NM', 'ORG_CD', 'JOB_NBR', 'EMP_CAT_CD2', 'COMIL_NBR', 'EMAIL_DESC', 'MGR_EMP_NBR'];
}

/** find a single person given fedex id number
 * nbr - fedex id number of wanted person
 * allColumns - if provided and truthy, all columns are returned, o.w. just the common ones
 * throwIfNotFound - if truthy, throw and error when not found instead of returning null
 * Commonly Fields
 * FEDEX_ID_NBR
 * FIRST_NM
 * LAST_NM
 * PREF_NM
 * ORG_CD
 * JOB_NBR
 * EMP_CAT_CD2
 * COMIL_NBR (aka centre)
 * EMAIL_DESC
 */
function getPersonByFedExIdNbr(nbr, allColumns, throwIfNotFound) {
  var params = {
    columns: allColumns ? null : getCommonPersonColumns(),
    usingValues: {
      FEDEX_ID_NBR: nbr
    }
  };

  var p = SysUtilityV2.findEntities('dss:PERSON', params);
  if (null === p || 0 === p.length) {
    if (throwIfNotFound) {
      throw 'Cannot find employee ' + nbr;
    }
    return null;
  }

  p[0].Full_Name = preferredFullNameFromRow(p[0]);

  return p[0];
}

/**
 * find all person records given an array of jobNbrs
 */
function getPersonsByJobNbrs(jobNbrs, allColumns, includeTerminated) {
  jobNbrs = toArray(jobNbrs);
  if (!jobNbrs || 0 === jobNbrs.length) {
    return null;
  }

  var where = 'JOB_NBR in (\'' + jobNbrs.join('\',\'') + '\')';

  if (!includeTerminated) {
    where += '\n      and EMP_CAT_CD2 != \'T\'';
  }

  var params = {
    columns: allColumns ? null : getCommonPersonColumns(),
    whereClause: where
  };

  var p = SysUtilityV2.findEntities('dss:PERSON', params);
  for (var idx = 0; idx < p.length; ++idx) {
    p[idx].Full_Name = preferredFullNameFromRow(p[idx]);
  }

  return p;
}

/**
 * find all person records given an array of orgCd, jobNbr paiars
 */
function getPersonsByOrgCdJobNbrPairs(orgCdjobNbrPairs, allColumns, includeTerminated) {
  if (!orgCdjobNbrPairs || 0 === orgCdjobNbrPairs.length) {
    return [];
  }

  var where = '      (';

  for (var i = 0; i < orgCdjobNbrPairs.length; ++i) {
    var pair = orgCdjobNbrPairs[i];
    where += (0 === i) ? '      ' : '\n  or ';
    where += '(ORG_CD = \'' + pair.ORG_CD + '\' and JOB_NBR = \'' + pair.JOB_NBR + '\')';
  }

  where += '\n      )';

  if (!includeTerminated) {
    where += '\n      and EMP_CAT_CD2 != \'T\'';
  }

  var params = {
    columns: allColumns ? null : getCommonPersonColumns(),
    whereClause: where
  };

  var p = SysUtilityV2.findEntities('dss:PERSON', params);
  for (var idx = 0; idx < p.length; ++idx) {
    p[idx].Full_Name = preferredFullNameFromRow(p[idx]);
  }

  return p;
}

function getPersonJobTypeForPerson(person) {
  var params = {
    columns: null,
    usingValues: {
      JOB_NBR: person.JOB_NBR,
      ORG_CD: person.ORG_CD
    }
  };

  var p = SysUtilityV2.findEntities('main:PERSON_JOB_TYPE', params);
  return p.length > 0 ? p[0] : null;
}
