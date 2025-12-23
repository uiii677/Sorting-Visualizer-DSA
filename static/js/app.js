document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const barsContainer = document.getElementById("bars");
    const statusText = document.getElementById("status");
    const sizeSlider = document.getElementById("sizeSlider");
    const sizeValue = document.getElementById("sizeValue");
    const speedSlider = document.getElementById("speedSlider");
    const speedValue = document.getElementById("speedValue");
    const generateBtn = document.getElementById("generateBtn");
    const algorithmSelect = document.getElementById("algorithmSelect");
    const visualizeBtn = document.getElementById("visualizeBtn");
    const pauseBtn = document.getElementById("pauseBtn");
    const resetBtn = document.getElementById("resetBtn");
    const searchTarget = document.getElementById("searchTarget");
    const searchBtn = document.getElementById("searchBtn");

    // Stats
    const comparisonsEl = document.getElementById("comparisons");
    const swapsEl = document.getElementById("swaps");
    const accessEl = document.getElementById("access");

    // State
    let array = [];
    let sortingSteps = [];
    let isVisualizing = false;
    let isPaused = false;
    let currentStep = 0;
    let animationInterval = null;

    // --- Initialization ---
    function generateArray() {
        if (isVisualizing) return;
        const size = parseInt(sizeSlider.value);
        array = Array.from({ length: size }, () => Math.floor(Math.random() * 400) + 10);
        resetState();
        drawBars(array);
        statusText.textContent = "New array generated";
    }

    function resetState() {
        sortingSteps = [];
        isVisualizing = false;
        isPaused = false;
        currentStep = 0;
        clearInterval(animationInterval);
        visualizeBtn.disabled = false;
        pauseBtn.disabled = true;
        searchBtn.disabled = false;
        updateStats(0, 0, 0);
    }

    // --- Drawing ---
    function drawBars(arr, highlights = {}) {
        barsContainer.innerHTML = "";
        const maxValue = Math.max(...arr);
        const barWidth = barsContainer.offsetWidth / arr.length - 2;

        arr.forEach((value, index) => {
            const bar = document.createElement("div");
            bar.classList.add("bar");
            bar.style.height = `${(value / maxValue) * 100}%`;
            bar.style.width = `${barWidth}px`;
            
            // Apply highlight classes
            if (highlights.sorted?.includes(index)) bar.classList.add("sorted");
            else if (highlights.swapping?.includes(index)) bar.classList.add("swap");
            else if (highlights.comparing?.includes(index)) bar.classList.add("compare");
            else if (highlights.searching?.includes(index)) bar.classList.add("searching");
            else if (highlights.pivot === index) bar.classList.add("pivot");
            else if (highlights.found === index) bar.classList.add("found");

            barsContainer.appendChild(bar);
        });
    }

    // --- Controls ---
    sizeSlider.addEventListener('input', (e) => {
        sizeValue.textContent = e.target.value;
        generateArray();
    });

    speedSlider.addEventListener('input', (e) => {
        speedValue.textContent = `${e.target.value}ms`;
    });

    generateBtn.addEventListener('click', generateArray);
    resetBtn.addEventListener('click', () => {
        resetState();
        drawBars(array);
        statusText.textContent = "Visualization reset";
    });

    pauseBtn.addEventListener('click', () => {
        isPaused = !isPaused;
        pauseBtn.textContent = isPaused ? "Resume" : "Pause";
        if (!isPaused) runVisualization();
    });

    // --- Sorting Visualization ---
    visualizeBtn.addEventListener('click', async () => {
        if (isVisualizing) return;
        isVisualizing = true;
        visualizeBtn.disabled = true;
        pauseBtn.disabled = false;
        searchBtn.disabled = true;
        statusText.textContent = "Sorting...";

        const algorithm = algorithmSelect.value;
        const response = await fetch("/api/sort", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ array, algorithm })
        });
        const data = await response.json();
        sortingSteps = data.steps;
        currentStep = 0;
        updateStats(0,0,0);
        runVisualization();
    });

    function runVisualization() {
        if (isPaused || currentStep >= sortingSteps.length) {
            if (currentStep >= sortingSteps.length) {
                statusText.textContent = "Sorting Complete!";
                drawBars(sortingSteps[sortingSteps.length - 1].array, { sorted: Array.from({length: array.length}, (_, i) => i) });
                resetState();
            }
            return;
        }

        const step = sortingSteps[currentStep];
        drawBars(step.array, step);
        
        // Simple stats calculation (can be improved from backend)
        if (step.comparing) updateStats(parseInt(comparisonsEl.textContent) + step.comparing.length, parseInt(swapsEl.textContent), parseInt(accessEl.textContent) + step.comparing.length);
        if (step.swapping) updateStats(parseInt(comparisonsEl.textContent), parseInt(swapsEl.textContent) + step.swapping.length, parseInt(accessEl.textContent) + step.swapping.length * 2);
        
        currentStep++;
        animationInterval = setTimeout(runVisualization, parseInt(speedSlider.value));
    }
    
    function updateStats(comparisons, swaps, access) {
        comparisonsEl.textContent = comparisons;
        swapsEl.textContent = swaps;
        accessEl.textContent = access;
    }

    // --- Search Visualization ---
    searchBtn.addEventListener('click', async () => {
        if (isVisualizing) return;
        const target = parseInt(searchTarget.value);
        if (isNaN(target)) {
            statusText.textContent = "Please enter a valid target number.";
            return;
        }
        
        statusText.textContent = `Searching for ${target}...`;
        searchBtn.disabled = true;
        
        const response = await fetch("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ array, target })
        });
        
        const data = await response.json();
        const sortedArray = data.sorted_array;
        const searchSteps = data.steps;
        
        // First, draw the sorted array
        drawBars(sortedArray);
        
        // Then, run through the search steps
        let i = 0;
        const searchInterval = setInterval(() => {
            if (i >= searchSteps.length) {
                clearInterval(searchInterval);
                const lastStep = searchSteps[searchSteps.length - 1];
                if (lastStep.found) {
                    statusText.textContent = `Found ${target} at index ${lastStep.mid}!`;
                    drawBars(sortedArray, { found: lastStep.mid });
                } else {
                    statusText.textContent = `${target} not found in the array.`;
                }
                searchBtn.disabled = false;
                return;
            }
            
            const step = searchSteps[i];
            const highlights = {
                searching: [step.low, step.high],
                pivot: step.mid
            };
            drawBars(sortedArray, highlights);
            i++;
        }, parseInt(speedSlider.value) * 2); // Slower for search
    });

    // Initial load
    generateArray();
});
