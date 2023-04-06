const sexes = {
  1: 'Male',
  0: 'Female',
};

const chestPainTypes = {
  1: 'Typical angina',
  2: 'Atypical angina',
  3: 'Non-anginal pain',
  4: 'Asymptomatic',
};

function caseInfoAsHTML(case_info) {
  var result = '<table>';

  // Clinical variables
  result += nonOptionRow('Age', case_info.age);
  result += optionRow('Sex', sexes, case_info.sex);
  result += optionRow('Chest pain', chestPainTypes, case_info.cp);
  result += nonOptionRow('Systolic blood pressure', case_info.trestbps);

  // Electrocardiogram

  // Exercise thallium scintigraphy

  // fluoroscopy for coronary calcium

  result += '</table>';
  return result;
}

function nonOptionRow(featureDescription, value) {
  return tableRow(featureDescription, 'nonOptionFeatureDescription', value);
}

function optionRow(featureDescription, options, highlightedValue) {
  return tableRow(featureDescription, 'optionFeatureDescription', optionsAsHTML(options, highlightedValue));
}

function optionsAsHTML(options, highlightedValue) {
  var result = '<select>';
  for (const [value, description] of Object.entries(options)) {
    var attribute = (value == highlightedValue) ? "selected" : "disabled";
    result += '<option ' + attribute + '>' + description;
  }
  result += '</select>';
  return result;
}

function tableRow(featureDescription, featureDescriptionClass, generatedFeatureValue) {
  return '<tr><td class="caseInfoCell ' + featureDescriptionClass + '">' + featureDescription +
    '</td><td class="caseInfoCell">' + generatedFeatureValue + '</td></tr>';
}