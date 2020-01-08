const checkSignForm = () => {

    const signupButton = document.getElementById('signupButton');
	console.log('signupButton click event start');
    signupButton.addEventListener('click', () => {
        console.log('signupButton click event start');
    	const errorParamsValue = 'Please correct the errors in the form! \n ' +
            '- name - min. 3 characters a-zA-Z0-9 \n ' +
            '- surname - min. 3 characters a-zA-Z0-9 \n ' +
            '- nickname - min. 5 characters a-zA-Z0-9 \n ' +
            '- mail - min. 3 characters -> include @ \n ' +
            '- password - min. 9 characters \n ';
        const confirmPwdError = 'Password and Confirm password fields are not the same !';

        const signupName = document.getElementById('signupName').value;
        const signupSurname = document.getElementById('signupSurname').value;
        const signupNickName = document.getElementById('signupNickName').value;
        const signupMail = document.getElementById('signupMail').value;
        const signupPwd = document.getElementById('signupPwd').value;
        const signupConfPwd = document.getElementById('signupConfPwd').value;

        const surnameExp = new RegExp('[a-zA-Z0-9]{3,}');
        const nicknameExp = new RegExp('[a-zA-Z0-9]{6,}');
        const emailExp = new RegExp('^\\S+@\\S+$');
        const pwdExp = new RegExp('.{9,}');

        if (signupPwd !== signupConfPwd) {
            alert(confirmPwdError);
            event.preventDefault();
            return false;
        }

        if (!(surnameExp.test(signupName)) ||
			!(surnameExp.test(signupSurname)) ||
			!(nicknameExp.test(signupNickName)) ||
			!(emailExp.test(signupMail)) ||
			!(pwdExp.test(signupPwd))) {

            alert(errorParamsValue);
            event.preventDefault();
            return false;
        }
    });
}

checkSignForm();