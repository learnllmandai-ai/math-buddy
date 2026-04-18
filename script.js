// Register service worker for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    });
}

// Chart.js glow plugin
const glowPlugin = {
    id: 'glow',
    beforeDraw: (chart) => {
        const { ctx } = chart;
        chart.data.datasets.forEach((dataset, i) => {
            if (dataset.label === 'Python' || dataset.label === 'JavaScript') {
                const meta = chart.getDatasetMeta(i);
                meta.data.forEach((element) => {
                    ctx.save();
                    ctx.shadowColor = dataset.label === 'Python' ? 'rgba(0, 255, 255, 0.8)' : 'rgba(255, 215, 0, 0.8)';
                    ctx.shadowBlur = 15;
                    ctx.strokeStyle = element.options.borderColor;
                    ctx.lineWidth = element.options.borderWidth;
                    ctx.beginPath();
                    ctx.moveTo(element.x, element.y);
                    // For line chart, need to draw the line with glow
                    // This is simplified; full glow might need more work
                    ctx.restore();
                });
            }
        });
    }
};

const ctx = document.getElementById('analyticsChart').getContext('2d');

const languages = [
    { name: 'Python', color: 'rgba(0, 255, 255, 1)', glow: true },
    { name: 'JavaScript', color: 'rgba(255, 215, 0, 1)', glow: true },
    { name: 'Java', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'Go', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'PHP', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'C', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'C#', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'C++', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'TypeScript', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'HTML/CSS', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'Kotlin', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'Scala', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'Ruby', color: 'rgba(128, 128, 128, 0.5)', glow: false },
    { name: 'Bash', color: 'rgba(128, 128, 128, 0.5)', glow: false }
];

const initialData = Array.from({ length: 50 }, () => Math.random() * 100);

const datasets = languages.map(lang => ({
    label: lang.name,
    data: [...initialData],
    borderColor: lang.color,
    backgroundColor: 'transparent',
    borderWidth: 2,
    fill: false,
    tension: 0.4, // Monotone cubic interpolation
    pointRadius: 0,
    hidden: false
}));

const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: Array.from({ length: 50 }, (_, i) => i),
        datasets: datasets
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 0 // Disable animation for real-time updates
        },
        scales: {
            x: {
                display: false
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: '#ffffff'
                }
            }
        },
        plugins: {
            legend: {
                display: false
            }
        }
    },
    plugins: [glowPlugin]
});

// Toggle visibility
languages.forEach((lang, index) => {
    const checkbox = document.getElementById(lang.name.toLowerCase().replace(/[^a-z]/g, ''));
    checkbox.addEventListener('change', () => {
        chart.data.datasets[index].hidden = !checkbox.checked;
        chart.update();
    });
});

// Simulation
let time = 50;
setInterval(() => {
    time++;
    chart.data.labels.push(time);
    chart.data.labels.shift();

    let spike = false;
    datasets.forEach(dataset => {
        const newValue = Math.random() * 100;
        dataset.data.push(newValue);
        dataset.data.shift();
        if (newValue > 90) spike = true;
    });

    chart.update();

    // Health status
    const avg = datasets.reduce((sum, ds) => sum + ds.data.reduce((a, b) => a + b, 0) / ds.data.length, 0) / datasets.length;
    const health = avg > 70 ? 'Optimal' : avg > 50 ? 'Good' : 'Warning';
    document.getElementById('health-status').textContent = health;

    // Vibration on spike
    if (spike && navigator.vibrate) {
        navigator.vibrate(200);
    }
}, 2000);

// Terminal
const messages = [
    '[INFO] Analyzing Python code efficiency...',
    '[INFO] Optimizing JavaScript bundle size...',
    '[INFO] Checking Java memory usage...',
    '[INFO] Profiling Go goroutines...',
    '[INFO] Validating PHP syntax...',
    '[INFO] Debugging C pointers...',
    '[INFO] Compiling C# assemblies...',
    '[INFO] Linking C++ objects...',
    '[INFO] Type-checking TypeScript...',
    '[INFO] Minifying HTML/CSS...',
    '[INFO] Building Kotlin APK...',
    '[INFO] Running Scala tests...',
    '[INFO] Parsing Ruby gems...',
    '[INFO] Executing Bash scripts...'
];

let messageIndex = 0;
let charIndex = 0;
const terminalOutput = document.getElementById('terminal-output');

function typeWriter() {
    if (messageIndex < messages.length) {
        const message = messages[messageIndex];
        if (charIndex < message.length) {
            terminalOutput.textContent += message.charAt(charIndex);
            charIndex++;
            setTimeout(typeWriter, 50);
        } else {
            terminalOutput.textContent += '\n';
            charIndex = 0;
            messageIndex++;
            setTimeout(typeWriter, 1000);
        }
    }
}

typeWriter();