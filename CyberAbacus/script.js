let timer = 60;
let score = 0;
let wrong = 0;
let currentAnswer = 0;
let gameActive = false;
let interval;

window.onload = () => {
    document.getElementById('high-score').innerText = localStorage.getItem('abacusHigh') || 0;
};

function startGame() {
    gameActive = true;
    timer = 60;
    score = 0;
    wrong = 0;
    document.getElementById('start-overlay').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
    document.getElementById('answer-input').focus();
    
    nextQuestion();
    
    interval = setInterval(() => {
        timer--;
        document.getElementById('timer').innerText = timer;
        if (timer <= 0) endGame();
    }, 1000);
}

function nextQuestion() {
    const container = document.getElementById('problem-list');
    container.innerHTML = '';
    let total = 0;
    let rows = 3; // Number of rows per question

    for (let i = 0; i < rows; i++) {
        let num = Math.floor(Math.random() * 90) + 10; // 2-digit number
        
        // Randomly make it negative, but keep total positive
        if (i > 0 && Math.random() > 0.5 && (total - num) > 0) {
            total -= num;
            createRow("-" + num, container);
        } else {
            total += num;
            createRow(i === 0 ? num : "+" + num, container);
        }
    }
    currentAnswer = total;
}

function createRow(text, parent) {
    const div = document.createElement('div');
    div.className = 'num-row';
    div.innerText = text;
    parent.appendChild(div);
}

document.getElementById('answer-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const userVal = parseInt(e.target.value);
        if (userVal === currentAnswer) {
            score++;
            document.getElementById('correct-count').innerText = score;
            document.body.style.backgroundColor = "#1a3a2a";
            setTimeout(() => document.body.style.backgroundColor = "#0a0b10", 200);
        } else {
            wrong++;
            document.getElementById('wrong-count').innerText = wrong;
            
            // --- NEW VIBRATION CODE ---
            if ("vibrate" in navigator) {
                // Vibrate pattern: 100ms on, 50ms off, 100ms on
                navigator.vibrate([100, 50, 100]);
            }
            
            document.getElementById('game-screen').classList.add('error-shake');
            setTimeout(() => document.getElementById('game-screen').classList.remove('error-shake'), 300);
        }
        e.target.value = '';
        nextQuestion();
    }
});

function endGame() {
    clearInterval(interval);
    gameActive = false;
    alert(`Mission Complete! \nScore: ${score} \nAccuracy: ${Math.round((score/(score+wrong))*100)}%`);
    
    const high = localStorage.getItem('abacusHigh') || 0;
    if (score > high) localStorage.setItem('abacusHigh', score);
    
    location.reload();
}