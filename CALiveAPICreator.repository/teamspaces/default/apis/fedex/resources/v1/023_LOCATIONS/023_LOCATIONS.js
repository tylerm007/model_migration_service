var values = [
  "YVR"
 ,"YYC"
 ,"YYZ"
 ,"YMX"
 ,"YEG"
 ,"YWG"
];

var results = [];
for (var idx = 0; idx < values.length; ++idx) {
  var v = values[idx];
  results.push({value: v, viewValue: v});
}

return results;
