      

var count = (document.getElementById("PreferenceForm")).length
var form = document.getElementById("PreferenceForm")
// console.log(preferences = window.localStorage.getItem('preferences'))

// const preferences = []
// console.log(preferences = JSON.parse(window.localStorage.getItem('preferences')))
// try
// {
//   console.log(const preferences = JSON.parse(window.localStorage.getItem('preferences')))
// }
// catch
// {
//   const preferences = []
// }

// console.log(count)

let preferences = []

// if (window.localStorage.getItem('preferences') != null)
// {
//   preferences = JSON.parse(window.localStorage.getItem('preferences'))
// }

function clearall()
{
  document.getElementById("PreferenceForm").reset()
  document.getElementById("error").style.display = "none";
  window.localStorage.setItem('preferences',JSON.stringify([]))
}

function check(x)
{
  for(let i = 0; i < count; i++)
  {
    if ( form[i].value == x.value && form[i] != x)
    {
      form[i].value = ""
    } 
  }
  for(let i = 0; i < count; i++)
  {
    preferences[i] = form[i].value
  }
  window.localStorage.setItem('preferences',JSON.stringify(preferences))
}

function submit()
{
  document.getElementById("error").style.display = "none";
  document.getElementById("checkbox-error").style.display = "none";
  for(let i = 0; i < count; i++)
  {
    preferences[i] = form[i].value
  }
  // console.log(preferences)

  if(preferences[0] == "")
  {
    console.log("empty")
    document.getElementById("error").style.display = "block";
    return false
  }

  for(let i = 0; i < count; i++)
  {
    if(preferences[i] == "")
    {
      for(let j = i+1; j < count; j++)
      {
        if(preferences[j] != "")
        {
          // return false
          console.log("wrong order")
          document.getElementById("error").style.display = "block";
          return false
        }
      }
      // return preferences
      console.log(preferences)
      window.localStorage.setItem('preferences',JSON.stringify(preferences))
      if(document.getElementById("flexCheckDefault").checked == true)
      {
        document.getElementById("submitButton").href = "../html/index.html"
        return
      }
      else
      {
        document.getElementById("checkbox-error").style.display = "block";
      }
      
    }
  }
  // return preferences
  console.log(preferences)
  window.localStorage.setItem('preferences',JSON.stringify(preferences))
  if(document.getElementById("flexCheckDefault").checked == true)
  {
    document.getElementById("submitButton").href = "../html/index.html"
  }
  else
  {
    document.getElementById("checkbox-error").style.display = "block";
  }
}

// document.getElementById("clearButton").onclick = clearall()

function getpref()
{
  preferences = JSON.parse(localStorage.getItem('preferences'))
  // console.log(preferences)
  for(let i = 0; i < count; i++)
  {
    form[i].value = preferences[i]
  }
  // console.log(document.getElementById("flexCheckDefault").checked)
}





