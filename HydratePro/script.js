import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.0';

const supabaseUrl = 'https://lfkmjyqjsnmdjzfcpizs.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxma21qeXFqc25tZGp6ZmNwaXpzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3NzQyNDMsImV4cCI6MjA5MDM1MDI0M30.6sb3v_mOMciQbmTmHgmsjWyewng-eKxPQgiY4QchKAI';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

let totalWater = parseInt(localStorage.getItem('totalWater')) || 0;
let goal = 3500;
let baseGoal = 3000;
let currentTemp = null;
let isExtremeHeat = false;
let userName = '';
let userCity = '';
let currentUser = null;

window.onload = async function() {
    const { data: { session } } = await supabase.auth.getSession();

    if (session) {
        currentUser = session.user;
        initializeApp();
    } else {
        document.getElementById('setup-screen').classList.add('active');
    }
};

async function completeSetup() {
    const name = document.getElementById('setup-name').value.trim();
    const age = parseInt(document.getElementById('setup-age').value);
    const city = document.getElementById('setup-city').value.trim();

    if (!name || !age || !city) {
        showSetupError('Please fill in all fields');
        return;
    }

    if (age < 1 || age > 120) {
        showSetupError('Age must be between 1 and 120');
        return;
    }

    const setupSubmit = document.querySelector('.setup-submit');
    const originalText = setupSubmit.innerText;
    setupSubmit.innerText = 'Setting up...';
    setupSubmit.disabled = true;

    try {
        const uniqueEmail = `user.${Date.now()}@hydratepro.app`;
        const { data, error: signUpError } = await supabase.auth.signUp({
            email: uniqueEmail,
            password: Math.random().toString(36).slice(-12),
            options: {
                data: {
                    name: name,
                    age: age,
                    city: city
                }
            }
        });

        if (signUpError) throw signUpError;
        if (!data.user) throw new Error('Signup failed - no user returned');

        currentUser = data.user;
        localStorage.setItem('userName', name);
        localStorage.setItem('userAge', age);
        localStorage.setItem('userCity', city);

        document.getElementById('setup-screen').classList.remove('active');
        initializeApp();
    } catch (error) {
        console.error('Setup error:', error);
        const errorMessage = error.message || 'Setup failed. Please try again.';
        showSetupError(errorMessage);
        setupSubmit.innerText = originalText;
        setupSubmit.disabled = false;
    }
}

function showSetupError(message) {
    const container = document.querySelector('.setup-container');
    let errorMsg = container.querySelector('.setup-error');
    if (!errorMsg) {
        errorMsg = document.createElement('div');
        errorMsg.className = 'setup-error';
        errorMsg.style.cssText = 'color: #ff4d4d; font-size: 0.85rem; margin-bottom: 15px; padding: 10px; background: rgba(255, 77, 77, 0.1); border-radius: 8px; border: 1px solid rgba(255, 77, 77, 0.3);';
        container.insertBefore(errorMsg, container.querySelector('.setup-input'));
    }
    errorMsg.innerText = message;
}

async function signInWithGoogle() {
    try {
        const button = event?.target;
        if (button) {
            button.disabled = true;
            button.style.opacity = '0.6';
        }

        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.href
            }
        });
        if (error) throw error;
    } catch (error) {
        console.error('Google sign-in error:', error);
        showSetupError('Google sign-in failed. Please check your connection and try again.');
        if (event?.target) {
            event.target.disabled = false;
            event.target.style.opacity = '1';
        }
    }
}

async function signInWithMicrosoft() {
    try {
        const button = event?.target;
        if (button) {
            button.disabled = true;
            button.style.opacity = '0.6';
        }

        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'azure',
            options: {
                redirectTo: window.location.href
            }
        });
        if (error) throw error;
    } catch (error) {
        console.error('Microsoft sign-in error:', error);
        showSetupError('Microsoft sign-in failed. Please check your connection and try again.');
        if (event?.target) {
            event.target.disabled = false;
            event.target.style.opacity = '1';
        }
    }
}

