const checkUpdateForm = () => {

    const updateButton = document.getElementById('updateButton');
    console.log("method checkUpdateForm start !!");
    updateButton.addEventListener('click', () => {
    	console.log("method checkUpdateForm event listener start!");
        const errorParamsValue = 'Please correct the errors in the form! \n ' +
            '- password - min. 9 characters \n ';
        const confirmPwdError = 'Password and Confirm password fields are not the same !';
        const updatePwd = document.getElementById('updatePwd').value;
        const updateConfPwd = document.getElementById('updateConfPwd').value;

        const pwdExp = new RegExp('^.{9,}$');

        if (updatePwd !== updateConfPwd) {
            alert(confirmPwdError);
            event.preventDefault();
            return false;
        }

        if (!pwdExp.test(updatePwd)) {
            alert(errorParamsValue);
            event.preventDefault();
            return false;
        }
    });
}

checkUpdateForm();