let isLoginMode = true;

window.onload = function() {
    if (localStorage.getItem('isLoggedIn') === 'true') {
        window.location.href = "./hub/index.html";
    }
    document.getElementById('forgot-password-link').style.display = isLoginMode ? 'block' : 'none';
};

function toggleMode() {
    isLoginMode = !isLoginMode;
    const title = document.getElementById('form-title');
    const btn = document.getElementById('main-btn');
    const toggleLink = document.getElementById('toggle-msg');
    const dobContainer = document.getElementById('dob-container');
    const forgotLink = document.getElementById('forgot-password-link');
    const errorMsg = document.getElementById('error-msg');

    errorMsg.innerText = '';

    if (isLoginMode) {
        title.innerHTML = "Welcome<span>Back</span>";
        btn.innerText = "Login";
        dobContainer.style.display = "none";
        forgotLink.style.display = "block";
        toggleLink.innerHTML = "Don't have an account? <span onclick='toggleMode()'>Create Account</span>";
    } else {
        title.innerHTML = "Create<span>Account</span>";
        btn.innerText = "Sign Up";
        dobContainer.style.display = "block";
        forgotLink.style.display = "none";
        toggleLink.innerHTML = "Already have an account? <span onclick='toggleMode()'>Login</span>";
    }
}

function handleAuth() {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    const dob = document.getElementById('dob').value;
    const remember = document.getElementById('remember').checked;
    const error = document.getElementById('error-msg');

    if (!user || !pass || (!isLoginMode && !dob)) {
        error.innerText = "Please fill in all fields";
        return;
    }

    if (isLoginMode) {
        const storedData = JSON.parse(localStorage.getItem(`user_${user}`));
        if (storedData && storedData.pass === pass) {
            if (remember) localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('currentUser', user);
            localStorage.setItem('currentDOB', storedData.dob);
            window.location.href = "./hub/index.html";
        } else {
            error.innerText = "Invalid username or password";
        }
    } else {
        if (localStorage.getItem(`user_${user}`)) {
            error.innerText = "Username already exists";
        } else {
            if (pass.length < 6) {
                error.innerText = "Password must be at least 6 characters";
                return;
            }
            const userData = { pass: pass, dob: dob };
            localStorage.setItem(`user_${user}`, JSON.stringify(userData));
            error.innerText = "";
            alert("Account created successfully! Please login.");
            toggleMode();
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
            document.getElementById('dob').value = '';
        }
    }
}

function showForgotPassword() {
    document.getElementById('forgot-modal').classList.remove('hidden');
}

function closeForgotPassword() {
    document.getElementById('forgot-modal').classList.add('hidden');
    document.getElementById('reset-username').value = '';
    document.getElementById('reset-email').value = '';
    document.getElementById('reset-msg').innerText = '';
}

function handlePasswordReset() {
    const username = document.getElementById('reset-username').value.trim();
    const email = document.getElementById('reset-email').value.trim();
    const resetMsg = document.getElementById('reset-msg');

    if (!username || !email) {
        resetMsg.innerText = "Please fill in all fields";
        return;
    }

    const storedData = JSON.parse(localStorage.getItem(`user_${username}`));

    if (!storedData) {
        resetMsg.innerText = "Username not found";
        return;
    }

    const dob = storedData.dob;
    const dobMatch = dob === email;

    if (dobMatch) {
        const tempPassword = generateTempPassword();
        storedData.pass = tempPassword;
        localStorage.setItem(`user_${username}`, JSON.stringify(storedData));

        resetMsg.style.color = '#00ff88';
        resetMsg.innerText = `Password reset successful! Temporary password: ${tempPassword} (Note: Change it after login)`;

        setTimeout(() => {
            closeForgotPassword();
            resetMsg.style.color = '#ff4d4d';
        }, 3000);
    } else {
        resetMsg.innerText = "Incorrect date of birth. Cannot reset password.";
    }
}

function generateTempPassword() {
    return 'Temp' + Math.random().toString(36).slice(-8).toUpperCase();
}