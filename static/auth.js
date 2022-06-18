
const redirectToLoginPage = () => {
    if(!window.location.href.includes('/login.html')) {
        window.open('/login.html', '_self');
    }
}

const redirectToHomePage = () => window.open('/meter-readings.html', '_self')

const logout = () => {
    if(confirm('logout ?')) {
        // clear all cookies 
        document.cookie.split(";").forEach(function(c) { document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); });
        redirectToLoginPage();
    }
}

const setCurrentUser = () => {
    fetch('/api/v1/users/current-user')
        .then(resp => resp.json())
        .then(resp => {
            if(resp.user) {
                if(window.location.href.includes('/login.html')) {
                    redirectToHomePage();
                } else {
                    document.getElementById('currentUserDisplayName').textContent = resp.user.name;
                }
            } else {
                redirectToLoginPage();
            }
        })
        .catch(error => console.log(error))
}

(
    function(){
        const userIdFromCookie = document.cookie.replace('userId=', '');
        if(userIdFromCookie) {
            setCurrentUser();
        } else {
            redirectToLoginPage();
        }
    }
)()



