<script>
    import { onMount, onDestroy } from 'svelte';
    import { Chart, registerables } from 'chart.js';
    import { auth } from '../../stores/authStore'; // Import the auth store
    import { get_request } from '$lib/api'; // Import the authenticated API helper
    import { goto } from '$app/navigation'; // For redirection
    import '../../routes/dashboard/dashboard.css'; // Your CSS file
 import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';

    let totalQuantity = tweened(0, { duration: 1000, easing: cubicOut });
    let goodQuantity = tweened(0, { duration: 1000, easing: cubicOut });
    let badQuantity = tweened(0, { duration: 1000, easing: cubicOut });

    
    // Register all Chart.js components (like scales, elements, etc.)
    Chart.register(...registerables);

    let boards = [];
    let searchQuery = '';
    let searchField = 'all';
    let sortKey = 'id';
    let sortAsc = true;
    // State variables for date and two times
    let selectedDate = '';
    let selectedStartTime = '00:00'; // Default start time
    let selectedEndTime = '23:59';    // Default end time

    let metrics = null;
    let loadingBoards = true;
    let loadingMetrics = false;
    let errorMessage = ''; // Renamed from 'error' to avoid conflict with potential global error

    // Pagination for boards table
    let visibleBoardCount = 10; // Initially show 10 boards
    const initialVisibleBoardCount = 10; // Define a constant for the initial count
