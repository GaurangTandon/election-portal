const form = document.getElementById('PreferenceForm');
const count = form ? form.length - 1 : 0;
const error = document.getElementById('error');
const checkboxError = document.getElementById('checkbox-error');
const checkbox = document.getElementById('flexCheckDefault');
const submitButton = document.getElementById('submitButton');
const clearButton = document.getElementById('clearButton');
const voteButton = document.getElementById('vote-button');

let preferences = [];

if (clearButton) {
    clearButton.addEventListener("click", function clearall() {
        form.reset();
        checkbox.checked = false;
        error.classList.add("error");
        error.classList.remove("showerror");
        checkboxError.classList.add("error");
        checkboxError.classList.remove("showerror");
        window.localStorage.setItem('preferences', JSON.stringify([]));
    });
}

if (form) {
    form.addEventListener("change", function check(par) {
        let cur = par.target;
        for (let i = 0; i < count; i += 1) {
            if (form[i].value !== "" && form[i].value === cur.value && form[i] !== cur) {
                form[i].value = '';
            }
        }
        for (let i = 0; i < count; i += 1) {
            preferences[i] = form[i].value;
        }
        window.localStorage.setItem('preferences', JSON.stringify(preferences));
    });
}

// const SHOW_CLS = "show";
if (submitButton) {
    submitButton.addEventListener("click", function submit() {
        error.classList.add("error");
        error.classList.remove("showerror");
        checkboxError.classList.add("error")
        checkboxError.classList.remove("showerror");
        for (let i = 0; i < count; i += 1) {
            preferences[i] = form[i].value;
        }
        // console.log(preferences)

        // if (preferences[0] === '') {
        //     // console.log('empty');
        //     // error.classList.add(SHOW_CLS);
        //     error.classList.remove("error");
        //     error.classList.add("showerror");
        //     return false;
        // }

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
            }
        }
        window.localStorage.setItem('preferences', JSON.stringify(preferences));
        if (checkbox.checked === true) {
            form.submit();
        } else {
            checkboxError.classList.remove("error")
            checkboxError.classList.add("showerror");
        }
    });
}

if (voteButton) {
    window.getpref = function () {
        preferences = JSON.parse(localStorage.getItem('preferences'));
        if (preferences === null) {
            preferences = [];
        }
        // console.log(preferences)
        for (let i = 0; i < count; i += 1) {
            form[i].value = preferences[i];
        }
        // console.log(document.getElementById("flexCheckDefault").checked)
    };
    // document.getElementById("clearButton").onclick = clearall()
    voteButton.addEventListener("click", getpref);
}
