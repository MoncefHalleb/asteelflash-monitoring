<script>
  import { onMount, onDestroy } from 'svelte';
  import { auth } from '../../stores/authStore'; // Can be removed if no auth needed
  import { goto } from '$app/navigation';
  import '../../routes/dashboard/dashboard.css';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  let predictionProbability = tweened(0, { duration: 1000, easing: cubicOut });

  let formData = {
    Id: 13835955,
    Id_Board: 370,
    Num_Serie: "fds",
    Id_Machine: "TNSKRPDEKA01212",
    DateDebut: "2025-07-08T09:00",
    DateFin: "2025-07-08T09:05",
    Result: 0,
    Side: "gffgd",
    Position_Flan: 0.4,
    Id_ConfigLigne: 0.0,
    Id_Process: 0.0,
    ref_asteel: "fdsqfdsq",
    ref_client: 549,
    family_name: "dfsqfds",
    board_version: "1SBB530549R1301",
    is_valid: 0.0,
    designation: "dfsqdfsq",
    client: "fdsqfdsq",
    code_indus: "sdqfdsq1",
    indice: "sfdqdsq12",
    software: "dsq",
    software_ver: "fqds12",
    id_assembly: "1",
    id_process: "21",
    quantcondit: 0.8,
    id_famille: 1.0,
    prix: 4.0
  };

  let prediction = null;
  let errorMessage = '';
  let loading = false;

  $: {
    if (!$auth.isAuthenticated && !loading) {
      console.log('Not authenticated, redirecting to login...');
      goto('/login');
    }
  }

 async function handlePredict() {
  if (!$auth.isAuthenticated) {
    errorMessage = 'Please log in first';
    return;
  }

  loading = true;
  errorMessage = '';
  prediction = null;

  console.log('Sending formData:', formData);

  // Crée un vrai FormData pour correspondre à FastAPI
  const fd = new FormData();
  for (let key in formData) {
    fd.append(key, formData[key]);
  }

  try {
    const response = await fetch('http://127.0.0.1:8100/predict/', {
      method: 'POST',
      body: fd
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
    }

    // Comme ton backend retourne un template HTML via TemplateResponse
    const html = await response.text();
    // injecter la réponse html dans ton document
    document.body.innerHTML = html;
  } catch (err) {
    errorMessage = 'An error occurred while processing your prediction. Please try again or contact support.';
    console.error('Prediction error:', err);
  } finally {
    loading = false;
  }

  }
</script>

<main class="p-8">
  <div class="header-content">
    <img src="/images.png" alt="AsteelFlash Logo" class="logo" />
    <h1 class="text-4xl font-bold" style="display: flex; justify-content: center; width: 100%;">
      <div class="flow-text">
        <div style="
          font-family: 'Inter', sans-serif;
          font-size: 1.0em;
          font-weight: 800;
          color: #f8f8f2;
          letter-spacing: -0.01em;
          display: flex;
          align-items: flex-end;
          gap: 0.3em;
          flex-wrap: wrap;
          line-height: 1.1;
          justify-content: center;
          width: 100%;
        ">
          <span style="color: red; text-shadow: 1px 2px;">Asteel</span>
          <span style="color: Blue; font-weight: 900; text-shadow: 1px 2px;">Flash</span>
          <span style="
            color: #50fa7b;
            font-weight: 900;
            margin-left: 0.7em;
            font-size: 0.7em;
            letter-spacing: 0.01em;
            background: linear-gradient(90deg, #50fa7b 60%, #8be9fd 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            align-self: flex-end;
            margin-bottom: 0.1em;
          ">
            Test Prediction
          </span>
        </div>
      </div>
    </h1>
  </div>

  <section class="mb-12">
    <div class="section-header flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <span class="icon ri-bar-chart-2-line text-3xl text-primary"></span>
        <h2 class="text-2xl font-bold text-text-light tracking-tight">Predict Test Result</h2>
      </div>
    </div>

    <div class="card">
      <form on:submit|preventDefault={handlePredict} class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label for="Id">
          ID:
          <input type="number" bind:value={formData.Id} required class="date-picker" />
        </label>
        <label for="Id_Board">
          ID Board:
          <input type="number" bind:value={formData.Id_Board} required class="date-picker" />
        </label>
        <label for="Num_Serie">
          Num Serie:
          <input type="text" bind:value={formData.Num_Serie} class="date-picker" />
        </label>
        <label for="Id_Machine">
          ID Machine:
          <input type="text" bind:value={formData.Id_Machine} class="date-picker" />
        </label>
        <label for="DateDebut">
          Date Debut:
          <input type="datetime-local" bind:value={formData.DateDebut} required class="date-picker" />
        </label>
        <label for="DateFin">
          Date Fin:
          <input type="datetime-local" bind:value={formData.DateFin} required class="date-picker" />
        </label>
        <label for="Result">
          Result:
          <input type="number" bind:value={formData.Result} required class="date-picker" />
        </label>
        <label for="Side">
          Side:
          <input type="text" bind:value={formData.Side} class="date-picker" />
        </label>
        <label for="Position_Flan">
          Position Flan:
          <input type="number" step="0.1" bind:value={formData.Position_Flan} required class="date-picker" />
        </label>
        <label for="Id_ConfigLigne">
          ID Config Ligne:
          <input type="number" step="0.1" bind:value={formData.Id_ConfigLigne} required class="date-picker" />
        </label>
        <label for="Id_Process">
          ID Process:
          <input type="number" step="0.1" bind:value={formData.Id_Process} required class="date-picker" />
        </label>
        <label for="ref_asteel">
          Ref Asteel:
          <input type="text" bind:value={formData.ref_asteel} class="date-picker" />
        </label>
        <label for="ref_client">
          Ref Client:
          <input type="number" bind:value={formData.ref_client} required class="date-picker" />
        </label>
        <label for="family_name">
          Family Name:
          <input type="text" bind:value={formData.family_name} class="date-picker" />
        </label>
        <label for="board_version">
          Board Version:
          <input type="text" bind:value={formData.board_version} class="date-picker" />
        </label>
        <label for="is_valid">
          Is Valid:
          <input type="number" step="0.1" bind:value={formData.is_valid} required class="date-picker" />
        </label>
        <label for="designation">
          Designation:
          <input type="text" bind:value={formData.designation} class="date-picker" />
        </label>
        <label for="client">
          Client:
          <input type="text" bind:value={formData.client} class="date-picker" />
        </label>
        <label for="code_indus">
          Code Indus:
          <input type="text" bind:value={formData.code_indus} class="date-picker" />
        </label>
        <label for="indice">
          Indice:
          <input type="text" bind:value={formData.indice} class="date-picker" />
        </label>
        <label for="software">
          Software:
          <input type="text" bind:value={formData.software} class="date-picker" />
        </label>
        <label for="software_ver">
          Software Ver:
          <input type="text" bind:value={formData.software_ver} class="date-picker" />
        </label>
        <label for="id_assembly">
          ID Assembly:
          <input type="text" bind:value={formData.id_assembly} class="date-picker" />
        </label>
        <label for="id_process">
          ID Process:
          <input type="text" bind:value={formData.id_process} class="date-picker" />
        </label>
        <label for="quantcondit">
          Quant Condit:
          <input type="number" step="0.1" bind:value={formData.quantcondit} required class="date-picker" />
        </label>
        <label for="id_famille">
          ID Famille:
          <input type="number" step="0.1" bind:value={formData.id_famille} required class="date-picker" />
        </label>
        <label for="prix">
          Prix:
          <input type="number" step="0.1" bind:value={formData.prix} required class="date-picker" />
        </label>
        <div class="col-span-2 flex justify-center">
          <button type="submit" class="btn-primary-gradient" disabled={loading}>
            <i class="ri-bar-chart-2-line"></i> Predict
          </button>
        </div>
      </form>

      {#if loading}
        <div class="spinner"></div>
      {:else if errorMessage}
        <p class="text-red-600 text-center mt-4">{errorMessage}</p>
      {:else if !$auth.isAuthenticated}
        <p class="text-text-dark-contrast text-center mt-4">Please log in to make predictions.</p>
      {:else if prediction}
        <div class="mt-8 text-center">
          <h3 class="text-lg font-semibold text-text-light mb-2">Prediction Result</h3>
          <p>ID: {prediction.id}</p>
          <p>Prediction: {prediction.prediction}</p>
          <p>Probability: {$predictionProbability.toFixed(2)}%</p>
        </div>
      {/if}
    </div>
  </section>
</main>

<style>
  .date-picker {
    padding: 0.3em 0.6em;
    border: 1px solid var(--text-light);
    border-radius: 5px;
    background: transparent;
    color: var(--text-light);
    width: 100%;
  }

  .btn-primary-gradient {
    background: linear-gradient(90deg, var(--primary), var(--primary-dark));
    border: none;
    color: var(--text-light);
    padding: 0.5em 1em;
    border-radius: 5px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .btn-primary-gradient:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(139, 233, 253, 0.3);
  }

  .btn-primary-gradient:disabled {
    background: gray;
    cursor: not-allowed;
  }

  .card {
    background: var(--card-bg);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .icon {
    color: var(--text-light);
  }

  .spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin: 20px auto;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>