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
        if(signupFields) signupFields.style.display = "none";
        toggleLink.innerHTML = "Don't have an account? <span onclick='toggleMode()'>Create Account</span>";
    } else {
        title.innerHTML = "Create<span>Account</span>";
        btn.innerText = "Sign Up";
        nameInput.placeholder = "Full Name";
        if(signupFields) signupFields.style.display = "block";
        toggleLink.innerHTML = "Already have an account? <span onclick='toggleMode()'>Login</span>";
    }
}

function handleAuth() {
    const name = document.getElementById('fullName').value.trim();
    const pass = document.getElementById('password').value.trim();
    const error = document.getElementById('error-msg');
    
    if (!name || !pass) {
        error.innerText = "Please fill in your Name and Password";
        return;
    }

    if (isLoginMode) {
        // --- LOGIN USING NAME ---
        const storedUser = JSON.parse(localStorage.getItem(`user_${name}`));
        
        if (storedUser && storedUser.password === pass) {
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('currentName', name); // Store the name for the Hub
            localStorage.setItem('currentCity', storedUser.city);
            localStorage.setItem('currentAge', storedUser.age);
            localStorage.setItem('currentDOB', storedUser.dob);
            
            window.location.href = "./hub/index.html";
        } else {
            error.innerText = "Name not found or password incorrect";
        }
    } else {
        // --- SIGN UP USING NAME ---
        const age = document.getElementById('age').value;
        const city = document.getElementById('city').value.trim();
        const dob = document.getElementById('dob').value;

        if (!age || !city || !dob) {
            error.innerText = "Please fill in Age, City, and Birthday";
            return;
        }

        if (localStorage.getItem(`user_${name}`)) {
            error.innerText = "This Name is already registered";
        } else {
            const userData = {
                password: pass,
                city: city,
                age: age,
                dob: dob
            };
            localStorage.setItem(`user_${name}`, JSON.stringify(userData));
            alert("Account created for " + name + "! Now please login.");
            toggleMode();
        }
    }
}