const settingsDropdown = document.getElementById('settings-dropdown');

settingsDropdown.addEventListener("click", function stopDismiss(event){
    event.stopPropagation();
});