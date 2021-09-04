const form = document.getElementById('PreferenceForm');
const count = form.length - 1;
const error = document.getElementById('error');
const checkboxError = document.getElementById('checkbox-error');
const checkbox = document.getElementById('flexCheckDefault');
const submitButton = document.getElementById('submitButton');
const clearButton = document.getElementById('clearButton');
const voteButton = document.getElementById('vote-button');

let preferences = [];

clearButton.addEventListener("click", function clearall(){
    form.reset();
    checkbox.checked = false;
    error.classList.add("error");
    error.classList.remove("showerror");
    checkboxError.classList.add("error");
    checkboxError.classList.remove("showerror");
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

// const SHOW_CLS = "show";

submitButton.addEventListener("click", function submit(){
    error.classList.add("error");
    error.classList.remove("showerror");
    checkboxError.classList.add("error")
    checkboxError.classList.remove("showerror");
    for (let i = 0; i < count; i += 1) {
        preferences[i] = form[i].value;
    }
    // console.log(preferences)

    if (preferences[0] === '') {
        // console.log('empty');
        // error.classList.add(SHOW_CLS);
        error.classList.remove("error");
        error.classList.add("showerror");
        return false;
    }

    for (let i = 0; i < count; i += 1) {
        if (preferences[i] === '') {
            for (let j = i + 1; j < count; j += 1) {
                if (preferences[j] !== '') {
                    // console.log('wrong order');
                    error.classList.remove("error");
                    error.classList.add("showerror");
                    return false;
                }
            }
            // return preferences
            // console.log(preferences);
            window.localStorage.setItem('preferences', JSON.stringify(preferences));
            if (checkbox.checked === true) {
                form.submit();
                window.localStorage.setItem('preferences', JSON.stringify([]));
                return true;
            }
            checkboxError.classList.remove("error")
            checkboxError.classList.add("showerror");
        }
    }
    // return preferences
    // console.log(preferences);
    window.localStorage.setItem('preferences', JSON.stringify(preferences));
    if (checkbox.checked === true) {
        form.submit();
        window.localStorage.setItem('preferences', JSON.stringify([]));
    } else {
        checkboxError.classList.remove("error")
        checkboxError.classList.add("showerror");
    }
});

// document.getElementById("clearButton").onclick = clearall()
voteButton.addEventListener("click", function getpref(){
    preferences = JSON.parse(localStorage.getItem('preferences'));
    if (preferences === null) {
        preferences = [];
    }
    // console.log(preferences)
    for (let i = 0; i < count; i += 1) {
        form[i].value = preferences[i];
    }
    // console.log(document.getElementById("flexCheckDefault").checked)
});


