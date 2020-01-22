const checkCreateOrderForm = () => {

    const createOrderButton = document.getElementById('createOrderButton');
    console.log('createOrderButton click event start');
    createOrderButton.addEventListener('click', () => {

        console.log('createOrderButton click event start');
        const errorParamsValue = 'Please correct the errors in the form! \n ' +
            '- date and time couldn\'t be in the past \n ';
        const dateTimeField = document.getElementById('predict-order-datetime-id').value;
        const predictedTime = new Date(dateTimeField);
        console.log(predictedTime);
        var currentDate = new Date();
        //  comparing timestamp
        if (predictedTime.getTime() <= currentDate.getTime()) {
            alert(errorParamsValue);
            event.preventDefault();
            return false;
        }
    });
}


checkCreateOrderForm();