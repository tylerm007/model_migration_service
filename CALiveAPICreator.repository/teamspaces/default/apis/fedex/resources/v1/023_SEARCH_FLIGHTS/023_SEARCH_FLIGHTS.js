var flightData = [
  '140 OAK YVR',
  '142 MEM YVR',
  '128 MEM YYZ',
  '132 MEM YYZ',
  '150 IND YYZ',
  '160 EWR YYZ',
  '232 MEM YYZ',
  '130 MEM YMX',
  '152 IND YMX',
  '138 IND YMX',
  '236 MEM YYC',
  '120 MEM YEG',
  '8065 MEM YWG',
  'MC216 MEM YWG'
];

var destFlights = getDestinations(flightData);

var results = [];

for (var dest in destFlights) {
  var flights = destFlights[dest];

  // emit the 'all' version
  var all = {
    value: 'all' + dest.toLowerCase(),
    viewValue: '--- All ' + dest.toUpperCase() + ' Flights (' + flights.length + ') ---',
    search: genSearch(flights)
  };

  results.push(all);

  for (var idx = 0; idx < flights.length; ++idx) {
    var f = flights[idx];
    var flightName = 'FLT ' + f.flight + ' (' + f.departure + '-' + f.destination + ')';
    results.push({
      value: f.flight,
      viewValue: flightName,
      search: genSearch([f])
    });
  }
}

return results;


function getDestinations(flightData) {
  var r = {};

  for (var idx = 0; idx < flightData.length; ++idx) {
    var x = flightData[idx].split(' ');
    var f = {
      flight: x[0],
      departure: x[1],
      destination: x[2]
    };
    r[f.destination] = (r[f.destination] || []);
    r[f.destination].push(f);
  }

  return r;
}

function genSearch(flights) {
  if (1 === flights.length) {
    return 'equal(\'FLT\':\'' + flights[0].flight + '\')';
  }

  var s = '';

  for (var idx = 0; idx < flights.length; ++idx) {
     var f = flights[idx];
     s += 0 === idx ? '' : ',';
     s += "'FLT':'" + f.flight + "'";
  }

  return 'equal_or(' + s + ')';
}
