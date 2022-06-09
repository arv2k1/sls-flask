const showAdminLogin = () => {
    document.getElementById('consumerLoginDiv').classList.add('hide');
    document.getElementById('adminLoginDiv').classList.remove('hide');
}

const showConsumerLogin = () => {
    document.getElementById('adminLoginDiv').classList.add('hide');
    document.getElementById('consumerLoginDiv').classList.remove('hide');
}

(
    () => {
        const params = new URLSearchParams(window.location.search);
        if(params.has('userType')) {
            const userType = params.get('userType');
            if(userType === 'admin') {
                showAdminLogin();
            } else {
                showConsumerLogin();
            }
        }
    }
)()

const consumerLogin = (e) => {
    const id = document.getElementById('consumerIdInput').value
    const password = document.getElementById('consumerPasswordInput').value
    const user = { id, password };

    fetch('/api/v1/login', {
        method: 'POST',
        body: JSON.stringify({user}),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(resp => resp.json())
    .then(resp => {
        if(resp.user) {
            redirectToHomePage();
        } else if(resp.status && resp.status === 'error') {
            alert(resp.message);
        } else {
            console.error(resp)
            alert('Unknown error')
        }
    })
    .catch(err => {
        console.error(err);
        alert('An error occurred')
    })
}