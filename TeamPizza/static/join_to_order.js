const checkCreateOrderForm = () => {

    const createOrderButton = document.getElementById('joinToOrderButton');
    console.log('createOrderButton click event start');
    createOrderButton.addEventListener('click', () => {

        console.log('createOrderButton click event start');
        const errorParamsValue = 'Please correct the errors in the form! \n ' +
            '- number of pieces must be more than 0\n ';
        const pizzaPiecesStr = document.getElementById('order-elements-id').value;
        var pizzaPieces = parseInt(pizzaPiecesStr);
        //  comparing timestamp
        if (pizzaPieces <= 0) {
            alert(errorParamsValue);
            event.preventDefault();
            return false;
        }
    });
}


checkCreateOrderForm();