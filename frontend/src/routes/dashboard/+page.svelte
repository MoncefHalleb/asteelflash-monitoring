<script>
    import { onMount, onDestroy } from 'svelte';
    import { Chart, registerables } from 'chart.js';
    import { auth } from '../../stores/authStore';
    import { get_request } from '$lib/api';
    import { goto } from '$app/navigation';
    import '../../routes/dashboard/dashboard.css';
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';

    Chart.register(...registerables);

    let boards = [];
    let searchQuery = '';
    let searchField = 'all';
    let sortKey = 'id';
    let sortAsc = true;
    let startDate = '';
    let endDate = '';
    let selectedStartTime = '00:00';
    let selectedEndTime = '23:59';
    let metrics = [];
    let loadingBoards = true;
    let loadingMetrics = false;
    let errorMessage = '';
    let visibleBoardCount = 10;
    const initialVisibleBoardCount = 10;

    let totalQuantity = tweened(0, { duration: 1000, easing: cubicOut });
    let goodQuantity = tweened(0, { duration: 1000, easing: cubicOut });
    let badQuantity = tweened(0, { duration: 1000, easing: cubicOut });
    let yieldRate = tweened(0, { duration: 1000, easing: cubicOut });
    let totalRevenue = tweened(0, { duration: 1000, easing: cubicOut });

    let quantityChart = null;
    let defectChart = null;
    let trendChart = null;
    let quantityCanvas;
    let defectCanvas;
    let trendCanvas;

    $: {
        if (!$auth.isAuthenticated && !loadingBoards && !loadingMetrics) {
            console.log('Not authenticated, redirecting to login...');
            goto('/login');
        }
    }

    $: if (metrics.length > 0) {
        const latestMetrics = metrics[metrics.length - 1] || {};
        totalQuantity.set(latestMetrics.total_quantity || 0);
        goodQuantity.set(latestMetrics.good_quantity || 0);
        badQuantity.set(latestMetrics.bad_quantity || 0);
        yieldRate.set(latestMetrics.yield_rate || 0);
        totalRevenue.set(latestMetrics.total_revenue || 0);
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

    onMount(async () => {
        if (!$auth.isAuthenticated) {
            loadingBoards = false;
            return;
        }
        try {
            const res = await get_request('/api/boards');
            boards = res;
            loadingBoards = false;
        } catch (err) {
            errorMessage = 'Failed to load boards: ' + err.message;
            loadingBoards = false;
            console.error('Error fetching boards:', err);
        }
    });

    $: {
        if (metrics.length > 0 && quantityCanvas) {
            updateQuantityChart(metrics[metrics.length - 1]);
        }
        if (metrics.length > 0 && defectCanvas) {
            updateDefectChart(metrics[metrics.length - 1].defect_details);
        }
        if (metrics.length > 0 && trendCanvas) {
            updateTrendChart(metrics);
        }
    }

    async function fetchMetrics() {
        if (!startDate || !endDate || !selectedStartTime || !selectedEndTime) {
            errorMessage = 'Please select a start date, end date, start time, and end time.';
            metrics = [];
            destroyCharts();
            return;
        }
        if (!$auth.isAuthenticated) {
            errorMessage = 'You must be logged in to fetch metrics.';
            metrics = [];
            destroyCharts();
            return;
        }

        loadingMetrics = true;
        destroyCharts();
        metrics = [];

        try {
            const startDateEncoded = encodeURIComponent(startDate);
            const endDateEncoded = encodeURIComponent(endDate);
            const startTimeEncoded = encodeURIComponent(selectedStartTime);
            const endTimeEncoded = encodeURIComponent(selectedEndTime);

            const res = await get_request(`/api/quality-metrics?start_date=${startDateEncoded}&end_date=${endDateEncoded}&start_time=${startTimeEncoded}&end_time=${endTimeEncoded}`);
            metrics = res;
            metrics.forEach(m => {
                m.total_quantity = m.total_quantity || 0;
                m.good_quantity = m.good_quantity || 0;
                m.bad_quantity = m.bad_quantity || 0;
                m.yield_rate = m.yield_rate || 0;
                m.total_revenue = m.total_revenue || 0;
            });
        } catch (err) {
            errorMessage = 'Failed to load metrics: ' + err.message;
            metrics = [];
            console.error('Error fetching metrics:', err);
        } finally {
            loadingMetrics = false;
        }
    }

    function updateQuantityChart(metric) {
        if (quantityChart) {
            quantityChart.data.datasets[0].data = [metric.total_quantity, metric.good_quantity, metric.bad_quantity];
            quantityChart.update();
        } else {
            quantityChart = new Chart(quantityCanvas, {
                type: 'bar',
                data: {
                    labels: ['Quantity'],
                    datasets: [
                        {
                            label: 'Total',
                            data: [metric.total_quantity],
                            backgroundColor: 'rgba(77, 182, 255, 0.7)',
                            borderColor: 'var(--primary)',
                            borderWidth: 1,
                            borderRadius: 5
                        },
                        {
                            label: 'Good',
                            data: [metric.good_quantity],
                            backgroundColor: 'rgba(52, 199, 89, 0.7)',
                            borderColor: 'var(--accent)',
                            borderWidth: 1,
                            borderRadius: 5
                        },
                        {
                            label: 'Bad',
                            data: [metric.bad_quantity],
                            backgroundColor: 'rgba(255, 77, 79, 0.7)',
                            borderColor: 'var(--danger)',
                            borderWidth: 1,
                            borderRadius: 5
                        }
                    ]
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
                            stacked: true,
                            ticks: { color: 'var(--text-light)' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            ticks: { color: 'var(--text-light)' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: 'var(--text-light)' } },
                        title: {
                            display: true,
                            text: 'Quantity Breakdown',
                            color: 'var(--text-light)',
                            font: { size: 18 }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.parsed.y}`;
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
                type: 'pie',
                data: {
                    labels: defectLabels,
                    datasets: [{
                        label: 'Defects',
                        data: defectCounts,
                        backgroundColor: backgroundColors,
                        borderColor: borderColors,
                        borderWidth: 1
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
                                        label += `${context.parsed} (${percentage})`;
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

    function updateTrendChart(metricsData) {
        if (trendChart) {
            trendChart.data.labels = metricsData.map(m => m.date);
            trendChart.data.datasets[0].data = metricsData.map(m => m.good_quantity);
            trendChart.data.datasets[1].data = metricsData.map(m => m.bad_quantity);
            trendChart.data.datasets[2].data = metricsData.map(m => m.yield_rate);
            trendChart.update();
        } else {
            trendChart = new Chart(trendCanvas, {
                type: 'line',
                data: {
                    labels: metricsData.map(m => new Date(m.date).toLocaleDateString()),
                    datasets: [
                        {
                            label: 'Good Quantity',
                            data: metricsData.map(m => m.good_quantity),
                            borderColor: 'var(--accent)',
                            backgroundColor: 'rgba(52, 199, 89, 0.2)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Bad Quantity',
                            data: metricsData.map(m => m.bad_quantity),
                            borderColor: 'var(--danger)',
                            backgroundColor: 'rgba(255, 77, 79, 0.2)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Yield Rate (%)',
                            data: metricsData.map(m => m.yield_rate),
                            borderColor: 'var(--primary)',
                            backgroundColor: 'rgba(77, 182, 255, 0.2)',
                            fill: true,
                            tension: 0.4,
                            yAxisID: 'y1'
                        }
                    ]
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
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            title: {
                                display: true,
                                text: 'Quantity',
                                color: 'var(--text-light)'
                            }
                        },
                        y1: {
                            position: 'right',
                            beginAtZero: true,
                            max: 100,
                            ticks: { color: 'var(--text-light)' },
                            grid: { drawOnChartArea: false },
                            title: {
                                display: true,
                                text: 'Yield Rate (%)',
                                color: 'var(--text-light)'
                            }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: 'var(--text-light)' } },
                        title: {
                            display: true,
                            text: 'Quality Metrics Trend',
                            color: 'var(--text-light)',
                            font: { size: 18 }
                        }
                    }
                }
            });
        }
    }

    function showMoreBoards() {
        visibleBoardCount += 10;
        if (visibleBoardCount > boards.length) {
            visibleBoardCount = boards.length;
        }
    }

    function showLessBoards() {
        visibleBoardCount -= 10;
        if (visibleBoardCount < initialVisibleBoardCount) {
            visibleBoardCount = initialVisibleBoardCount;
        }
    }

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
        if (trendChart) {
            trendChart.destroy();
            trendChart = null;
        }
    }

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
                <select id="board-search-field" bind:value={searchField} class="search-select">
                    <option value="all">All Fields</option>
                    <option value="id">ID</option>
                    <option value="ref_asteel">REF Asteel</option>
                    <option value="family_name">Family</option>
                    <option value="is_valid">Validity</option>
                </select>
                <div class="search-input-container">
                    <input type="text" placeholder="Search boards..." bind:value={searchQuery} class="w-full"/>
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
                                <td class="py-2 px-5">{board.prix !== null ? board.prix.toFixed(2) + ' €' : 'N/A'}</td>
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
            <label for="start-date">
                Start Date:
                <input type="date" id="start-date" bind:val