<script>
    import { createEventDispatcher } from 'svelte';
    import { post, put } from '$lib/api';

    const dispatch = createEventDispatcher();

    export let board = null;
    export let mode = 'create';

    let formBoard = {
        Id: '',
        REF_AsteelFlash: '',
        REF_Clients: '',
        Designation: '',
        Client: '',
        Board_Ver: '',
        Code_Indus: '',
        Indice: '',
        Software: '',
        Software_Ver: '',
        Valide: true,
        Id_Assembly: '',
        Id_Process: '',
        QuantCondit: '',
        Id_Famille: '',
        prix: '',
    };

    let errorMessage = '';
    let successMessage = '';
    let loading = false;

    $: if (board) {
        formBoard = {
            Id: board.id,
            REF_AsteelFlash: board.ref_asteel || '',
            REF_Clients: board.ref_client || '',
            Designation: board.designation || '',
            Client: board.client || '',
            Board_Ver: board.board_version || '',
            Code_Indus: board.code_indus || '',
            Indice: board.indice || '',
            Software: board.software || '',
            Software_Ver: board.software_ver || '',
            Valide: board.is_valid !== undefined ? board.is_valid : true,
            Id_Assembly: board.id_assembly || '',
            Id_Process: board.id_process || '',
            QuantCondit: board.quantcondit || '',
            Id_Famille: board.id_famille || '',
            prix: board.prix || '',
        };
    } else {
        formBoard = {
            Id: '',
            REF_AsteelFlash: '',
            REF_Clients: '',
            Designation: '',
            Client: '',
            Board_Ver: '',
            Code_Indus: '',
            Indice: '',
            Software: '',
            Software_Ver: '',
            Valide: true,
            Id_Assembly: '',
            Id_Process: '',
            QuantCondit: '',
            Id_Famille: '',
            prix: '',
        };
    }

    async function handleSubmit() {
        errorMessage = '';
        successMessage = '';
        loading = true;

        const dataToSend = {};
        for (const key in formBoard) {
            let value = formBoard[key];
            if (mode === 'edit' && key !== 'Id' && (value === '' || value === null)) {
                continue;
            }
            if (value !== null && value !== '') {
                if (['Id', 'Id_Assembly', 'Id_Process', 'QuantCondit', 'Id_Famille'].includes(key)) {
                    const parsedValue = parseInt(value, 10);
                    console.log(`[DEBUG] ${key} raw:`, value, 'parsed:', parsedValue);
                    if (isNaN(parsedValue)) {
                        errorMessage = `Invalid number for ${key}.`;
                        loading = false;
                        return;
                    }
                    dataToSend[key] = parsedValue;
                } else if (key === 'prix') {
                    console.log('[DEBUG] prix raw value:', value, 'type:', typeof value);
                    const parsedValue = parseFloat(value);
                    if (isNaN(parsedValue)) {
                        errorMessage = `Invalid number for prix.`;
                        loading = false;
                        return;
                    }
                    dataToSend[key] = parsedValue;
                    console.log('[DEBUG] prix parsed value:', parsedValue, 'type:', typeof parsedValue);
                } else if (key === 'Valide') {
                    dataToSend[key] = Boolean(value);
                } else {
                    dataToSend[key] = value;
                }
            }
        }

        console.log('[DEBUG] Final dataToSend payload:', dataToSend);

        try {
            if (mode === 'create') {
                delete dataToSend.Id;
                const newBoard = await post('/api/boards/', dataToSend);
                console.log('[DEBUG] Backend response (create):', newBoard);
                successMessage = `Board "${newBoard.ref_asteel}" (ID: ${newBoard.id}) created successfully!`;
            } else if (mode === 'edit') {
                const boardId = formBoard.Id;
                if (!boardId) {
                    errorMessage = "Board ID is missing for update.";
                    loading = false;
                    return;
                }
                delete dataToSend.Id;
                const updatedBoard = await put(`/api/boards/${boardId}`, dataToSend);
                console.log('[DEBUG] Backend response (edit):', updatedBoard);
                successMessage = `Board ID ${updatedBoard.id} updated successfully!`;
            }
            dispatch('success');
        } catch (err) {
            console.error('Error submitting board form:', err);
            errorMessage = err.message || 'An unexpected error occurred.';
        } finally {
            loading = false;
        }
    }

    function handleCancel() {
        dispatch('cancel');
    }
    
