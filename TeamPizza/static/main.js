const navSlide = () => {
    const stack = document.querySelector('.stack');
    const nav = document.querySelector('.nav-links');
    const navLinks = document.querySelectorAll('.nav-links li');

    stack.addEventListener('click', () => {
        nav.classList.toggle('nav-active');
        //Animate links
        navLinks.forEach((link, index) => {
            if (link.style.animation) {
                link.style.animation = '';
            } else {
                link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7 + 0.3}s`;
                console.log(index / 7);
            }
        })

        //stack animation
        stack.classList.toggle('toggle');
    });
}

const checkLoginForm = () => {
    const loginButton = document.getElementById('loginButton');
    loginButton.addEventListener('click', () => {
    	const errorValue= 'Please correct the errors in the form! \n ' +
			'- login - min. 6 characters a-zA-Z0-9 \n ' + '- password - min. 9 characters \n ';
        const loginNickname = document.getElementById('loginNickname').value;
        const loginPassword = document.getElementById('loginPassword').value;
        var nicknameExp = new RegExp('[a-zA-Z0-9]{6,}');
        var pwdExp = new RegExp('.{9,}');
        if (!(nicknameExp.test(loginNickname)) || !(pwdExp.test(loginPassword))) {
			alert(errorValue);
        }
    });
}

const checkSignForm = () => {

}

navSlide();
checkLoginForm();