$: if (metrics) {
        totalQuantity.set(metrics.total_quantity || 0);
        goodQuantity.set(metrics.good_quantity || 0);
        badQuantity.set(metrics.bad_quantity || 0);
    }
    // Computed filtered and sorted boards
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

    // Chart instances
    let quantityChart = null;
    let defectChart = null;

    // References to the canvas elements
    let quantityCanvas;
    let defectCanvas;

    // Reactive statement to check authentication status and redirect
    // This will run whenever $auth (the store) changes, including on initial load
    $: {
        if (!$auth.isAuthenticated && !loadingBoards && !loadingMetrics) {
            console.log('Not authenticated, redirecting to login...');
            goto('/login');
        }
    }

    onMount(async () => {
        // Fetch boards only if authenticated
        if (!$auth.isAuthenticated) {
            loadingBoards = false; // Mark as done loading even if not authenticated
            return; // Exit if not authenticated, redirection handled by reactive block
        }

        try {
            const res = await get_request('/api/boards'); // Use get_request
            boards = res; // get_request already parses JSON
            loadingBoards = false;
        } catch (err) {
            errorMessage = 'Failed to load boards: ' + err.message;
            loadingBoards = false;
            console.error('Error fetching boards:', err);
        }
    });

    // Reactive statement to re-render charts when metrics data and canvases are ready
    $: {
        if (metrics && quantityCanvas) {
            updateQuantityChart(metrics.good_quantity, metrics.bad_quantity);
        }
        if (metrics && defectCanvas) {
            updateDefectChart(metrics.defect_details);
        }
    }

    async function fetchMetrics() {
        // Ensure date and times are selected
        if (!selectedDate || !selectedStartTime || !selectedEndTime) {
            errorMessage = 'Please select a date, start time, and end time.';
            metrics = null; // Clear metrics to hide charts
            destroyCharts(); // Destroy existing charts if selection is incomplete
            return;
        }

        // Only proceed if authenticated
        if (!$auth.isAuthenticated) {
            errorMessage = 'You must be logged in to fetch metrics.';
            metrics = null;
            destroyCharts();
            return;
        }

        loadingMetrics = true;
        // Destroy existing charts before fetching new metrics to prevent old data flicker
        destroyCharts();
        metrics = null; // Clear metrics to hide charts and trigger re-render of canvas elements if needed

        try {
            const dateEncoded = encodeURIComponent(selectedDate);
            const startTimeEncoded = encodeURIComponent(selectedStartTime);
            const endTimeEncoded = encodeURIComponent(selectedEndTime);

            const res = await get_request(`/api/quality-metrics?selected_date=${dateEncoded}&start_time=${startTimeEncoded}&end_time=${endTimeEncoded}`);

            metrics = res; // get_request already parses JSON
            // Ensure numbers are not null for display, default to 0
            metrics.total_quantity = metrics.total_quantity || 0;
            metrics.good_quantity = metrics.good_quantity || 0;
            metrics.bad_quantity = metrics.bad_quantity || 0;

        } catch (err) {
            errorMessage = 'Failed to load metrics: ' + err.message;
            metrics = null; // Clear old metrics on error
            console.error('Error fetching metrics:', err);
        } finally {
            loadingMetrics = false;
        }
    }

    // Function to create/update the Quantity Chart
    function updateQuantityChart(good, bad) {
    if (quantityChart) {
        quantityChart.data.datasets[0].data = [good, bad];
        quantityChart.update();
    } else {
        quantityChart = new Chart(quantityCanvas, {
            type: 'bar',
            data: {
                labels: ['Good Quantity', 'Bad Quantity'],
                datasets: [{
                    label: 'Quantity',
                    data: [good, bad],
                    backgroundColor: [
                        'rgba(80, 250, 123, 0.7)',
                        'rgba(255, 85, 85, 0.7)'
                    ],
                    borderColor: [
                        'var(--accent)',
                        'var(--danger)'
                    ],
                    borderWidth: 1,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                },
                scales: {
                    x: {
                        ticks: { color: 'var(--text-light)' },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: 'var(--text-light)' },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    }
                },
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Good vs. Bad Quantity',
                        color: 'var(--text-light)',
                        font: { size: 18 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) label += context.parsed.y;
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
}

    function updateDefectChart(defectDetails) {
    if (defectChart) {
        defectChart.data.labels = Object.keys(defectDetails);
        defectChart.data.datasets[0].data = Object.values(defectDetails);
        defectChart.update();
    } else {
        const defectLabels = Object.keys(defectDetails);
        const defectCounts = Object.values(defectDetails);
        const totalDefects = defectCounts.reduce((sum, count) => sum + count, 0);

        const backgroundColors = [
            'rgba(139, 233, 253, 0.7)',
            'rgba(80, 250, 123, 0.7)',
            'rgba(255, 121, 198, 0.7)',
            'rgba(241, 250, 140, 0.7)',
            'rgba(98, 218, 255, 0.7)',
            'rgba(189, 147, 249, 0.7)'
        ];
        const borderColors = [
            'var(--primary)',
            'var(--accent)',
            '#ff79c6',
            'var(--warn)',
            '#62daff',
            '#bd93f9'
        ];

        defectChart = new Chart(defectCanvas, {
            type: 'doughnut',
            data: {
                labels: defectLabels,
                datasets: [{
                    label: 'Defects',
                    data: defectCounts,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1000,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: 'var(--text-light)' }
                    },
                    title: {
                        display: true,
                        text: 'Defect Breakdown',
                        color: 'var(--text-light)',
                        font: { size: 18 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) label += ': ';
                                if (context.parsed !== null) {
                                    const percentage = totalDefects > 0 ? ((context.parsed / totalDefects) * 100).toFixed(2) + '%' : '0%';
                                    label += context.parsed + ` (${percentage})`;
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
}


    // Function to show more boards
    function showMoreBoards() {
        visibleBoardCount += 10; // Increase by 10 or any desired amount
        if (visibleBoardCount > boards.length) {
            visibleBoardCount = boards.length; // Don't exceed total boards
        }
    }

    // Function to show less boards
    function showLessBoards() {
        visibleBoardCount -= 10; // Decrease by 10
        if (visibleBoardCount < initialVisibleBoardCount) {
            visibleBoardCount = initialVisibleBoardCount; // Don't go below the initial count
        }
    }

    // Cleanup function for charts when component is destroyed
    onDestroy(() => {
        destroyCharts();
    });

    function destroyCharts() {
        if (quantityChart) {
            quantityChart.destroy();
            quantityChart = null;
        }
        if (defectChart) {
            defectChart.destroy();
            defectChart = null;
        }
    }

    // Placeholder functions for admin actions
    function handleAddNewBoard() {
        console.log("Admin: Initiating Add New Board...");
        goto('/boards/new');
    }

    function handleModifyBoard(boardId) {
        console.log("Admin: Initiating Modify Board for ID:", boardId);
        goto(`/boards/edit/${boardId}`);
    }
</script>

<main class="p-8">
    

    <div class="header-content">
        <img src="/images.png" alt="AsteelFlash Logo" class="logo"/>
        <h1 class="text-4xl font-bold">
            <span style="color: red;">ASTEELFLASH DEV</span>
            <span style="color: blue;"> & TESTS Dashboard</span>
        </h1>
    </div>

    <section class="mb-12">
        <div class="section-header">
            <span class="icon ri-clipboard-line"></span>
            <h2 class="text-2xl font-semibold text-text-light">Boards Information</h2>
                            {boards.length} Boards

        </div>

      

        <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
            <div class="flex flex-col md:flex-row gap-3 w-full md:w-2/3 items-center">
                <label class="text-text-light font-medium" for="board-search-field">
                    <i class="ri-filter-3-line mr-1"></i> Search by:
                </label>
                <select
                    id="board-search-field"
                    bind:value={searchField}
                    class="search-select"
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
                        class="w-full"
                    />
                    <span class="search-icon">
                        <i class="ri-search-line"></i>
                    </span>
                </div>
            </div>
              {#if $auth.userRole === 'admin'}
            <div class="admin-actions">
                <button class="add-button" on:click={handleAddNewBoard}>
                    <i class="ri-add-circle-fill"></i> Add New Board
                </button>
            </div>
        {/if}
        </div>
        {#if errorMessage.includes('Failed to load boards')}
            <p class="text-red-600">{errorMessage}</p>
        {:else if loadingBoards}
            <div class="spinner"></div>
        {:else if !$auth.isAuthenticated}
            <p class="text-text-dark-contrast text-center mt-4">Please log in to view board information.</p>
        {:else}
            <div class="card overflow-x-auto">
                <table class="min-w-full">
                    <thead>
                        <tr>
                            <th class="py-3 px-5 cursor-pointer" on:click={() => { sortKey = 'id'; sortAsc = sortKey === 'id' ? !sortAsc : true; }}>
                                ID <span class="sort-indicator">{sortKey === 'id' ? (sortAsc ? '▲' : '▼') : ''}</span>
                            </th>
                            <th class="py-3 px-5 cursor-pointer" on:click={() => { sortKey = 'ref_asteel'; sortAsc = sortKey === 'ref_asteel' ? !sortAsc : true; }}>
                                REF Asteel <span class="sort-indicator">{sortKey === 'ref_asteel' ? (sortAsc ? '▲' : '▼') : ''}</span>
                            </th>
                            <th class="py-3 px-5 cursor-pointer" on:click={() => { sortKey = 'family_name'; sortAsc = sortKey === 'family_name' ? !sortAsc : true; }}>
                                Family <span class="sort-indicator">{sortKey === 'family_name' ? (sortAsc ? '▲' : '▼') : ''}</span>
                            </th>
                            <th class="py-3 px-5 cursor-pointer" on:click={() => { sortKey = 'is_valid'; sortAsc = sortKey === 'is_valid' ? !sortAsc : true; }}>
                                Validity <span class="sort-indicator">{sortKey === 'is_valid' ? (sortAsc ? '▲' : '▼') : ''}</span>
                            </th>
                            <th class="py-3 px-5 cursor-pointer" on:click={() => { sortKey = 'prix'; sortAsc = sortKey === 'prix' ? !sortAsc : true; }}>
                                Prix <span class="sort-indicator">{sortKey === 'prix' ? (sortAsc ? '▲' : '▼') : ''}</span>
                            </th>
                            {#if $auth.userRole === 'admin'}
                                <th class="py-3 px-5">Actions</th>
                            {/if}
                        </tr>
                    </thead>
                    <tbody>
                        {#each filteredBoards.slice(0, visibleBoardCount) as board}
                            <tr class="border-b">
                                <td class="py-2 px-5">{board.id}</td>
                                <td class="py-2 px-5">{board.ref_asteel}</td>
                                <td class="py-2 px-5">{board.family_name}</td>
                                <td class="py-2 px-5">
                                    {#if board.is_valid}
                                        <span class="badge">✔️ Valid</span>
                                    {:else}
                                        <span class="badge bad">❌ Invalid</span>
                                    {/if}
                                </td>
                                                                <td class="py-2 px-5">{board.prix}</td>

                                {#if $auth.userRole === 'admin'}
                                    <td class="py-2 px-5">
                                        <button class="modify-button" on:click={() => handleModifyBoard(board.id)}>
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
                            Show More ({filteredBoards.length - visibleBoardCount} remaining)
                        </button>
                    {/if}
                    {#if visibleBoardCount > initialVisibleBoardCount}
                        <button on:click={showLessBoards} class="btn-primary-gradient btn-pagination">
                            Show Less
                        </button>
                    {/if}
                </div>
            </div>
        {/if}
    </section>

    <section class="card">
        <div class="section-header">
            <span class="icon ri-bar-chart-2-line"></span>
            <h2 class="text-2xl font-semibold text-text-light">Quality Metrics Overview</h2>
        </div>

        <div class="metrics-filter-grid">
            <label for="selected-date">
                Date:
                <input type="date" id="selected-date" bind:value={selectedDate} />
            </label>

            <label for="start-time">
                Start Time:
                <input type="time" id="start-time" bind:value={selectedStartTime} />
            </label>

            <label for="end-time">
                End Time:
                <input type="time" id="end-time" bind:value={selectedEndTime} />
            </label>

            <div class="flex-grow"></div> 

            <button on:click={fetchMetrics} class="btn-primary-gradient">
                <i class="ri-search-line"></i> Load Metrics
            </button>
        </div>
        {#if loadingMetrics}
            <div class="spinner"></div>
        {:else if errorMessage.includes('Failed to load metrics') || errorMessage.includes('Please select a date')}
            <p class="text-red-600">{errorMessage}</p>
        {:else if !$auth.isAuthenticated}
            <p class="text-text-dark-contrast text-center mt-4">Please log in to view quality metrics.</p>
        {:else if metrics}
           <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
    <div class="p-4 bg-blue-600 text-center rounded shadow-md">
        <p class="text-lg font-semibold text-white">Total Quantity</p>
        <p class="text-2xl font-bold text-white">{$totalQuantity.toFixed(0)}</p>
    </div>
    <div class="p-4 bg-green-600 text-center rounded shadow-md">
        <p class="text-lg font-semibold text-white">Good Quantity</p>
        <p class="text-2xl font-bold text-white">{$goodQuantity.toFixed(0)}</p>
    </div>
    <div class="p-4 bg-red-600 text-center rounded shadow-md">
        <p class="text-lg font-semibold text-white">Bad Quantity</p>
        <p class="text-2xl font-bold text-white">{$badQuantity.toFixed(0)}</p>
    </div>
</div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="chart-container">
                    <canvas bind:this={quantityCanvas}></canvas>
                </div>
                <div class="chart-container">
                    <canvas bind:this={defectCanvas}></canvas>
                </div>
            </div>
{#if metrics.ref_price_stats && metrics.ref_price_stats.length > 0}
    <div class="mt-8">
        <h3 class="text-lg font-semibold text-text-light mb-2">Price Statistics by Asteel Reference:</h3>
        <div class="card overflow-x-auto">
            <table class="min-w-full">
                <thead>
                    <tr>
                        <th class="py-3 px-5">REF Asteel</th>
                        <th class="py-3 px-5">Good Tests</th>
                        <th class="py-3 px-5">Bad Tests</th>
                        <th class="py-3 px-5">Unit Price</th>
                        <th class="py-3 px-5">Total Price</th>
                    </tr>
                </thead>
                <tbody>
                    {#each metrics.ref_price_stats as stat}
                        <tr class="border-b">
                            <td class="py-2 px-5">{stat.ref_asteel}</td>
                            <td class="py-2 px-5 text-green-600 font-semibold">{stat.good_count}</td>
                            <td class="py-2 px-5 text-green-600 font-semibold">{stat.bad_count}</td>
                            <td class="py-2 px-5">{stat.unit_price !== null ? stat.unit_price.toFixed(2) + ' €' : 'N/A'}</td>
                            <td class="py-2 px-5 font-semibold">{stat.total_price !== null ? stat.total_price.toFixed(2) + ' €' : 'N/A'}</td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </div>
{/if}

        {:else}
            <p class="text-text-dark-contrast text-center mt-4">Select a date and time range above to view quality metrics.</p>
        {/if}
    </section>
</main>