const settingsDropdown = document.getElementById('settings-dropdown');
if(settingsDropdown !== null)
{
    settingsDropdown.addEventListener("click", function stopDismiss(event){
        event.stopPropagation();
    });
}
