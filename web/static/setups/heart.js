const genders = {
  1: 'Male',
  0: 'Female',
};

const chestPainTypes = {
  1: 'typical angina',
  2: 'atypical angina',
  3: 'non-anginal pain',
  4: 'asymptomatic',
};

function caseInfoAsHTML(case_info) {
  var result = '<table>';
  result += tableRow('Age', case_info.age);
  result += tableRow('Gender', lookup(genders, case_info.sex));
  result += tableRow('Chest pain', lookup(chestPainTypes, case_info.cp));
  result += '</tabke>';
  return result;
}

function lookup(table, value) {
  if(table.hasOwnProperty(value)) {
    return table[value];
  }
  return 'N/A';
}

function tableRow(featureDescription, generatedFeatureValue) {
  return '<tr><td>' + featureDescription + '</td><td>' + generatedFeatureValue + '</td></tr>';
}