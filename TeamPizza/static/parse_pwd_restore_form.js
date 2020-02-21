const checkRestoreForm = () => {
    const errorValue = 'Please correct the errors in the form! \n ' +
        '- email - remember about correct domain and format ! \n ';
    const emailRestore = document.getElementById('emailRestore').value;
    const emailRgx = new RegExp('.*@teldat.com.pl');
    if (!(emailRgx.test(emailRestore))) {
        alert(errorValue);
        event.preventDefault();
        return false;
    }
}

