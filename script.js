let isLoginMode = true;

function toggleMode() {
    isLoginMode = !isLoginMode;
    const title = document.getElementById('form-title');
    const btn = document.getElementById('main-btn');
    const toggleLink = document.getElementById('toggle-msg');
    const signupFields = document.getElementById('signup-extra-fields');
    const nameInput = document.getElementById('fullName');

    if (isLoginMode) {
        title.innerHTML = "Welcome<span>Back</span>";
        btn.innerText = "Login";
        nameInput.placeholder = "Enter your Name";
        signupFields.style.display = "none";
        toggleLink.innerHTML = "Don't have an account? <span onclick='toggleMode()'>Create Account</span>";
    } else {
        title.innerHTML = "Create<span>Account</span>";
        btn.innerText = "Sign Up";
        nameInput.placeholder = "Full Name";
        signupFields.style.display = "block";
        toggleLink.innerHTML = "Already have an account? <span onclick='toggleMode()'>Login</span>";
    }
}

function handleAuth() {
    const name = document.getElementById('fullName').value.trim();
    const pass = document.getElementById('password').value.trim();
    const error = document.getElementById('error-msg');
    
    if (!name || !pass) {
        error.innerText = "Fields cannot be empty";
        return;
    }

    if (isLoginMode) {
        const data = JSON.parse(localStorage.getItem(`user_${name}`));
        if (data && data.password === pass) {
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('currentName', name);
            localStorage.setItem('currentCity', data.city);
            localStorage.setItem('currentAge', data.age);
            localStorage.setItem('currentDOB', data.dob);
            window.location.href = "./hub/index.html";
        } else {
            error.innerText = "Invalid credentials";
        }
    } else {
        const age = document.getElementById('age').value;
        const city = document.getElementById('city').value.trim();
        const dob = document.getElementById('dob').value;
        if (!age || !city || !dob) {
            error.innerText = "Please fill all fields";
            return;
        }
        localStorage.setItem(`user_${name}`, JSON.stringify({password: pass, city, age, dob}));
        alert("Account created!");
        toggleMode();
    }
}