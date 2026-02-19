// Seeded Random Number Generator
// Using a simple LCG for reproducibility, though not identical to numpy
class Random {
    constructor(seed) {
        this.seed = seed;
    }

    // A simple LCG: X_{n+1} = (aX_n + c) % m
    // Using constants from Numerical Recipes
    random() {
        this.seed = (1664525 * this.seed + 1013904223) % 4294967296;
        return this.seed / 4294967296;
    }

    // Box-Muller transform for normal distribution
    normal() {
        let u = 0, v = 0;
        while(u === 0) u = this.random(); // Converting [0,1) to (0,1)
        while(v === 0) v = this.random();
        return Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
    }
}

// Configuration
const CONFIG = {
    days: 60,
    initialPrice: 65000,
    mu: 0.0005,
    sigma: 0.04,
    initialCash: 100000,
    seed: 123
};

// Initialize Random Generator
const rng = new Random(CONFIG.seed);

function simulateBitcoinPrices(days, initialPrice, mu, sigma) {
    const prices = [initialPrice];
    const dt = 1;

    for (let i = 0; i < days - 1; i++) {
        const prevPrice = prices[prices.length - 1];
        const drift = (mu - 0.5 * Math.pow(sigma, 2)) * dt;
        const shock = sigma * Math.sqrt(dt) * rng.normal();
        const price = prevPrice * Math.exp(drift + shock);
        prices.push(price);
    }

    // Create an array of objects for easier handling
    return prices.map((price, index) => ({
        day: index + 1,
        price: price,
        sma7: null,
        sma30: null
    }));
}

function calculateMovingAverages(data) {
    // Helper to calculate mean of an array slice
    const mean = (arr) => arr.reduce((a, b) => a + b, 0) / arr.length;

    for (let i = 0; i < data.length; i++) {
        // SMA 7
        if (i >= 6) {
            const window7 = data.slice(i - 6, i + 1).map(d => d.price);
            data[i].sma7 = mean(window7);
        }

        // SMA 30
        if (i >= 29) {
            const window30 = data.slice(i - 29, i + 1).map(d => d.price);
            data[i].sma30 = mean(window30);
        }
    }
    return data;
}

function runTradingStrategy(data, initialCash) {
    let cash = initialCash;
    let btcHoldings = 0;
    let position = "CASH"; // CASH or BTC
    const summaryData = [];

    data.forEach((row, index) => {
        const price = row.price;
        const sma7 = row.sma7;
        const sma30 = row.sma30;
        let action = "HOLD";

        // Trading Logic
        if (sma7 !== null && sma30 !== null) {
            if (sma7 > sma30 && position === "CASH") {
                // Buy Signal (Golden Cross)
                btcHoldings = cash / price;
                cash = 0;
                position = "BTC";
                action = "BUY";
            } else if (sma7 < sma30 && position === "BTC") {
                // Sell Signal (Death Cross)
                cash = btcHoldings * price;
                btcHoldings = 0;
                position = "CASH";
                action = "SELL";
            }
        }

        const currentValue = cash + (btcHoldings * price);

        // Add to summary data for rendering
        summaryData.push({
            ...row,
            action: action,
            portfolioValue: currentValue,
            holdings: btcHoldings,
            cash: cash
        });
    });

    return summaryData;
}

function renderTable(data) {
    const tableBody = document.querySelector("#results-table tbody");
    if (!tableBody) return;

    tableBody.innerHTML = ""; // Clear existing rows

    data.forEach(row => {
        const tr = document.createElement("tr");

        // Helper for formatting currency
        const fmt = (num) => num !== null ? `$${num.toFixed(2)}` : "NaN";
        const fmtNum = (num) => num !== null ? num.toFixed(4) : "0.0000";

        // Determine action class
        let actionClass = "";
        if (row.action === "BUY") actionClass = "buy-action";
        if (row.action === "SELL") actionClass = "sell-action";

        tr.innerHTML = `
            <td>${row.day}</td>
            <td>${fmt(row.price)}</td>
            <td>${fmt(row.sma7)}</td>
            <td>${fmt(row.sma30)}</td>
            <td class="${actionClass}">${row.action}</td>
            <td>${fmt(row.portfolioValue)}</td>
            <td>${fmtNum(row.holdings)}</td>
            <td>${fmt(row.cash)}</td>
        `;
        tableBody.appendChild(tr);
    });
}

function renderSummary(initialCash, finalValue) {
    const returnPct = ((finalValue - initialCash) / initialCash) * 100;
    const summaryDiv = document.getElementById("summary-content");

    if (!summaryDiv) return;

    const returnClass = returnPct >= 0 ? "positive" : "negative";

    summaryDiv.innerHTML = `
        <p><strong>Initial Portfolio Value:</strong> $${initialCash.toFixed(2)}</p>
        <p><strong>Final Portfolio Value:</strong> $${finalValue.toFixed(2)}</p>
        <p><strong>Return:</strong> <span class="${returnClass}">${returnPct.toFixed(2)}%</span></p>
    `;
}

function init() {
    console.log("Initializing Bitcoin Simulation...");

    // 1. Simulate
    let data = simulateBitcoinPrices(CONFIG.days, CONFIG.initialPrice, CONFIG.mu, CONFIG.sigma);

    // 2. Calculate MAs
    data = calculateMovingAverages(data);

    // 3. Run Strategy
    const results = runTradingStrategy(data, CONFIG.initialCash);

    // 4. Render
    renderTable(results);
    renderSummary(CONFIG.initialCash, results[results.length - 1].portfolioValue);
}

// Run when DOM is ready
if (typeof document !== 'undefined') {
    document.addEventListener("DOMContentLoaded", init);
}

// Export for Node.js testing (if running in Node)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Random,
        simulateBitcoinPrices,
        calculateMovingAverages,
        runTradingStrategy,
        CONFIG
    };
}
