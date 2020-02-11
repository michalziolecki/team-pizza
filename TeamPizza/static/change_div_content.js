const createBackgroundTabColor = (updateColor, securityColor, removeColor) => {
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

};

const changeDivToSecurity = () => {
    var updateContentTab = document.getElementById('update-user-form');
    var securityContentTab = document.getElementById('last-login-table');
    var removeContentTab = document.getElementById('delete-user-form');
    updateContentTab.style.display = "none";
    securityContentTab.style.display = "block";
    removeContentTab.style.display = "none";

    createBackgroundTabColor('', '#ccc', '');

};

const changeDivToRemove = () => {
    var updateContentTab = document.getElementById('update-user-form');
    var securityContentTab = document.getElementById('last-login-table');
    var removeContentTab = document.getElementById('delete-user-form');
    updateContentTab.style.display = "none";
    securityContentTab.style.display = "none";
    removeContentTab.style.display = "block";

    createBackgroundTabColor('', '', '#ccc');

};

const createBackgroundOrderTabColor = (createColorTab, ordersColorTab, closeColorTab) => {
    var createOrderTab = document.getElementById('create-order-tab');
    var chooseOrderTab = document.getElementById('join-to-order-tab');
    var closedOrderTab = document.getElementById('close-order-tab');
    createOrderTab.style.backgroundColor = createColorTab;
    chooseOrderTab.style.backgroundColor = ordersColorTab;
    closedOrderTab.style.backgroundColor = closeColorTab;
};

const changeDivToClosedOrder  = () => {
    var createOrderTab = document.getElementById('create-order-form');
    var chooseOrderTab = document.getElementById('choose-order-table');
    var closedOrderTab = document.getElementById('close-order-table');

    createOrderTab.style.display = "none";
    chooseOrderTab.style.display = "none";
    closedOrderTab.style.display = "block";

    createBackgroundOrderTabColor('', '', '#ccc');
};

const changeDivToCreateOrder = () => {
    var createOrderTab = document.getElementById('create-order-form');
    var chooseOrderTab = document.getElementById('choose-order-table');
    var closedOrderTab = document.getElementById('close-order-table');

    createOrderTab.style.display = "block";
    chooseOrderTab.style.display = "none";
    closedOrderTab.style.display = "none";

    createBackgroundOrderTabColor('#ccc', '', '');

};

const changeDivToOpenedOrders = () => {
    var createOrderTab = document.getElementById('create-order-form');
    var chooseOrderTab = document.getElementById('choose-order-table');
    var closedOrderTab = document.getElementById('close-order-table');

    createOrderTab.style.display = "none";
    chooseOrderTab.style.display = "block";
    closedOrderTab.style.display = "none";

    createBackgroundOrderTabColor('', '#ccc', '');

};