function initializeApp() {
    userName = localStorage.getItem('userName') || currentUser?.user_metadata?.full_name || 'User';
    userCity = localStorage.getItem('userCity') || 'Unknown';
    const userAge = parseInt(localStorage.getItem('userAge')) || 18;

    baseGoal = userAge < 14 ? 2100 : 3000;
    totalWater = parseInt(localStorage.getItem('totalWater')) || 0;

    displayWelcome();
    fetchWeather(userCity);
    updateUI();
}

function displayWelcome() {
    const banner = document.getElementById('welcome-banner');
    banner.innerText = `Welcome, ${userName}`;
    banner.classList.remove('hidden');
}

async function fetchWeather(city) {
    try {
        const response = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=0&longitude=0&current=temperature_2m&timezone=auto&location=${encodeURIComponent(city)}`);
        const data = await response.json();

        if (data.results && data.results.length > 0) {
            const location = data.results[0];
            const tempResponse = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${location.latitude}&longitude=${location.longitude}&current=temperature_2m&timezone=auto`);
            const tempData = await tempResponse.json();
            currentTemp = Math.round(tempData.current.temperature_2m);
        } else {
            currentTemp = 25;
        }
    } catch (error) {
        console.error('Weather fetch failed:', error);
        currentTemp = 25;
    }

    calculateGoal(currentTemp);
    displayWeatherInfo(currentTemp);
}

function calculateGoal(temp) {
    const adjustment = Math.max(0, temp - 25) * 50;
    goal = baseGoal + adjustment;
    isExtremeHeat = temp > 32;

    const body = document.body;
    const climateAlert = document.getElementById('climate-alert');

    if (isExtremeHeat) {
        body.classList.add('extreme-heat');
        climateAlert.innerText = 'Extreme Heat Alert';
        climateAlert.classList.remove('hidden');
    } else {
        body.classList.remove('extreme-heat');
        climateAlert.classList.add('hidden');
    }

    document.getElementById('goal-display').innerText = goal;
}

function displayWeatherInfo(temp) {
    const weatherInfo = document.getElementById('weather-info');
    const locationDisplay = document.getElementById('location-display');

    weatherInfo.innerHTML = `It's ${temp}°C today. Your goal has been adjusted for optimal hydration.`;
    locationDisplay.innerHTML = `📍 ${userCity} • ${temp}°C`;
    locationDisplay.classList.remove('hidden');
}

window.addEventListener('keydown', (e) => {
    if (e.key === '1') addWater(250);
    if (e.key === '2') addWater(500);
    if (e.key === 'r' || e.key === 'R') resetWater();
});

function addWater(amount) {
    if (navigator.vibrate) navigator.vibrate(40);

    totalWater += amount;
    localStorage.setItem('totalWater', totalWater);
    updateUI();

    if (totalWater >= goal && (totalWater - amount) < goal) {
        triggerSuccess();
    }
}

function resetWater() {
    if (confirm("Reset today's progress?")) {
        if (navigator.vibrate) navigator.vibrate([50, 50, 50]);
        totalWater = 0;
        localStorage.setItem('totalWater', 0);
        updateUI();
    }
}

function updateUI() {
    const percent = Math.min(Math.floor((totalWater / goal) * 100), 100);
    const remaining = Math.max(goal - totalWater, 0);

    document.getElementById('percent-num').innerText = percent;
    document.getElementById('current-ml').innerText = totalWater;
    document.getElementById('goal-display').innerText = goal;
    document.getElementById('rem-ml').innerText = remaining + "ml";

    const offset = 565.48 - (565.48 * percent) / 100;
    document.getElementById('progress-ring').style.strokeDashoffset = offset;

    const statusText = document.getElementById('status-text');
    if (percent < 30) statusText.innerText = "Dehydrated";
    else if (percent < 70) statusText.innerText = "Getting There";
    else if (percent < 100) statusText.innerText = "Almost Hydrated";
    else statusText.innerText = "Goal Reached!";
}

function triggerSuccess() {
    const colors = isExtremeHeat
        ? ['#ff5722', '#ffffff', '#ffb88c']
        : ['#00d4ff', '#ffffff', '#00ff88'];

    confetti({
        particleCount: 150,
        spread: 70,
        origin: { y: 0.6 },
        colors: colors
    });
}
