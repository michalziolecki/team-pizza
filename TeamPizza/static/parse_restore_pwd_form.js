const checkRestoreForm = () => {
    const regexError = 'Please correct the errors in the form! \n ' +
        '- password - min. 9 characters! \n ';
    const confirmPwdError = 'Passwords are not the same !';
    const pwd = document.getElementById('updatePwd').value;
    const pwdConf = document.getElementById('updateConfPwd').value;
    const pwdExp = new RegExp('.{9,}');

    if (pwd !== pwdConf) {
            alert(confirmPwdError);
            event.preventDefault();
            return false;
    }

    if (!(pwdExp.test(pwd))) {
        alert(regexError);
        event.preventDefault();
        return false;
    }
}

