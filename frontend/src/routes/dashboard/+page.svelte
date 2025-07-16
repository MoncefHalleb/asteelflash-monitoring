<script>
    import { onMount, onDestroy } from 'svelte';
    import { Chart, registerables } from 'chart.js';
    import { auth } from '../../stores/authStore';
    import { get_request } from '$lib/api';
    import { goto } from '$app/navigation';
    import '../../routes/dashboard/dashboard.css';
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';
    import { browser } from '$app/environment';
    import dayjs from 'dayjs'; // Optional, for better date formatting

    let allTests = []; // Initialize as an empty array

    // Reactive loading state
    let loadingBoards = false;
    let loadingMetrics = false;
    let loadingUniqueTests = false;
    $: loading = loadingBoards || loadingMetrics || loadingUniqueTests;

    // Debug loading state changes
    $: if (browser) console.log('Loading state:', { loading, loadingBoards, loadingMetrics, loadingUniqueTests });

    // Svelte state variables
    let totalQuantity = tweened(0, { duration: 1000, easing: cubicOut });
    let goodQuantity = tweened(0, { duration: 1000, easing: cubicOut });
    let badQuantity = tweened(0, { duration: 1000, easing: cubicOut });


    Chart.register(...registerables);

    let boards = [];
    let searchQuery = '';
    let searchField = 'all';
    let sortKey = 'id';
    let sortAsc = true;

    let selectedDate = '';
    let selectedStartTime = '00:00';
    let selectedEndTime = '23:59';

    let metrics = null;
    let errorMessage = '';
    let importError = '';
    let importSuccess = '';
    let importFile = null;
    let visibleBoardCount = 10;
    const initialVisibleBoardCount = 10;
    let visibleMetricCount = 10;
    const initialVisibleMetricCount = 10;

    $: if (metrics) {
        totalQuantity.set(metrics.total_quantity || 0);
        goodQuantity.set(metrics.good_quantity || 0);
        badQuantity.set(metrics.bad_quantity || 0);
    }

    $: filteredBoards = boards
        .filter(b => {
            if (!searchQuery) return true;
            const q = searchQuery.toLowerCase();
            if (searchField === 'all') {
                return (
                    (b.id + '').includes(q) ||
                    (b.ref_asteel || '').toLowerCase().includes(q) ||
                    (b.ref_client || '').toLowerCase().includes(q) ||
                    (b.family_name || '').toLowerCase().includes(q) ||
                    (b.designation || '').toLowerCase().includes(q) ||
                    (b.client || '').toLowerCase().includes(q)
                );
            } else if (searchField === 'id') {
                return (b.id + '').includes(q);
            } else if (searchField === 'ref_asteel') {
                return (b.ref_asteel || '').toLowerCase().includes(q);
            } else if (searchField === 'ref_client') {
                return (b.ref_client || '').toLowerCase().includes(q);
            } else if (searchField === 'family_name') {
                return (b.family_name || '').toLowerCase().includes(q);
            } else if (searchField === 'designation') {
                return (b.designation || '').toLowerCase().includes(q);
            } else if (searchField === 'client') {
                return (b.client || '').toLowerCase().includes(q);
            } else if (searchField === 'is_valid') {
                return ((b.is_valid ? 'valid' : 'invalid').includes(q));
            }
            return true;
        })
        .sort((a, b) => {
            let aVal = a[sortKey];
            let bVal = b[sortKey];
            if (typeof aVal === 'string') aVal = aVal.toLowerCase();
            if (typeof bVal === 'string') bVal = bVal.toLowerCase();
            if (aVal === undefined) return 1;
            if (bVal === undefined) return -1;
            if (aVal < bVal) return sortAsc ? -1 : 1;
            if (aVal > bVal) return sortAsc ? 1 : -1;
            return 0;
        });

    let quantityChart = null;
    let defectChart = null;
    let quantityCanvas;
    let defectCanvas;

    // Conditional redirect
    $: {
        if (browser && !$auth.isAuthenticated && !loading) {
            console.log('Not authenticated, redirecting...');
            goto('/login');
        }
    }

    // Lightning Animation Variables and Logic
    let stormCanvas;
    let stormCtx;
    let bolts = [];
    let particles = [];
    let timer = 0;
    let nextStrike = 0;
    let animationFrameId;

    class Particle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.vx = (Math.random() - 0.5) * 3;
            this.vy = (Math.random() - 0.5) * 3;
            this.radius = Math.random() * 1.5 + 0.5;
            this.life = Math.random() * 50 + 20;
            this.opacity = 1;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.life--;
            this.opacity = this.life / 70;
        }

        draw() {
            if (stormCtx) {
                stormCtx.beginPath();
                stormCtx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                stormCtx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
                stormCtx.fill();
            }
        }
    }

    class LightningBolt {
        constructor() {
            this.startX = Math.random() * stormCanvas.width;
            this.startY = 0;
            this.segments = [];
            this.life = Math.random() * 120 + 90;
            this.maxLife = this.life;
            this.opacity = 1;

            let currentX = this.startX;
            let currentY = this.startY;
            let segmentCount = Math.floor(Math.random() * 10 + 15);

            for (let i = 0; i < segmentCount; i++) {
                let nextX = currentX + (Math.random() - 0.5) * 40;
                let nextY = currentY + Math.random() * 20 + 10;
                this.segments.push({ x1: currentX, y1: currentY, x2: nextX, y2: nextY });

                const particleCount = Math.random() < 0.3 ? 0 : 5;
                for (let j = 0; j < particleCount; j++) {
                    particles.push(new Particle(
                        currentX + Math.random() * (nextX - currentX),
                        currentY + Math.random() * (nextY - currentY)
                    ));
                }

                currentX = nextX;
                currentY = nextY;
            }
        }

        update() {
            this.life--;
            this.opacity = Math.min(this.life / 100, (this.maxLife - this.life) / 5);
        }

        draw() {
            if (stormCtx) {
                stormCtx.save();
                stormCtx.globalAlpha = this.opacity;
                stormCtx.strokeStyle = '#fff';
                stormCtx.lineWidth = (Math.random() * 1.5 + 1) * this.opacity;
                stormCtx.shadowColor = '#d4f1ff';
                stormCtx.shadowBlur = 20;

                stormCtx.beginPath();
                for (const seg of this.segments) {
                    stormCtx.moveTo(seg.x1, seg.y1);
                    stormCtx.lineTo(seg.x2, seg.y2);
                }
                stormCtx.stroke();
                stormCtx.restore();
            }
        }
    }

    function initStormCanvas() {
        if (browser && stormCanvas) {
            stormCanvas.width = window.innerWidth;
            stormCanvas.height = window.innerHeight;
            bolts = [];
            particles = [];
            stormCanvas.style.pointerEvents = 'none';
        }
    }
    const INITIAL_DISPLAY_COUNT = 5;
    const INCREMENT_COUNT = 5;

    // State variables for "Show More/Less" functionality
    let visibleTestsCount = INITIAL_DISPLAY_COUNT;
    let visibleUniqueTestsCount = INITIAL_DISPLAY_COUNT;

    // Functions to handle "Show More" clicks
    function showMoreTests() {
        visibleTestsCount += INCREMENT_COUNT;
    }

    function showMoreUniqueTests() {
        visibleUniqueTestsCount += INCREMENT_COUNT;
    }

    // Functions to handle "Show Less" clicks
    function showLessTests() {
        visibleTestsCount = Math.max(INITIAL_DISPLAY_COUNT, visibleTestsCount - INCREMENT_COUNT);
    }

    function showLessUniqueTests() {
        visibleUniqueTestsCount = Math.max(INITIAL_DISPLAY_COUNT, visibleUniqueTestsCount - INCREMENT_COUNT);
    }


    function animateStorm() {
        if (!stormCtx) return;

        stormCtx.clearRect(0, 0, stormCanvas.width, stormCanvas.height);

        timer++;
        if (timer >= nextStrike) {
            timer = 0;
            nextStrike = Math.random() * 240 + 180;

            const strikeCount = Math.floor(Math.random() * 3) + 1;
            for (let i = 0; i < strikeCount; i++) {
                if (stormCanvas) {
                    bolts.push(new LightningBolt());
                }
            }
        }

        for (let i = bolts.length - 1; i >= 0; i--) {
            const bolt = bolts[i];
            bolt.update();
            if (bolt.life <= 0) {
                bolts.splice(i, 1);
            } else {
                bolt.draw();
            }
        }

        for (let i = particles.length - 1; i >= 0; i--) {
            const p = particles[i];
            p.update();
            if (p.life <= 0) {
                particles.splice(i, 1);
            } else {
                p.draw();
            }
        }

        animationFrameId = requestAnimationFrame(animateStorm);
    }

    // Helper function to enforce minimum loading time
    async function withMinimumLoading(stateVar, operation) {
        if (!browser) return;
        console.log(`Starting ${stateVar}...`);
        try {
            // Set loading state
            if (stateVar === 'loadingBoards') loadingBoards = true;
            else if (stateVar === 'loadingMetrics') loadingMetrics = true;
            else if (stateVar === 'loadingUniqueTests') loadingUniqueTests = true;

            const loadingTimer = new Promise(resolve => setTimeout(resolve, 2000)); // Reduced to 2s
            const result = await Promise.all([
                operation().catch(err => {
                    console.error(`Error in ${stateVar} operation:`, err);
                    throw err;
                }),
                loadingTimer
            ]);
            return result[0];
        } catch (err) {
            console.error(`Error in ${stateVar}:`, err);
            throw err;
        } finally {
            // Reset loading state
            if (stateVar === 'loadingBoards') loadingBoards = false;
            else if (stateVar === 'loadingMetrics') loadingMetrics = false;
            else if (stateVar === 'loadingUniqueTests') loadingUniqueTests = false;
            console.log(`Finished ${stateVar}, loading:`, loading);
        }
    }

    onMount(async () => {
        if (browser && document.getElementById('storm-canvas')) {
            stormCanvas = document.getElementById('storm-canvas');
            stormCtx = stormCanvas.getContext('2d');
            initStormCanvas();
            animateStorm();
            window.addEventListener('resize', initStormCanvas);
        } else {
            console.warn('Storm canvas not found or not in browser environment.');
        }

        if (!$auth.isAuthenticated) {
            loadingBoards = false;
            return;
        }

        await withMinimumLoading('loadingBoards', async () => {
            console.log('Fetching boards from /api/boards');
            const res = await get_request('/api/boards');
            console.log('Boards response:', res);
            boards = res;
        }).catch(err => {
            errorMessage = 'Failed to load boards: ' + err.message;
            console.error('onMount error:', err);
        });

        // This call will only happen if selectedDate, startTime, and endTime are already set on mount.
        // Otherwise, fetchMetrics will be called when the user applies filters.
        if (selectedDate && selectedStartTime && selectedEndTime) {
            await fetchMetrics();
        }
    });

    async function fetchMetrics() {
        if (!selectedDate || !selectedStartTime || !selectedEndTime) {
            errorMessage = 'Please select a date, start time, and end time.';
            metrics = null;
            allTests = []; // Clear allTests if input is incomplete
            destroyCharts(); // Note: This clears charts on incomplete input. Consider if this is desired.
            return;
        }
        if (!$auth.isAuthenticated) {
            errorMessage = 'You must be logged in.';
            metrics = null;
            allTests = []; // Clear allTests if not authenticated
            destroyCharts(); // Note: This clears charts on incomplete input. Consider if this is desired.
            return;
        }

        await withMinimumLoading('loadingMetrics', async () => {
            try {
                const dateEncoded = encodeURIComponent(selectedDate);
                const startTimeEncoded = encodeURIComponent(selectedStartTime);
                const endTimeEncoded = encodeURIComponent(selectedEndTime);

                const res = await get_request(`/api/quality-metrics?selected_date=${dateEncoded}&start_time=${startTimeEncoded}&end_time=${endTimeEncoded}`);
                metrics = res;
                metrics.total_quantity = metrics.total_quantity || 0;
                metrics.good_quantity = metrics.good_quantity || 0;
                metrics.bad_quantity = metrics.bad_quantity || 0;

                // Populate allTests with the ref_stats array from the metrics response
                allTests = metrics.test_details || [];
                // If you prefer ref_price_stats, use:
                // allTests = metrics.ref_price_stats || [];

                errorMessage = ''; // Clear any previous errors
                console.log('allTests populated with ref_stats (from quality-metrics):', allTests); // For debugging
            } catch (err) {
                errorMessage = 'Failed to load metrics: ' + err.message;
                metrics = null;
                allTests = []; // Clear allTests on error
                console.error('Error fetching quality metrics:', err);
            }
        });
    }

    function updateQuantityChart(good, bad) {
        if (!browser || !quantityCanvas) return;

        if (quantityChart) {
            quantityChart.data.datasets[0].data = [good, bad];
            quantityChart.update();
        } else {
            quantityChart = new Chart(quantityCanvas, {
                type: 'bar',
                data: {
                    labels: ['Good', 'Bad'],
                    datasets: [{
                        data: [good, bad],
                        backgroundColor: ['rgba(80, 250, 123, 0.7)', 'rgba(255, 85, 85, 0.7)'],
                        borderColor: ['var(--accent)', 'var(--danger)'],
                        borderWidth: 1,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    animation: { duration: 1000, easing: 'easeOutQuart' },
                    scales: {
                        x: { ticks: { color: 'var(--text-light)' }, grid: { color: 'rgba(255,255,255,0.05)' }},
                        y: { beginAtZero: true, ticks: { color: 'var(--text-light)' }, grid: { color: 'rgba(255,255,255,0.05)' }}
                    },
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: 'Good vs Bad Quantity', color: 'var(--text-light)', font: { size: 18 } }
                    }
                }
            });
        }
    }

    function updateDefectChart(defectDetails) {
        if (!browser || !defectCanvas) return;

        const labels = Object.keys(defectDetails);
        const data = Object.values(defectDetails);
        const total = data.reduce((sum, count) => sum + count, 0);
        if (defectChart) {
            defectChart.data.labels = labels;
            defectChart.data.datasets[0].data = data;
            defectChart.update();
        } else {
            defectChart = new Chart(defectCanvas, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: ['rgba(139,233,253,0.7)', 'rgba(80,250,123,0.7)', 'rgba(255,121,198,0.7)', 'rgba(241,250,140,0.7)', 'rgba(98,218,255,0.7)', 'rgba(189,147,249,0.7)'],
                        borderColor: ['var(--primary)', 'var(--accent)', '#ff79c6', 'var(--warn)', '#62daff', '#bd93f9'],
                        borderWidth: 1,
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    animation: { animateRotate: true, animateScale: true, duration: 1000 },
                    plugins: {
                        legend: { position: 'right', labels: { color: 'var(--text-light)' }},
                        title: { display: true, text: 'Defect Breakdown', color: 'var(--text-light)', font: { size: 18 }},
                        tooltip: {
                            callbacks: {
                                label: ctx => {
                                    const percent = total > 0 ? ((ctx.parsed / total) * 100).toFixed(2) + '%' : '0%';
                                    return `${ctx.label}: ${ctx.parsed} (${percent})`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    function showMoreBoards() {
        visibleBoardCount = Math.min(visibleBoardCount + 10, boards.length);
    }

    function showLessBoards() {
        visibleBoardCount = Math.max(visibleBoardCount - 10, initialVisibleBoardCount);
    }
    function showMoreMetrics() {
        visibleMetricCount = Math.min(visibleMetricCount + 10, metrics.length);
    }

    function showLessMetrics() {
        visibleMetricCount = Math.max(visibleMetricCount - 10, initialVisibleMetricCount);
    }

    onDestroy(() => {
        destroyCharts();
        if (browser) {
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
            window.removeEventListener('resize', initStormCanvas);
        }
    });

    function destroyCharts() {
        if (quantityChart) { quantityChart.destroy(); quantityChart = null; }
        if (defectChart) { defectChart.destroy(); defectChart = null; }
    }

    // Mapping for metric column names to ensure correct casing for the backend
    const metricColumnBackendMapping = {
        'typetest': 'TypeTest',
        'result': 'Result',
        'id_machine': 'Id_Machine',
        'idmachine': 'Id_Machine',
        'id_operateur': 'Id_Operateur',
        'idoperateur': 'Id_Operateur',
        'id_board': 'Id_Board', // This is the key correction for 'id_board'
        'idboard': 'Id_Board',
        'num_serie': 'Num_Serie',
        'numserie': 'Num_Serie',
        'ref_asteel': 'Ref_Asteel',
        'refasteel': 'Ref_Asteel',
        // Add exact matches to be safe, though the function handles it
        'TypeTest': 'TypeTest',
        'Result': 'Result',
        'Id_Machine': 'Id_Machine',
        'Id_Operateur': 'Id_Operateur',
        'Id_Board': 'Id_Board',
        'Num_Serie': 'Num_Serie',
        'Ref_Asteel': 'Ref_Asteel',
    };

    // Helper function to get the correctly cased metric column name
    function getBackendMetricColumnName(inputKey) {
        // First, check for an exact match (case-sensitive)
        if (metricColumnBackendMapping[inputKey]) {
            return metricColumnBackendMapping[inputKey];
        }
        // If not found, check for a lowercase match to handle variations
        const lowerInputKey = inputKey.toLowerCase();
        for (const mapKey in metricColumnBackendMapping) {
            if (mapKey.toLowerCase() === lowerInputKey) {
                return metricColumnBackendMapping[mapKey];
            }
        }
        // Fallback: If no mapping found, return the original key and log a warning
        console.warn(`No specific backend mapping found for '${inputKey}'. Using original key. Please check casing or add to mapping.`);
        return inputKey;
    }

    let selectedMetricColumn = '';
    let metricValue = ''; // Correctly defined and used now
    let uniqueTests = [];
    let uniqueTestsError = '';

    function handleCellClick(columnKey, cellValue) {
        selectedMetricColumn = getBackendMetricColumnName(columnKey); // APPLY THE CORRECTION HERE
        metricValue = cellValue; // Correctly assigns to 'metricValue'
        fetchUniqueTestsByMetric();
    }

    let startDate = '';
    let endDate = '';

    // You may default to today for testing
    startDate = dayjs().startOf('day').format('YYYY-MM-DD HH:mm:ss');
    endDate = dayjs().endOf('day').format('YYYY-MM-DD HH:mm:ss');

    // Renamed for clarity and consistency with handleCellClick
    async function fetchUniqueTestsByMetric() {
        if (!selectedMetricColumn || !metricValue || !selectedDate || !selectedStartTime || !selectedEndTime) {
            errorMessage = 'Please select all criteria for unique tests.';
            uniqueTests = []; // Still clear uniqueTests
            return;
        }
        if (!$auth.isAuthenticated) {
            errorMessage = 'You must be logged in to fetch unique tests.';
            uniqueTests = []; // Still clear uniqueTests
            return;
        }

        await withMinimumLoading('loadingUniqueTests', async () => {
            try {
                const startDateTime = dayjs(selectedDate + ' ' + selectedStartTime).format('YYYY-MM-DD HH:mm:ss');
                const endDateTime = dayjs(selectedDate + ' ' + selectedEndTime).format('YYYY-MM-DD HH:mm:ss');

                const res = await get_request(`/api/unique-tests-by-metric?metric_column=${encodeURIComponent(selectedMetricColumn)}&metric_value=${encodeURIComponent(metricValue)}&start_date=${encodeURIComponent(startDateTime)}`
                                         + `&end_date=${encodeURIComponent(endDateTime)}`);
                uniqueTests = res; // uniqueTests variable will hold this data
                errorMessage = '';
                console.log('Fetched unique tests (for uniqueTests variable):', uniqueTests); // Add console log for debugging
            } catch (err) {
                errorMessage = 'Failed to load unique tests: ' + err.message;
                uniqueTests = []; // Clear uniqueTests on error
                console.error('Error fetching unique tests:', err);
            }
        });
    }

    function handleAddNewBoard() {
        console.log("Admin: Initiating Add New Board...");
        goto('/boards/new');
    }

    function handleModifyBoard(boardId) {
        console.log("Admin: Initiating Modify Board for ID:", boardId);
        goto(`/boards/edit/${boardId}`);
    }

    async function exportCSV() {
        if (!$auth.isAuthenticated || !$auth.accessToken) {
            errorMessage = 'You must be logged in to export or your session may have expired.';
            console.log('Token missing or not authenticated:', $auth);
            return;
        }

        await withMinimumLoading('loadingBoards', async () => {
            try {
                const res = await fetch('/api/boards/export/csv', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${$auth.accessToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'boards_export.csv';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            } catch (err) {
                errorMessage = 'Export failed: ' + err.message;
                console.error('Export CSV error:', err);
            }
        });
    }

    async function exportExcel() {
        if (!$auth.isAuthenticated || !$auth.accessToken) {
            errorMessage = 'You must be logged in to export or your session may have expired.';
            console.log('Token missing or not authenticated:', $auth);
            return;
        }

        await withMinimumLoading('loadingBoards', async () => {
            try {
                const res = await fetch('/api/boards/export/xlsx', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${$auth.accessToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'boards_export.xlsx';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            } catch (err) {
                errorMessage = 'Excel export failed: ' + err.message;
                console.error('Export Excel error:', err);
            }
        });
    }

    function onFileSelected(event) {
        importFile = event.target.files[0];
        importError = '';
        importSuccess = '';
    }

    async function handleImportCSV() {
        if (!$auth.isAuthenticated || !$auth.accessToken) {
            importError = 'You must be logged in to import data or your session may have expired.';
            console.log('Token missing or not authenticated:', $auth);
            return;
        }
        if (!importFile) {
            importError = 'Please select a CSV file to import.';
            return;
        }
        importError = '';
        importSuccess = '';
        errorMessage = '';

        await withMinimumLoading('loadingBoards', async () => {
            try {
                const formData = new FormData();
                formData.append('file', importFile);
                const res = await fetch('/api/boards/import/csv', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${$auth.accessToken}`
                    },
                    body: formData
                });
                if (!res.ok) {
                    const errorData = await res.text();
                    throw new Error(errorData || `Import failed with status ${res.status}`);
                }
                const data = await res.json();
                importSuccess = data.message || 'Import successful.';
                const refreshed = await get_request('/api/boards');
                boards = refreshed;
                importFile = null;
                if (browser) {
                    const fileInput = document.getElementById('import-csv-file');
                    if (fileInput) fileInput.value = '';
                }
            } catch (err) {
                importError = 'Import failed: ' + err.message;
                console.error('Import CSV error:', err);
            }
        });
    }
    
  let forecastData = [];
  let loadingForecast = false;
let visibleForecastCount = 5; // Initial number of rows to display
  const INITIAL_DISPLAY_COUNT1 = 5;
  const INCREMENT_COUNT1 = 5;

  // Fetch forecast when the button is clicked
  async function fetchForecast(periods = 30) {
    loadingForecast = true;
    errorMessage = '';  // Reset any previous errors
    try {
      const res = await get_request(`/api/defect-forecast?periods=${periods}`);
      forecastData = res;  // Store the forecast data in `forecastData`
      loadingForecast = false;
    } catch (err) {
      errorMessage = 'Failed to load forecast: ' + err.message;
      loadingForecast = false;
    }
  }

  // Show more rows
  function showMoreForecast() {
    visibleForecastCount += INCREMENT_COUNT1;
  }

  // Show less rows
  function showLessForecast() {
    visibleForecastCount = Math.max(INITIAL_DISPLAY_COUNT1, visibleForecastCount - INCREMENT_COUNT1);
  }

  // Trigger forecast fetch on mount or user action
  onMount(() => {
    fetchForecast(); // Default to fetch 30-day forecast when the component is mounted
  });


</script>

{#if loading}
    <div class="microchip-container">
        <!-- Fallback text for debugging -->
        <svg class="microchip" viewBox="0 0 128 128" width="128px" height="128px" role="img" aria-label="Loading...">
            <symbol id="dot-1">
                <circle r="3" cx="3" cy="38" />
            </symbol>
            <symbol id="dot-2">
                <circle r="3" cx="3" cy="54" />
            </symbol>
            <symbol id="dot-3">
                <circle r="3" cx="3" cy="70" />
            </symbol>
            <symbol id="dot-4">
                <circle r="3" cx="3" cy="3" />
            </symbol>
            <symbol id="dot-5">
                <circle r="3" cx="20" cy="3" />
            </symbol>
            <symbol id="dot-6">
                <circle r="3" cx="3" cy="30" />
            </symbol>
            <symbol id="dot-7">
                <circle r="3" cx="37" cy="3" />
            </symbol>
            <symbol id="dot-8">
                <circle r="3" cx="54" cy="3" />
            </symbol>
            <symbol id="dot-9">
                <circle r="3" cx="71" cy="3" />
            </symbol>
            <symbol id="line-1">
                <polyline points="12 54,12 46,3 46,3 38" stroke-dasharray="42 42" />
            </symbol>
            <symbol id="line-2">
                <polyline points="29 54,3 54" stroke-dasharray="42 42" />
            </symbol>
            <symbol id="line-3">
                <polyline points="12 54,12 62,3 62,3 70" stroke-dasharray="42 42" />
            </symbol>
            <symbol id="line-4">
                <polyline points="28 20,28 12,20 12,20 3" stroke-dasharray="60 60" />
            </symbol>
            <symbol id="line-5">
                <polyline points="37 29,37 20,3 20,3 3" stroke-dasharray="60 60" />
            </symbol>
            <symbol id="line-6">
                <polyline points="15 20,15 30,3 30" stroke-dasharray="60 60" />
            </symbol>
            <symbol id="line-7">
                <polyline points="54 12,37 12,37 3" stroke-dasharray="43 43" />
            </symbol>
            <symbol id="line-8">
                <polyline points="54 29,54 3" stroke-dasharray="43 43" />
            </symbol>
            <symbol id="line-9">
                <polyline points="54 12,71 12,71 3" stroke-dasharray="43 43" />
            </symbol>
            <symbol id="spark-1">
                <polyline points="12 54,12 46,3 46,3 38" stroke-dasharray="15 69" />
            </symbol>
            <symbol id="spark-2">
                <polyline points="29 54,3 54" stroke-dasharray="15 69" />
            </symbol>
            <symbol id="spark-3">
                <polyline points="12 54,12 62,3 62,3 70" stroke-dasharray="15 69" />
            </symbol>
            <symbol id="spark-4">
                <polyline points="28 20,28 12,20 12,20 3" stroke-dasharray="15 105" />
            </symbol>
            <symbol id="spark-5">
                <polyline points="37 29,37 20,3 20,3 3" stroke-dasharray="15 105" />
            </symbol>
            <symbol id="spark-6">
                <polyline points="15 20,15 30,3 30" stroke-dasharray="15 105" />
            </symbol>
            <symbol id="spark-7">
                <polyline points="54 12,37 12,37 3" stroke-dasharray="15 71" />
            </symbol>
            <symbol id="spark-8">
                <polyline points="54 29,54 3" stroke-dasharray="15 71" />
            </symbol>
            <symbol id="spark-9">
                <polyline points="54 12,71 12,71 3" stroke-dasharray="15 71" />
            </symbol>
            <symbol id="wave">
                <rect x="3" y="3" rx="2.5" ry="2.5" width="44" height="44" />
            </symbol>
            <g transform="translate(10,10)">
                <g class="microchip__lines" stroke-linecap="round" stroke-linejoin="round">
                    <g>
                        <g fill="none" stroke="currentcolor">
                            <use class="microchip__line microchip__line--1" href="#line-1" />
                            <use class="microchip__spark microchip__spark--1" href="#spark-1" />
                            <use class="microchip__line microchip__line--2" href="#line-2" />
                            <use class="microchip__spark microchip__spark--2" href="#spark-2" />
                            <use class="microchip__line microchip__line--3" href="#line-3" />
                            <use class="microchip__spark microchip__spark--3" href="#spark-3" />
                        </g>
                        <g fill="currentcolor">
                            <use class="microchip__dot microchip__dot--1" href="#dot-1" />
                            <use class="microchip__dot microchip__dot--2" href="#dot-2" />
                            <use class="microchip__dot microchip__dot--3" href="#dot-3" />
                        </g>
                    </g>
                    <g>
                        <g fill="none" stroke="currentcolor">
                            <use class="microchip__line microchip__line--4" href="#line-4" />
                            <use class="microchip__spark microchip__spark--4" href="#spark-4" />
                            <use class="microchip__line microchip__line--5" href="#line-5" />
                            <use class="microchip__spark microchip__spark--5" href="#spark-5" />
                            <use class="microchip__line microchip__line--6" href="#line-6" />
                            <use class="microchip__spark microchip__spark--6" href="#spark-6" />
                        </g>
                        <g fill="currentcolor">
                            <use class="microchip__dot microchip__dot--4" href="#dot-4" />
                            <use class="microchip__dot microchip__dot--5" href="#dot-5" />
                            <use class="microchip__dot microchip__dot--6" href="#dot-6" />
                        </g>
                    </g>
                    <g>
                        <g fill="none" stroke="currentcolor">
                            <use class="microchip__line microchip__line--7" href="#line-7" />
                            <use class="microchip__spark microchip__spark--7" href="#spark-7" />
                            <use class="microchip__line microchip__line--8" href="#line-8" />
                            <use class="microchip__spark microchip__spark--8" href="#spark-8" />
                            <use class="microchip__line microchip__line--9" href="#line-9" />
                            <use class="microchip__spark microchip__spark--9" href="#spark-9" />
                        </g>
                        <g fill="currentcolor">
                            <use class="microchip__dot microchip__dot--7" href="#dot-7" />
                            <use class="microchip__dot microchip__dot--8" href="#dot-8" />
                            <use class="microchip__dot microchip__dot--9" href="#dot-9" />
                        </g>
                    </g>
                    <g transform="translate(108,0) scale(-1,1)">
                        <g fill="none" stroke="currentcolor">
                            <use class="microchip__line microchip__line--4" href="#line-4" />
                            <use class="microchip__spark microchip__spark--4" href="#spark-4" />
                            <use class="microchip__line microchip__line--5" href="#line-5" />
                            <use class="microchip__spark microchip__spark--5" href="#spark-5" />
                            <use class="microchip__line microchip__line--6" href="#line-6" />
                            <use class="microchip__spark microchip__spark--6" href="#spark-6" />
                        </g>
                        <g fill="currentcolor">
                            <use class="microchip__dot microchip__dot--4" href="#dot-4" />
                            <use class="microchip__dot microchip__dot--5" href="#dot-5" />
                            <use class="microchip__dot microchip__dot--6" href="#dot-6" />
                        </g>
                    </g>
                    <g transform="translate(108,0) scale(-1,1)">
                        <g fill="none" stroke="currentcolor">
                            <use class="microchip__line microchip__line--1" href="#line-1" />
                            <use class="microchip__spark microchip__spark--1" href="#spark-1" />
                            <use class="microchip__line microchip__line--2" href="#line-2" />
                            <use class="microchip__spark microchip__spark--2" href="#spark-2" />
                            <use class="microchip__line microchip__line--3" href="#line-3" />
                            <use class="microchip__spark microchip__spark--3" href="#spark-3" />
                        </g>
                        <g fill="currentcolor">
                            <use class="microchip__dot microchip__dot--1" href="#dot-1" />
                            <use class="microchip__dot microchip__dot--2" href="#dot-2" />
                            <use class="microchip__dot microchip__dot--3" href="#dot-3" />
                        </g>
                    </g>
                    <g transform="translate(0,108) scale(1,-1)">
                        <g fill="none" stroke="currentcolor">
                            <use class="microchip__line microchip__line--7" href="#line-7" />
                            <use class="microchip__spark microchip__spark--7" href="#spark-7" />
                            <use class="microchip__line microchip__line--8" href="#line-8" />
                            <use class="microchip__spark microchip__spark--8" href="#spark-8" />
                            <use class="microchip__line microchip__line--9" href="#line-9" />
                            <use class="microchip__spark microchip__spark--9" href="#spark-9" />
                        </g>
                        <g fill="currentcolor">
                            <use class="microchip__dot microchip__dot--7" href="#dot-7" />
                            <use class="microchip__dot microchip__dot--8" href="#dot-8" />
                            <use class="microchip__dot microchip__dot--9" href="#dot-9" />
                        </g>
                    </g>
                    <g transform="translate(0,108) scale(1,-1)">
                        <g fill="none" stroke="currentcolor">
                            <use class="microchip__line microchip__line--4" href="#line-4" />
                            <use class="microchip__spark microchip__spark--4" href="#spark-4" />
                            <use class="microchip__line microchip__line--5" href="#line-5" />
                            <use class="microchip__spark microchip__spark--5" href="#spark-5" />
                            <use class="microchip__line microchip__line--6" href="#line-6" />
                            <use class="microchip__spark microchip__spark--6" href="#spark-6" />
                        </g>
                        <g fill="currentcolor">
                            <use class="microchip__dot microchip__dot--4" href="#dot-4" />
                            <use class="microchip__dot microchip__dot--5" href="#dot-5" />
                            <use class="microchip__dot microchip__dot--6" href="#dot-6" />
                        </g>
                    </g>
                </g>
                <g transform="translate(29,29)">
                    <g class="microchip__center">
                        <g fill="none" stroke="currentcolor" stroke-width="6">
                            <use class="microchip__wave microchip__wave--1" href="#wave" />
                            <use class="microchip__wave microchip__wave--2" href="#wave" />
                        </g>
                        <rect class="microchip__core" fill="currentcolor" rx="5" ry="5" width="50" height="50" />
                    </g>
                </g>
            </g>
        </svg>
    </div>
{/if}

<canvas id="storm-canvas"></canvas>
<main class="p-8">
    <div class="header-content">
        <img src="/images.png" alt="AsteelFlash Logo" class="logo"/>
        <h1 class="font-bold header-title">
            <div class="flow-text">
                <div class="asteel-flash-brand">
                    <div class="brand-container">
                        <span class="red-text brand-part">Asteel</span>
                        <span class="blue-text font-extrabold brand-part">Flash</span>
                    </div>
                    <span class="water-flow-text brand-tagline"> Tests & Development </span>
                </div>
            </div>
        </h1>
    </div>
 <button class="btn-primary-gradient" on:click={() => fetchForecast(30)}>
    <i class="ri-bar-chart-line"></i> Get 30-Day Forecast
  </button>

  {#if loadingForecast}
    <div class="loading-spinner">
      Loading forecast...
    </div>
  {/if}

  {#if errorMessage}
    <p class="text-red-500">{errorMessage}</p>
  {/if}

  {#if forecastData.length > 0}
    <section class="forecast-results">
      <h3>Defect Rate Forecast</h3>
      <table class="forecast-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Forecast (yhat)</th>
            <th>Lower Bound (yhat_lower)</th>
            <th>Upper Bound (yhat_upper)</th>
          </tr>
        </thead>
        <tbody>
          {#each forecastData.slice(0, visibleForecastCount) as { ds, yhat, yhat_lower, yhat_upper }}
            <tr>
              <td>{dayjs(ds).format('YYYY-MM-DD')}</td>
              <td>{yhat.toFixed(2)}</td>
              <td>{yhat_lower.toFixed(2)}</td>
              <td>{yhat_upper.toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </section>

    <!-- Show More / Show Less buttons -->
    <div class="text-center mt-4 space-x-4">
      {#if visibleForecastCount > INITIAL_DISPLAY_COUNT1}
        <button class="btn btn-secondary px-6 py-2 rounded-lg" on:click={showLessForecast}>
          Show Less
        </button>
      {/if}
      {#if forecastData.length > visibleForecastCount}
        <button class="btn btn-secondary px-6 py-2 rounded-lg" on:click={showMoreForecast}>
          Show More ({forecastData.length - visibleForecastCount} remaining)
        </button>
      {/if}
    </div>
  {/if}

    <section class="mb-12">
        <div class="section-header flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
                <span class="icon ri-clipboard-line text-3xl text-primary"></span>
                <h2 class="text-2xl font-bold text-text-light tracking-tight">Boards Information</h2>
            </div>
            <div class="tag-info bg-white-700 text-white rounded-full px-4 py-1 text-lg font-semibold shadow-md">
                <i class="ri-database-2-line mr-1"></i>
                {boards.length} Boards
            </div>
        </div>

        <div class="relative mb-8">
            <div class="table-search-actions absolute top-0 right-0 flex items-center gap-3 flex-wrap justify-end md:justify-start w-full md:w-auto">
                <label class="font-medium text-primary flex items-center gap-1" for="board-search-field">
                    <i class="ri-filter-3-line text-white"></i> Search by:
                </label>
                <select
                    id="board-search-field"
                    bind:value={searchField}
                    class="form-select"
                >
                    <option value="all">All Fields</option>
                    <option value="id">ID</option>
                    <option value="ref_asteel">REF Asteel</option>
                    <option value="family_name">Family</option>
                    <option value="is_valid">Validity</option>
                </select>
                <div class="search-input-container">
                    <input
                        type="text"
                        placeholder="Search boards..."
                        bind:value={searchQuery}
                        class="form-input"
                    />
                    <span class="search-icon">
                        <i class="ri-search-line"></i>
                    </span>
                </div>
            </div>

            {#if $auth.userRole === 'admin'}
            <div class="admin-actions mt-16 md:mt-0">
                <button class="btn-action btn-add" on:click={handleAddNewBoard}>
                    <i class="ri-add-circle-fill"></i> Add New Board
                </button>
            </div>
            {/if}
        </div>

        <div class="import-export-controls flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div class="flex gap-2 items-center flex-wrap">
                <button
                    class="btn-primary-gradient"
                    on:click={exportCSV}
                    title="Export Boards to CSV"
                >
                    <i class="ri-file-download-line"></i> Export CSV
                </button>
                <button
                    class="btn-primary-gradient"
                    on:click={exportExcel}
                    title="Export Boards to Excel"
                >
                    <i class="ri-file-download-line"></i> Export Excel
                </button>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
                <label for="import-csv-file" class="btn-primary-gradient cursor-pointer flex items-center gap-1" title="Import Boards from CSV">
                    <i class="ri-upload-cloud-line"></i> Import CSV
                    <input
                        type="file"
                        accept=".csv"
                        id="import-csv-file"
                        on:change={onFileSelected}
                        class="hidden"
                    />
                </label>
                <button
                    class="btn-primary-gradient"
                    on:click={handleImportCSV}
                    disabled={!importFile}
                    title="Import Boards from CSV"
                >
                    <i class="ri-upload-cloud-line"></i> Process Import
                </button>
            </div>
        </div>

        {#if importError}
            <p class="text-red-500 mt-2">{importError}</p>
        {/if}
        {#if importSuccess}
            <p class="text-green-500 mt-2">{importSuccess}</p>
        {/if}

        {#if errorMessage.includes('Failed to load boards')}
            <p class="text-red-500 mt-4">{errorMessage}</p>
        {/if}
        {#if loadingBoards}
            <p class="debug">Debug: Loading boards...</p>
        {/if}

        {#if !$auth.isAuthenticated && !loadingBoards}
            <p class="text-text-dark-contrast text-center mt-4">Please log in to view board information.</p>
        {:else}
            <div class="card overflow-x-auto">
                <table class="min-w-full table-auto">
                    <thead>
                        <tr>
                            <th class="py-3 px-5 cursor-pointer text-left" on:click={() => { sortKey = 'id'; sortAsc = sortKey === 'id' ? !sortAsc : true; }}>
                                ID <span class="sort-indicator">{sortKey === 'id' ? (sortAsc ? '↑' : '↓') : ''}</span>
                            </th>
                            <th class="py-3 px-5 cursor-pointer text-left" on:click={() => { sortKey = 'ref_asteel'; sortAsc = sortKey === 'ref_asteel' ? !sortAsc : true; }}>
                                REF Asteel <span class="sort-indicator">{sortKey === 'ref_asteel' ? (sortAsc ? '↑' : '↓') : ''}</span>
                            </th>
                            <th class="py-3 px-5 cursor-pointer text-left" on:click={() => { sortKey = 'family_name'; sortAsc = sortKey === 'family_name' ? !sortAsc : true; }}>
                                Family <span class="sort-indicator">{sortKey === 'family_name' ? (sortAsc ? '↑' : '↓') : ''}</span>
                            </th>
                            <th class="py-3 px-5 cursor-pointer text-left" on:click={() => { sortKey = 'is_valid'; sortAsc = sortKey === 'is_valid' ? !sortAsc : true; }}>
                                Validity <span class="sort-indicator">{sortKey === 'is_valid' ? (sortAsc ? '↑' : '↓') : ''}</span>
                            </th>
                            <th class="py-3 px-5 cursor-pointer text-left" on:click={() => { sortKey = 'prix'; sortAsc = sortKey === 'prix' ? !sortAsc : true; }}>
                                Prix <span class="sort-indicator">{sortKey === 'prix' ? (sortAsc ? '↑' : '↓') : ''}</span>
                            </th>
                            {#if $auth.userRole === 'admin'}
                                <th class="py-3 px-5 text-left">Actions</th>
                            {/if}
                        </tr>
                    </thead>
                    <tbody>
                        {#each filteredBoards.slice(0, visibleBoardCount) as board}
                            <tr class="border-b border-gray-700 hover:bg-gray-800 transition-colors">
                                <td class="py-2 px-5 text-gray-300">{board.id}</td>
                                <td class="py-2 px-5 text-gray-300" on:click={() => handleCellClick('REF Asteel', board.ref_asteel)}>{board.ref_asteel}</td>
                                <td class="py-2 px-5 text-gray-300">{board.family_name}</td>
                                <td class="py-2 px-5">
                                    {#if board.is_valid}
                                        <span class="badge badge-valid">✅ Valid</span>
                                    {:else}
                                        <span class="badge badge-invalid">❌ Invalid</span>
                                    {/if}
                                </td>
                                <td class="py-2 px-5 text-gray-300">{board.prix}</td>
                                {#if $auth.userRole === 'admin'}
                                    <td class="py-2 px-5">
                                        <button class="btn-action btn-modify" on:click={() => handleModifyBoard(board.id)}>
                                            <i class="ri-edit-fill"></i> Modify
                                        </button>
                                    </td>
                                {/if}
                            </tr>
                        {/each}
                    </tbody>
                </table>
                <div class="pagination-buttons">
                    {#if visibleBoardCount < filteredBoards.length}
                        <button on:click={showMoreBoards} class="btn-primary-gradient btn-pagination">
                            Show More <i class="ri-arrow-down-s-line"></i>
                        </button>
                    {/if}
                    {#if visibleBoardCount > initialVisibleBoardCount}
                        <button on:click={showLessBoards} class="btn-primary-gradient btn-pagination">
                            Show Less <i class="ri-arrow-up-s-line"></i>
                        </button>
                    {/if}
                </div>
            </div>
        {/if}
  <section class="card">
        <div class="section-header">
            <span class="icon ri-bar-chart-2-line"></span>
            <h2 class="text-2xl font-semibold text-text-light">Quality Metrics Overview</h2>
        </div>

        <div class="metrics-filter-grid">
            <label for="selected-date" class="form-label">
                Date:
                <input type="date" id="selected-date" bind:value={selectedDate} class="form-input" />
            </label>

            <label for="start-time" class="form-label">
                Start Time:
                <input type="time" id="start-time" bind:value={selectedStartTime} class="form-input" />
            </label>

            <label for="end-time" class="form-label">
                End Time:
                <input type="time" id="end-time" bind:value={selectedEndTime} class="form-input" />
            </label>

            <div class="flex-grow"></div> 

            <button on:click={fetchMetrics} class="btn-primary-gradient">
                <i class="ri-search-line"></i> Load Metrics
            </button>
        </div>
        {#if loadingMetrics}
            <div class="spinner"></div>
        {:else if errorMessage.includes('Failed to load metrics') || errorMessage.includes('Please select a date')}
            <p class="text-red-500 mt-4">{errorMessage}</p>
        {:else if !$auth.isAuthenticated}
            <p class="text-text-dark-contrast text-center mt-4">Please log in to view quality metrics.</p>
        {:else if metrics}
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div class="metric-box bg-blue-600 text-center rounded-lg shadow-lg p-4">
                    <p class="text-lg font-semibold text-white">Total Quantity</p>
                    <p class="text-3xl font-bold text-white mt-1">{$totalQuantity.toFixed(0)}</p>
                </div>
                <div class="metric-box bg-green-600 text-center rounded-lg shadow-lg p-4">
                    <p class="text-lg font-semibold text-white">Good Quantity</p>
                    <p class="text-3xl font-bold text-white mt-1">{$goodQuantity.toFixed(0)}</p>
                </div>
                <div class="metric-box bg-red-600 text-center rounded-lg shadow-lg p-4">
                    <p class="text-lg font-semibold text-white">Bad Quantity</p>
                    <p class="text-3xl font-bold text-white mt-1">{$badQuantity.toFixed(0)}</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
             
            </div>
   {#if allTests.length > 0}
    <table class="min-w-full table-auto">
        <thead>
            <tr>
                {#each Object.keys(allTests[0]) as col}
                    <th class="py-3 px-5 text-left capitalize">{col.replace(/_/g, ' ')}</th>
                {/each}
            </tr>
        </thead>
        <tbody>
            {#each allTests.slice(0, visibleTestsCount) as test}
                <tr class="border-b border-gray-700 hover:bg-gray-800 transition-colors">
                    {#each Object.entries(test) as [key, value]}
                        <td
                            class="py-2 px-5 text-gray-300 clickable hover:text-primary-light"
                            on:click={() => handleCellClick(key, value)}
                        >
                            {value ?? '-'}
                        </td>
                    {/each}
                </tr>
            {/each}
        </tbody>
    </table>

    <div class="text-center mt-4 space-x-4">
        {#if visibleTestsCount > INITIAL_DISPLAY_COUNT}
            <button
                class="btn btn-secondary px-6 py-2 rounded-lg"
                on:click={showLessTests}
            >
                Show Less
            </button>
        {/if}
        {#if allTests.length > visibleTestsCount}
            <button
                class="btn btn-secondary px-6 py-2 rounded-lg"
                on:click={showMoreTests}
            >
                Show More ({allTests.length - visibleTestsCount} remaining)
            </button>
        {/if}
    </div>

{:else if !loadingUniqueTests && errorMessage}
    <p class="text-danger text-center">{errorMessage}</p>
{:else if !loadingUniqueTests}
    <p class="text-center">No tests found for the selected criteria. Please use the filters above.</p>
{/if}

<p class="text-text-light text-center mt-4">Select a date and time range above to view quality metrics.</p>

<div class="mt-8 pt-8 border-t border-gray-700">
    <div class="section-header">
        <span class="icon ri-search-line"></span>
        <h2 class="text-2xl font-semibold text-text-light">Unique Tests Related to Selection</h2>
    </div>

    {#if selectedMetricColumn && metricValue}
        <p class="text-text-light mt-4">Showing unique tests for <strong>{selectedMetricColumn}</strong>: <strong>{metricValue}</strong></p>
    {/if}

    {#if loadingUniqueTests}
        <div class="spinner mt-4"></div>
    {:else if uniqueTestsError}
        <p class="text-red-500 mt-4">{uniqueTestsError}</p>
    {:else if uniqueTests.length > 0}
        <h3 class="text-lg font-semibold text-text-light mt-6 mb-3">Unique Tests Found ({uniqueTests.length}):</h3>
        <div class="card overflow-x-auto">
            <table class="min-w-full table-auto">
                <thead>
                    <tr>
                        <th class="py-3 px-5 text-left">Num_Serie</th>
                        <th class="py-3 px-5 text-left">Date_Debut</th>
                        <th class="py-3 px-5 text-left">Result</th>
                        <th class="py-3 px-5 text-left">Type_Test</th>
                        <th class="py-3 px-5 text-left">Id_Machine</th>
                        <th class="py-3 px-5 text-left">Id_Operateur</th>
                        <th class="py-3 px-5 text-left">Id_Board</th>
                    </tr>
                </thead>
                <tbody>
                    {#each uniqueTests.slice(0, visibleUniqueTestsCount) as test}
                        <tr class="border-b border-gray-700 hover:bg-gray-800 transition-colors">
                            <td class="py-2 px-5 text-gray-300">{test.num_serie ?? '-'}</td>
                            <td class="py-2 px-5 text-gray-300">{test.date_debut ?? '-'}</td>
                            <td class="py-2 px-5 text-gray-300">{test.result ?? '-'}</td>
                            <td class="py-2 px-5 text-gray-300">{test.type_test ?? '-'}</td>
                            <td class="py-2 px-5 text-gray-300">{test.id_machine ?? '-'}</td>
                            <td class="py-2 px-5 text-gray-300">{test.id_operateur ?? '-'}</td>
                            <td class="py-2 px-5 text-gray-300">{test.id_board ?? '-'}</td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>

        <div class="text-center mt-4 space-x-4">
            {#if visibleUniqueTestsCount > INITIAL_DISPLAY_COUNT}
                <button
                    class="btn btn-secondary px-6 py-2 rounded-lg"
                    on:click={showLessUniqueTests}
                >
                    Show Less
                </button>
            {/if}
            {#if uniqueTests.length > visibleUniqueTestsCount}
                <button
                    class="btn btn-secondary px-6 py-2 rounded-lg"
                    on:click={showMoreUniqueTests}
                >
                    Show More ({uniqueTests.length - visibleUniqueTestsCount} remaining)
                </button>
            {/if}
        </div>

    {:else if !uniqueTestsError && selectedMetricColumn && metricValue}
        <p class="text-text-light text-center mt-4">No unique tests found for the selected criteria ({selectedMetricColumn}: {metricValue}).</p>
    {:else}
        <p class="text-text-light text-center mt-4">Click on 'REF Asteel' or 'Num_Serie' in the "Price Statistics by Asteel Reference" table above to see related unique tests.</p>
    {/if}
</div>      
    {:else}
        <p class="text-text-light text-center mt-4">No quality metrics available. Please select a date and time range.</p>
    {/if}
    </section>
</main>

<style>
    /* Debug styles */
    
  
    /* Microchip preloader styles */
    .microchip-container {
        display: flex;
        justify-content: center;
        align-items: center;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: var(--background-dark, rgba(26, 26, 26, 0.9));
        z-index: 1000;
        opacity: 1;
        transition: opacity 0.3s ease;
                pointer-events: none; /* Prevent blocking clicks when hidden */

    }

    .microchip {
        display: block;
        width: 8em;
        height: 8em;
        color: var(--microchip-core-color, #8be9fd);
    }

    .microchip__center,
    .microchip__dot,
    .microchip__line,
    .microchip__lines,
    .microchip__spark,
    .microchip__wave {
        animation-duration: 5s;
        animation-timing-function: cubic-bezier(0.65, 0, 0.35, 1);
        animation-iteration-count: infinite;
    }

    .microchip__core,
    .microchip__dot {
        fill: var(--microchip-core-color, #8be9fd);
        transition: fill 0.3s;
    }

    .microchip__center,
    .microchip__wave {
        transform-origin: 25px 25px;
    }

    .microchip__center {
        animation-name: center-scale;
    }

    .microchip__dot--1 { animation-name: dot-scale1; transform-origin: 3px 38px; }
    .microchip__dot--2 { animation-name: dot-scale2; transform-origin: 3px 54px; }
    .microchip__dot--3 { animation-name: dot-scale3; transform-origin: 3px 70px; }
    .microchip__dot--4 { animation-name: dot-scale4; transform-origin: 3px 3px; }
    .microchip__dot--5 { animation-name: dot-scale5; transform-origin: 20px 3px; }
    .microchip__dot--6 { animation-name: dot-scale6; transform-origin: 3px 30px; }
    .microchip__dot--7 { animation-name: dot-scale7; transform-origin: 37px 3px; }
    .microchip__dot--8 { animation-name: dot-scale8; transform-origin: 54px 3px; }
    .microchip__dot--9 { animation-name: dot-scale9; transform-origin: 71px 3px; }

    .microchip__line,
    .microchip__spark,
    .microchip__wave {
        transition: stroke 0.3s;
    }

    .microchip__line {
        stroke: var(--microchip-core-color, #8be9fd);
    }

    .microchip__line--1 { animation-name: line-draw1; }
    .microchip__line--2 { animation-name: line-draw2; }
    .microchip__line--3 { animation-name: line-draw3; }
    .microchip__line--4 { animation-name: line-draw4; }
    .microchip__line--5 { animation-name: line-draw5; }
    .microchip__line--6 { animation-name: line-draw6; }
    .microchip__line--7 { animation-name: line-draw7; }
    .microchip__line--8 { animation-name: line-draw8; }
    .microchip__line--9 { animation-name: line-draw9; }

    .microchip__lines {
        animation-name: linescale;
        transform-origin: 54px 54px;
    }

    .microchip__spark,
    .microchip__wave {
        animation-timing-function: linear;
        stroke: var(--microchip-active-color, #50fa7b);
    }

    .microchip__spark--1 { animation-name: spark1; }
    .microchip__spark--2 { animation-name: spark2; }
    .microchip__spark--3 { animation-name: spark3; }
    .microchip__spark--4 { animation-name: spark4; }
    .microchip__spark--5 { animation-name: spark5; }
    .microchip__spark--6 { animation-name: spark6; }
    .microchip__spark--7 { animation-name: spark7; }
    .microchip__spark--8 { animation-name: spark8; }
    .microchip__spark--9 { animation-name: spark9; }

    .microchip__wave--1 { animation-name: wave-scale1; }
    .microchip__wave--2 { animation-name: wave-scale2; }

    /* Animations */
    @keyframes center-scale {
        from, to { transform: scale(0); }
        12.5%, 75% { transform: scale(1); }
    }
    @keyframes dot-scale1 {
        from, 20%, 81.25%, to { transform: scale(0); }
        32.5%, 68.75% { transform: scale(1); }
    }
    @keyframes dot-scale2 {
        from, 10.5%, 87.5%, to { transform: scale(0); }
        23%, 75% { transform: scale(1); }
    }
    @keyframes dot-scale3 {
        from, 20%, 81.25%, to { transform: scale(0); }
        32.5%, 68.75% { transform: scale(1); }
    }
    @keyframes dot-scale4 {
        from, 20%, 81.25%, to { transform: scale(0); }
        32.5%, 68.75% { transform: scale(1); }
    }
    @keyframes dot-scale5 {
        from, 11.5%, 87.5%, to { transform: scale(0); }
        24%, 75% { transform: scale(1); }
    }
    @keyframes dot-scale6 {
        from, 14.5%, 85%, to { transform: scale(0); }
        27%, 72.5% { transform: scale(1); }
    }
    @keyframes dot-scale7 {
        from, 20%, 81.25%, to { transform: scale(0); }
        32.5%, 68.75% { transform: scale(1); }
    }
    @keyframes dot-scale8 {
        from, 11%, 87.5%, to { transform: scale(0); }
        23.5%, 75% { transform: scale(1); }
    }
    @keyframes dot-scale9 {
        from, 20%, 81.25%, to { transform: scale(0); }
        32.5%, 68.75% { transform: scale(1); }
    }
    @keyframes line-draw1 {
        from, 93.75%, to { stroke-dashoffset: 59; }
        25%, 68.75% { stroke-dashoffset: 17; }
    }
    @keyframes line-draw2 {
        from, 93.75%, to { stroke-dashoffset: 42; }
        25%, 68.75% { stroke-dashoffset: 0; }
    }
    @keyframes line-draw3 {
        from, 93.75%, to { stroke-dashoffset: 59; }
        25%, 68.75% { stroke-dashoffset: 17; }
    }
    @keyframes line-draw4 {
        from, 93.75%, to { stroke-dashoffset: 78; }
        25%, 68.75% { stroke-dashoffset: 18; }
    }
    @keyframes line-draw5 {
        from, 93.75%, to { stroke-dashoffset: 60; }
        25%, 68.75% { stroke-dashoffset: 0; }
    }
    @keyframes line-draw6 {
        from, 93.75%, to { stroke-dashoffset: 91; }
        25%, 68.75% { stroke-dashoffset: 31; }
    }
    @keyframes line-draw7 {
        from, 93.75%, to { stroke-dashoffset: 60; }
        25%, 68.75% { stroke-dashoffset: 17; }
    }
    @keyframes line-draw8 {
        from, 93.75%, to { stroke-dashoffset: 43; }
        25%, 68.75% { stroke-dashoffset: 0; }
    }
    @keyframes line-draw9 {
        from, 93.75%, to { stroke-dashoffset: 60; }
        25%, 68.75% { stroke-dashoffset: 17; }
    }
    @keyframes linescale {
        from { opacity: 1; transform: scale(0); }
        12.5%, 75% { opacity: 1; transform: scale(1); }
        93.75%, to { opacity: 0; transform: scale(0.5); }
    }
    @keyframes spark1 {
        from, 27.5% { stroke-dashoffset: 59; }
        50%, 52.5% { stroke-dashoffset: -25; }
        75%, to { stroke-dashoffset: -109; }
    }
    @keyframes spark2 {
        from, 27.5% { stroke-dashoffset: 42; }
        50%, 52.5% { stroke-dashoffset: -42; }
        75%, to { stroke-dashoffset: -126; }
    }
    @keyframes spark3 {
        from, 27.5% { stroke-dashoffset: 59; }
        50%, 52.5% { stroke-dashoffset: -25; }
        75%, to { stroke-dashoffset: -109; }
    }
    @keyframes spark4 {
        from, 27.5% { stroke-dashoffset: 78; }
        50%, 52.5% { stroke-dashoffset: -42; }
        75%, to { stroke-dashoffset: -162; }
    }
    @keyframes spark5 {
        from, 27.5% { stroke-dashoffset: 60; }
        50%, 52.5% { stroke-dashoffset: -60; }
        75%, to { stroke-dashoffset: -180; }
    }
    @keyframes spark6 {
        from, 27.5% { stroke-dashoffset: 91; }
        50%, 52.5% { stroke-dashoffset: -29; }
        75%, to { stroke-dashoffset: -149; }
    }
    @keyframes spark7 {
        from, 27.5% { stroke-dashoffset: 60; }
        50%, 52.5% { stroke-dashoffset: -26; }
        75%, to { stroke-dashoffset: -112; }
    }
    @keyframes spark8 {
        from, 27.5% { stroke-dashoffset: 43; }
        50%, 52.5% { stroke-dashoffset: -43; }
        75%, to { stroke-dashoffset: -129; }
    }
    @keyframes spark9 {
        from, 27.5% { stroke-dashoffset: 60; }
        50%, 52.5% { stroke-dashoffset: -26; }
        75%, to { stroke-dashoffset: -112; }
    }
    @keyframes wave-scale1 {
        from, 0%, 25%, 50%, 75% { stroke-width: 6px; transform: scale(1); }
        10%, 35%, 60%, 85%, to { animation-timing-function: steps(1); stroke-width: 0; transform: scale(2); }
    }
    @keyframes wave-scale2 {
        from, 5%, 30%, 55%, 80% { stroke-width: 6px; transform: scale(1); }
        15%, 40%, 65%, 90%, to { animation-timing-function: steps(1); stroke-width: 0; transform: scale(2); }
    }
</style>