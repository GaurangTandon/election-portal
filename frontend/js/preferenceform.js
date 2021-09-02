const form = document.getElementById('PreferenceForm');
const count = form.length;
const error = document.getElementById('error');
const checkboxError = document.getElementById('checkbox-error');
const checkbox = document.getElementById('flexCheckDefault');
const submitButton = document.getElementById('submitButton');
const clearButton = document.getElementById("clearButton");

let preferences = [];

clearButton.addEventListener("click", function clearall(){
  form.reset();

  error.classList.remove("showerror");
  checkbox.checked = false;
  checkboxError.classList.remove("showerror");
  // error.classList.add("showerror");
  // checkboxError.classList.add("showerror");

  // checkboxError.style.display = 'none';
  // error.style.display = 'none';
  window.localStorage.setItem('preferences', JSON.stringify([]));
});

form.addEventListener("change", function check(par){

  let cur = par.target;
  for (let i = 0; i < count; i += 1) {
    if (form[i].value === cur.value && form[i] !== cur) {
        form[i].value = '';
    }
  }
  for (let i = 0; i < count; i += 1) {
    preferences[i] = form[i].value;
  }
  window.localStorage.setItem('preferences', JSON.stringify(preferences));
});


submitButton.addEventListener("click", function submit(){
  // error.style.display = 'none';
  // checkboxError.style.display = 'none';

  error.classList.remove("showerror");
  checkboxError.classList.remove("showerror");
  
  for (let i = 0; i < count; i += 1) {
      preferences[i] = form[i].value;
  }
  // console.log(preferences)

  if (preferences[0] === '') {
      // console.log('empty');
      // error.classList.add(SHOW_CLS);
      error.classList.add("showerror");
      // error.style.display = 'block';
      return false;
  }

  for (let i = 0; i < count; i += 1) {
      if (preferences[i] === '') {
        for (let j = i + 1; j < count; j += 1) {
            if (preferences[j] !== '') {
                // console.log('wrong order');
                // error.style.display = 'block';
                error.classList.add("showerror");
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
        // checkboxError.style.display = 'block';
        checkboxError.classList.add("showerror");
      }
  }
  // return preferences
  // console.log(preferences);
  window.localStorage.setItem('preferences', JSON.stringify(preferences));
  if (checkbox.checked === true) {
      submitButton.href = '../html/index.html';
  } else {
      // checkboxError.style.display = 'block';
      checkboxError.classList.add("showerror");
  }
});

function getpref() {
    preferences = JSON.parse(localStorage.getItem('preferences'));
    // console.log(preferences)
    for (let i = 0; i < count; i += 1) {
        form[i].value = preferences[i];
    }
    // console.log(document.getElementById("flexCheckDefault").checked)
}

document.getElementById("settings-dropdown").addEventListener("click", function stopDismiss(event)
{
  event.stopPropagation();
});