const createBackgroundTabColor = (updateColor, securityColor, removeColor ) => {
    var updateTab = document.getElementById('update-tab');
    var securityTab = document.getElementById('security-tab');
    var removeTab = document.getElementById('remove-tab');
    updateTab.style.backgroundColor = updateColor;
    securityTab.style.backgroundColor = securityColor;
    removeTab.style.backgroundColor = removeColor;
};

const changeDivToUpdate = () => {
    var updateContentTab = document.getElementById('update-user-form');
    var securityContentTab = document.getElementById('last-login-table');
    var removeContentTab = document.getElementById('delete-user-form');
    updateContentTab.style.display = "block";
    securityContentTab.style.display = "none";
    removeContentTab.style.display = "none";

    createBackgroundTabColor('#ccc', '', '');
    // var updateTab = document.getElementById('update-tab');
    // var securityTab = document.getElementById('security-tab');
    // var removeTab = document.getElementById('remove-tab');
    // updateTab.style.backgroundColor = '#ccc';
    // securityTab.style.backgroundColor = '';
    // removeTab.style.backgroundColor = '';
};

const changeDivToSecurity = () => {
    var updateContentTab = document.getElementById('update-user-form');
    var securityContentTab = document.getElementById('last-login-table');
    var removeContentTab = document.getElementById('delete-user-form');
    updateContentTab.style.display = "none";
    securityContentTab.style.display = "block";
    removeContentTab.style.display = "none";

    createBackgroundTabColor('', '#ccc', '');

    // var updateTab = document.getElementById('update-tab');
    // var securityTab = document.getElementById('security-tab');
    // var removeTab = document.getElementById('remove-tab');
    // updateTab.style.backgroundColor = '';
    // securityTab.style.backgroundColor = '#ccc';
    // removeTab.style.backgroundColor = '';
};

const changeDivToRemove = () => {
    var updateContentTab = document.getElementById('update-user-form');
    var securityContentTab = document.getElementById('last-login-table');
    var removeContentTab = document.getElementById('delete-user-form');
    updateContentTab.style.display = "none";
    securityContentTab.style.display = "none";
    removeContentTab.style.display = "block";

    createBackgroundTabColor('', '', '#ccc');

    // var updateTab = document.getElementById('update-tab');
    // var securityTab = document.getElementById('security-tab');
    // var removeTab = document.getElementById('remove-tab');
    // updateTab.style.backgroundColor = '';
    // securityTab.style.backgroundColor = '';
    // removeTab.style.backgroundColor = '#ccc';
};

