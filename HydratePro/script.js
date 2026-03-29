let totalWater = parseInt(localStorage.getItem('totalWater')) || 0;
let goal = 3500;
let baseGoal = 3000;
let currentTemp = null;
let isExtremeHeat = false;
let userName = '';
let userCity = '';

window.onload = function() {
    const setupComplete = localStorage.getItem('setupComplete');
    if (!setupComplete) {
        document.getElementById('setup-screen').classList.add('active');
    } else {
        initializeApp();
    }
};

function completeSetup() {
    const name = document.getElementById('setup-name').value.trim();
    const age = parseInt(document.getElementById('setup-age').value);
    const city = document.getElementById('setup-city').value.trim();

    if (!name || !age || !city) {
        alert('Please fill in all fields');
        return;
    }

    localStorage.setItem('userName', name);
    localStorage.setItem('userAge', age);
    localStorage.setItem('userCity', city);
    localStorage.setItem('setupComplete', 'true');

    document.getElementById('setup-screen').classList.remove('active');
    initializeApp();
}

function initializeApp() {
    userName = localStorage.getItem('userName') || '';
    userCity = localStorage.getItem('userCity') || '';
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
