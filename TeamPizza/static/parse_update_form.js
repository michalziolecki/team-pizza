const checkUpdateForm = () => {

    var updateButton = document.getElementById('updateButton');
    updateButton.addEventListener('click', () => {
    	const errorParamsValue = 'Please correct the errors in the form! \n ' +
            '- name - min. 3 characters a-zA-Z0-9 \n ' +
            '- surname - min. 3 characters a-zA-Z0-9 \n ' +
            '- nickname - min. 5 characters a-zA-Z0-9 \n ' +
            '- mail - min. 3 characters -> include @ \n ' +
            '- password - min. 9 characters \n ';
        const confirmPwdError = 'Password and Confirm password fields are not the same !';

        // const updateName = document.getElementById('updateName').value;
        // const updateSurname = document.getElementById('updateSurname').value;
        // const updateNickName = document.getElementById('updateNickName').value;
        // const updateMail = document.getElementById('updateMail').value;
        const updatePwd = document.getElementById('updatePwd').value;
        const updateConfPwd = document.getElementById('updateConfPwd').value;

        // var surnameExp = new RegExp('[a-zA-Z0-9]{3,}|$');
        // var nicknameExp = new RegExp('[a-zA-Z0-9]{6,}|$');
        // var emailExp = new RegExp('(^\\S+@\\S+$)|$');
        var pwdExp = new RegExp('^.{9,}$');

        if (updatePwd !== updateConfPwd) {
            alert(confirmPwdError);
        }

        // !(surnameExp.test(updateName)) ||
        // 			!(surnameExp.test(updateSurname)) ||
        // 			!(nicknameExp.test(updateNickName)) ||
        // 			!(emailExp.test(updateMail)) ||
        if (!pwdExp.test(updatePwd)) {
            alert(errorParamsValue);
        }
    });
}

checkSignForm();