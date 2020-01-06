const changeDivToUpdate = () => {
    var updateTab = document.getElementById('update-user-form');
    var securityTab = document.getElementById('last-login-table');
    var removeTab = document.getElementById('delete-user-form');
    console.log("display test");
    console.log(updateTab.style.display);
    updateTab.style.display = "block";
    securityTab.style.display = "none";
    removeTab.style.display = "none";
};

const changeDivToSecurity = () => {
    var updateTab = document.getElementById('update-user-form');
    var securityTab = document.getElementById('last-login-table');
    var removeTab = document.getElementById('delete-user-form');
    updateTab.style.display = "none";
    securityTab.style.display = "block";
    removeTab.style.display = "none";
};

const changeDivToRemove = () => {
    var updateTab = document.getElementById('update-user-form');
    var securityTab = document.getElementById('last-login-table');
    var removeTab = document.getElementById('delete-user-form');
    updateTab.style.display = "none";
    securityTab.style.display = "none";
    removeTab.style.display = "block";
};