const checkLoginForm = () => {
    const loginButton = document.getElementById('loginButton');
    loginButton.addEventListener('click', () => {
        const errorValue = 'Please correct the errors in the form! \n ' +
            '- login - min. 5 characters a-zA-Z0-9 \n ' + '- password - min. 9 characters \n ';
        const loginNickname = document.getElementById('loginNickname').value;
        const loginPassword = document.getElementById('loginPassword').value;
        const nicknameExp = new RegExp('[a-zA-Z0-9]{5,}');
        const pwdExp = new RegExp('.{9,}');
        if (!(nicknameExp.test(loginNickname)) || !(pwdExp.test(loginPassword))) {
            alert(errorValue);
            event.preventDefault();
            return false;
        }
    });
}

// checkLoginForm();