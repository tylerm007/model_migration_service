var DateTimeFormatter = Java.type('java.time.format.DateTimeFormatter');
var OffsetDateTime = Java.type('java.time.OffsetDateTime');
var ZoneId = Java.type('java.time.ZoneId');

var dtStr = row.CREATE_TMSTP.truncateFractional(0).asSQLServerTimestampOffsetFormat();
var dtm = OffsetDateTime.parse(dtStr, DateTimeFormatter.ofPattern('yyyy-MM-dd HH:mm:ss xxx'));
var etTS = dtm.toInstant().atZone(ZoneId.of('America/Toronto'));

var fmt = DateTimeFormatter.ofPattern('yyyy-MM-dd HH:mm');
virtuals.CREATE_TMSTP_ET = fmt.format(etTS);