</script>

<div class="board-form-outer">
    <div class="board-form-wrapper">
        <div class="section-header">
            <span class="icon ri-board-line"></span>
            <h2 class="text-2xl font-semibold text-text-light">
                {mode === 'create' ? 'Create New Board' : `Edit Board ID: ${board ? board.id : ''}`}
            </h2>
        </div>

        {#if errorMessage}
            <p class="error-message">{errorMessage}</p>
        {/if}
        {#if successMessage}
            <p class="success-message">{successMessage}</p>
        {/if}

        <form on:submit|preventDefault={handleSubmit} class="board-form-grid">
            <div class="form-col">
                <label for="REF_AsteelFlash">
                    Asteel Flash Ref:
                    <input type="text" id="REF_AsteelFlash" name="REF_AsteelFlash" bind:value={formBoard.REF_AsteelFlash} placeholder="Enter Asteel Flash Reference" />
                </label>
                <label for="REF_Clients">
                    Client Ref:
                    <input type="text" id="REF_Clients" name="REF_Clients" bind:value={formBoard.REF_Clients} placeholder="Enter Client Reference" />
                </label>
                <label for="Designation">
                    Designation:
                    <input type="text" id="Designation" name="Designation" bind:value={formBoard.Designation} placeholder="Enter Designation" />
                </label>
                <label for="Client">
                    Client:
                    <input type="text" id="Client" name="Client" bind:value={formBoard.Client} placeholder="Enter Client Name" />
                </label>
                <label for="Board_Ver">
                    Board Version:
                    <input type="text" id="Board_Ver" name="Board_Ver" bind:value={formBoard.Board_Ver} placeholder="Enter Board Version" />
                </label>
                <label for="Code_Indus">
                    Industrial Code:
                    <input type="text" id="Code_Indus" name="Code_Indus" bind:value={formBoard.Code_Indus} placeholder="Enter Industrial Code" />
                </label>
                <label for="Indice">
                    Indice:
                    <input type="text" id="Indice" name="Indice" bind:value={formBoard.Indice} placeholder="Enter Indice" />
                </label>
            </div>
            <div class="form-col">
                <label for="Software">
                    Software:
                    <input type="text" id="Software" name="Software" bind:value={formBoard.Software} placeholder="Enter Software Name" />
                </label>
                <label for="Software_Ver">
                    Software Version:
                    <input type="text" id="Software_Ver" name="Software_Ver" bind:value={formBoard.Software_Ver} placeholder="Enter Software Version" />
                </label>
                <label for="Id_Assembly">
                    Assembly ID:
                    <input type="number" id="Id_Assembly" name="Id_Assembly" bind:value={formBoard.Id_Assembly} placeholder="Enter Assembly ID" />
                </label>
                <label for="Id_Process">
                    Process ID:
                    <input type="number" id="Id_Process" name="Id_Process" bind:value={formBoard.Id_Process} placeholder="Enter Process ID" />
                </label>
                <label for="QuantCondit">
                    Quantity Condition:
                    <input type="number" id="QuantCondit" name="QuantCondit" bind:value={formBoard.QuantCondit} placeholder="Enter Quantity Condition" />
                </label>
                <label for="Id_Famille">
                    Family ID:
                    <input type="number" id="Id_Famille" name="Id_Famille" bind:value={formBoard.Id_Famille} placeholder="Enter Family ID" />
                </label>
                <label for="prix">
                    Prix:
                    <input type="number" id="prix" name="prix" bind:value={formBoard.prix} placeholder="Enter Prix" />
                </label>
                <div class="form-field switch-field">
                    <div class="form-check form-switch">
                        <input
                            class="form-check-input"
                            type="checkbox"
                            role="switch"
                            id="ValideSwitch"
                            bind:checked={formBoard.Valide}
                        />
                        <label class="form-check-label" for="ValideSwitch">{formBoard.Valide ? 'Board is Valid' : 'Board is Invalid'}</label>
                    </div>
                </div>
            </div>
            <div class="form-actions">
                <button type="submit" class="btn-primary-gradient" disabled={loading}>
                    {#if loading}
                        <div class="spinner-small"></div>
                        Saving...
                    {:else}
                        <i class="ri-save-fill"></i> {mode === 'create' ? 'Create Board' : 'Update Board'}
                    {/if}
                </button>
                <button type="button" class="btn-secondary" on:click={handleCancel}>
                    <i class="ri-close-circle-fill"></i> Cancel
                </button>
            </div>
        </form>
    </div>
</div>


<style>
    /* Variables for theming (define these in a global CSS file or :root) */
    :root {
        --primary-gradient-start: #6a11cb; /* Example: Deep Purple */
        --primary-gradient-end: #2575fc;   /* Example: Bright Blue */
        --secondary-button-bg: #6c757d;    /* Muted Grey */
        --secondary-button-hover-bg: #5a6268;
        --text-light: #e0e0e0;             /* Light grey for text on dark backgrounds */
        --text-dark-contrast: #333;        /* Dark text for light backgrounds */
        --background-card: #2d3142;        /* Darker background for cards/forms */
        --border-color: rgba(139, 233, 253, 0.2); /* Light blue-ish for borders */
        --danger: #ff5555;                 /* Red for errors */
        --accent: #50fa7b;                 /* Green for success */
        --input-bg: rgba(255, 255, 255, 0.1);
        --input-border-focus: #8be9fd; /* Light blue for input focus */
        --shadow-light: rgba(0, 0, 0, 0.1);
        --shadow-medium: rgba(0, 0, 0, 0.2);

        /* New variables for switch */
        --switch-bg-off: #6c757d; /* Grey when off */
        --switch-bg-on: var(--primary-gradient-end); /* Primary color when on */
        --switch-thumb-bg: #f8f9fa; /* Light background for the thumb */
        --switch-thumb-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
    }

    /* --- General Form Container --- */
    .board-form-outer {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        min-height: 100vh;
        background: linear-gradient(120deg, #232526 0%, #414345 100%);
        padding: 2rem 0;
    }

    .board-form-wrapper {
        background: var(--background-card);
        padding: 2.5rem 2rem;
        border-radius: 1.2rem;
        box-shadow: 0 10px 30px var(--shadow-medium);
        margin-top: 0.3rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        width: 100%;
        max-width: 1500px;
    }

    /* --- Section Header --- */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-bottom: 0.5rem;
        color: var(--text-light);
    }

    .section-header .icon {
        font-size: 2rem;
        color: var(--primary-gradient-end);
    }

    .section-header h2 {
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* --- Form Grid Layout --- */
    .board-form-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 2.5rem 2rem;
        margin-bottom: 0.5rem;
    }

    .form-col {
        flex: 1 1 320px;
        min-width: 320px;
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
    }

    /* --- Form Labels and Inputs --- */
    .board-form-grid label {
        display: flex;
        flex-direction: column;
        font-weight: 500;
        color: var(--text-light);
        gap: 0.5rem;
        font-size: 0.97rem;
    }

    .board-form-grid input[type="text"],
    .board-form-grid input[type="number"] {
        width: 100%;
        box-sizing: border-box;
        background: var(--input-bg);
        border: 1px solid var(--border-color);
        color: var(--text-light);
        padding: 0.85rem 1.1rem;
        border-radius: 0.6rem;
        box-shadow: inset 0 2px 5px var(--shadow-light);
        font-size: 1rem;
        transition: border-color 0.3s, box-shadow 0.3s;
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
    }

    .board-form-grid input::placeholder {
        color: rgba(255, 255, 255, 0.4);
    }

    .board-form-grid input[type="text"]:focus,
    .board-form-grid input[type="number"]:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px rgba(139, 233, 253, 0.2);
    }

    .board-form-grid input[type="number"]:disabled {
        background-color: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.5);
        cursor: not-allowed;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* --- Switch Checkbox Styling --- */
    .form-field.switch-field {
        display: flex;
        align-items: center;
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
    }

    .form-check {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        min-height: 1.5rem;
        padding-left: 0;
    }

    .form-check-input {
        width: 3.2rem;
        height: 1.7rem;
        margin-top: 0;
        background-color: var(--switch-bg-off);
        border: 1px solid rgba(0, 0, 0, 0.25);
        border-radius: 1.7rem;
        appearance: none;
        cursor: pointer;
        transition: background-color 0.3s, border-color 0.3s;
        position: relative;
        flex-shrink: 0;
    }

    .form-check-input:focus {
        outline: 0;
        box-shadow: 0 0 0 0.25rem rgba(139, 233, 253, 0.4);
        border-color: var(--input-border-focus);
    }

    .form-check-input::before {
        content: "";
        float: left;
        width: 1.3rem;
        height: 1.3rem;
        background-color: var(--switch-thumb-bg);
        border-radius: 50%;
        transition: transform 0.3s, background-color 0.3s, box-shadow 0.3s;
        position: absolute;
        top: 0.15rem;
        left: 0.2rem;
        box-shadow: var(--switch-thumb-shadow);
    }

    .form-check-input:checked {
        background-color: var(--switch-bg-on);
        border-color: var(--switch-bg-on);
    }

    .form-check-input:checked::before {
        transform: translateX(1.5rem);
        background-color: var(--switch-thumb-bg);
    }

    .form-check-input:disabled {
        pointer-events: none;
        opacity: 0.65;
        background-color: var(--switch-bg-off);
    }

    .form-check-input:disabled::before {
        background-color: rgba(255, 255, 255, 0.6);
    }

    .form-check-label {
        font-size: 1rem;
        color: var(--text-light);
        cursor: pointer;
        padding-left: 0;
        font-weight: 600;
        letter-spacing: 0.01em;
    }

    /* --- Form Actions (Buttons) --- */
    .form-actions {
        width: 100%;
        display: flex;
        justify-content: flex-end;
        gap: 1.25rem;
        margin-top: 2.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 1.5rem;
    }

    .btn-primary-gradient,
    .btn-secondary {
        padding: 0.9rem 1.8rem;
        border: none;
        border-radius: 0.6rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.6rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px var(--shadow-light);
    }

    .btn-primary-gradient {
        background: linear-gradient(45deg, var(--primary-gradient-start), var(--primary-gradient-end));
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }

    .btn-primary-gradient:hover:not(:disabled) {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px var(--shadow-medium);
        filter: brightness(1.1);
    }

    .btn-primary-gradient:disabled {
        background: linear-gradient(45deg, #4b0e8c, #1a5ac5);
        cursor: not-allowed;
        opacity: 0.7;
        box-shadow: none;
    }

    .btn-secondary {
        background-color: var(--secondary-button-bg);
        color: white;
    }

    .btn-secondary:hover {
        background-color: var(--secondary-button-hover-bg);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px var(--shadow-medium);
    }

    /* --- Message Styles --- */
    .error-message,
    .success-message {
        padding: 1rem 1.25rem;
        border-radius: 0.6rem;
        margin-bottom: 1.5rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
        animation: fadeIn 0.5s ease-out;
    }

    .error-message {
        color: var(--danger);
        background-color: rgba(255, 85, 85, 0.15);
        border: 1px solid var(--danger);
    }

    .success-message {
        color: var(--accent);
        background-color: rgba(80, 250, 123, 0.15);
        border: 1px solid var(--accent);
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* --- Spinner --- */
    .spinner-small {
        border: 3px solid rgba(255, 255, 255, 0.4);
        border-top: 3px solid white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        animation: spin 0.8s linear infinite;
        display: inline-block;
        margin-right: 10px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* --- Webkit Date/Time Input Icons (if applicable) --- */
    :global(input[type="date"]::-webkit-calendar-picker-indicator),
    :global(input[type="time"]::-webkit-calendar-picker-indicator) {
        filter: invert(1);
        opacity: 0.8;
        cursor: pointer;
    }

    /* --- Responsive Adjustments --- */
    @media (max-width: 900px) {
        .board-form-grid {
            flex-direction: column;
            gap: 2rem 0;
        }
        .form-col {
            min-width: 0;
        }
        .form-actions {
            flex-direction: column;
            align-items: stretch;
        }
        .btn-primary-gradient,
        .btn-secondary {
            width: 100%;
        }
    }
</style>