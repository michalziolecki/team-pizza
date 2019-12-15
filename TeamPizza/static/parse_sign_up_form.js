const checkSignForm = () => {

    var signupButton = document.getElementById('signupButton');
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

        var surnameExp = new RegExp('[a-zA-Z0-9]{3,}');
        var nicknameExp = new RegExp('[a-zA-Z0-9]{6,}');
        var emailExp = new RegExp('^\\S+@\\S+$');
        var pwdExp = new RegExp('.{9,}');

        if (signupPwd !== signupConfPwd) {
            alert(confirmPwdError);
        }

        if (!(surnameExp.test(signupName)) ||
			!(surnameExp.test(signupSurname)) ||
			!(nicknameExp.test(signupNickName)) ||
			!(emailExp.test(signupMail)) ||
			!(pwdExp.test(signupPwd))) {

            alert(errorParamsValue);
        }
    });
}

checkSignForm();