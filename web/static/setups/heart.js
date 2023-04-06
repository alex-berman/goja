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

const fbsOptions = {
  0: '<= 120 mg/dl',
  1: '> 120 mg/dl',
};

const restecgOptions = {
  0: 'Normal',
  1: 'ST-T wave abnormality',
  2: 'Left ventricular hypertrophy',
};

const yesOrNo = {
  1: 'Yes',
  0: 'No',
};

const slopeOptions = {
  1: 'Upsloping',
  2: 'Flat',
  3: 'Downsloping',
};

const thalOptions = {
  '3.0': 'None',
  '6.0': 'Fixed',
  '7.0': 'Reversable',
  '?': 'N/A',
};

const caOptions = {
  '0.0': '0',
  '1.0': '1',
  '2.0': '2',
  '3.0': '3',
  '?': 'N/A',
};

const border = '<tr><td colspan=2 style="padding-top: 10px; border-bottom: 1px solid #ccc;"></td></tr>';


function caseInfoAsHTML(case_info) {
  var result = '<table>';

  result += header('Clinical data');
  result += nonOptionRow('Age', case_info.age);
  result += optionRow('Sex', sexes, case_info.sex);
  result += optionRow('Chest pain', chestPainTypes, case_info.cp);
  result += nonOptionRow('Systolic blood pressure', case_info.trestbps);

  result += border;
  result += header('Test data', 'padding-top: 10px;');
  result += nonOptionRow('Serum cholesterol (mg/dl)', case_info.chol);
  result += optionRow('Fasting blood sugar', fbsOptions, case_info.fbs);
  result += optionRow('ECG at rest', restecgOptions, case_info.restecg);

  result += subHeader('Exercise', 'padding-top: 10px');
  result += nonOptionRow('Maximum heart rate', case_info.thalach);
  result += optionRow('Exercise-induced angina', yesOrNo, case_info.exang);
  result += optionRow('Peak ST segment', slopeOptions, case_info.slope);
  result += nonOptionRow('ST depression relative to rest', case_info.oldpeak);
  result += optionRow('Thallium scintigraphic defect', thalOptions, case_info.thal);
  result += optionRow('Major vessels colored by flouroscopy', caOptions, case_info.ca);

  result += '</table>';
  return result;
}

function header(title, style) {
  var result = '<tr><td colspan=2 class="caseInfoHeader"';
  if(style) {
    result += ' style="' + style + '"';
  }
  result += '>' + title + '</td></tr>';
  return result;
}

function subHeader(title, style) {
  var result = '<tr><td colspan=2 class="caseInfoSubHeader"';
  if(style) {
    result += ' style="' + style + '"';
  }
  result += '>' + title + '</td></tr>';
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