const form = document.getElementById('PreferenceForm');
const count = form.length;
const error = document.getElementById('error');
const checkboxError = document.getElementById('checkbox-error');
const checkbox = document.getElementById('flexCheckDefault');
const submitButton = document.getElementById('submitButton');
// console.log(preferences = window.localStorage.getItem('preferences'))

let preferences = [];

function clearall() {
  form.reset();
  error.style.display = 'none';
  window.localStorage.setItem('preferences', JSON.stringify([]));
}

function check(x) {
  for (let i = 0; i < count; i += 1) {
    if (form[i].value === x.value && form[i] !== x) {
      form[i].value = '';
    }
  }
  for (let i = 0; i < count; i += 1) {
    preferences[i] = form[i].value;
  }
  window.localStorage.setItem('preferences', JSON.stringify(preferences));
}

function submit() {
  error.style.display = 'none';
  checkboxError.style.display = 'none';
  for (let i = 0; i < count; i += 1) {
    preferences[i] = form[i].value;
  }
  // console.log(preferences)

  if (preferences[0] === '') {
    // console.log('empty');
    error.style.display = 'block';
    return false;
  }

  for (let i = 0; i < count; i += 1) {
    if (preferences[i] === '') {
      for (let j = i + 1; j < count; j += 1) {
        if (preferences[j] !== '') {
          // console.log('wrong order');
          error.style.display = 'block';
          return false;
        }
      }
      // return preferences
      // console.log(preferences);
      window.localStorage.setItem('preferences', JSON.stringify(preferences));
      if (checkbox.checked === true) {
        submitButton.href = '../html/index.html';
        return true;
      }
      checkboxError.style.display = 'block';
    }
  }
  // return preferences
  // console.log(preferences);
  window.localStorage.setItem('preferences', JSON.stringify(preferences));
  if (checkbox.checked === true) {
    submitButton.href = '../html/index.html';
  } else {
    checkboxError.style.display = 'block';
  }
}

// document.getElementById("clearButton").onclick = clearall()

function getpref() {
  preferences = JSON.parse(localStorage.getItem('preferences'));
  // console.log(preferences)
  for (let i = 0; i < count; i += 1) {
    form[i].value = preferences[i];
  }
  // console.log(document.getElementById("flexCheckDefault").checked)
}
