document.addEventListener('DOMContentLoaded', function() {
    const storageIdSelect = document.getElementById('storage_id');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const modeStorage = document.getElementById('mode_storage');
    const modeProduction = document.getElementById('mode_production');
    const expirationInput = document.getElementById('expiration_date');
    
    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    function updateEndDateConstraints() {
        const selectedOption = storageIdSelect.options[storageIdSelect.selectedIndex];
        const isProduction = modeProduction.checked;
        if (!startDateInput.value) return;
        const startDate = new Date(startDateInput.value);

        if (isProduction) {
            const minTime = parseInt(selectedOption.dataset.minTime) || 0;
            const maxTime = parseInt(selectedOption.dataset.maxTime) || 0;

            if (minTime >= 0 && maxTime >= minTime) {
                const minEndDate = new Date(startDate);
                minEndDate.setDate(startDate.getDate() + minTime);

                const maxEndDate = new Date(startDate);
                maxEndDate.setDate(startDate.getDate() + maxTime);

                // Populate production min/max fields
                const minInput = document.getElementById('min_end_date');
                const maxInput = document.getElementById('max_end_date');
                if (minInput) minInput.value = formatDate(minEndDate);
                if (maxInput) maxInput.value = formatDate(maxEndDate);
            }
        } else {
            // For storage mode, set expiration_date minimum to start date
            if (expirationInput) {
                expirationInput.min = formatDate(startDate);
                // Do not auto-fill expiration, but make it required by the HTML form
            }
        }
    }
    
    function updateFormForMode() {
        const isProduction = modeProduction.checked;
        const selectedOption = storageIdSelect.options[storageIdSelect.selectedIndex];
        
        // Update the ingredient dropdown based on mode
        for (let option of storageIdSelect.options) {
            if (option.value) { // Skip the placeholder option
                const isProducible = option.dataset.producible === 'true';
                option.disabled = isProduction && !isProducible;
                if (isProduction && !isProducible) {
                    option.style.color = 'gray';
                    option.title = '이 재료는 생산할 수 없습니다';
                } else {
                    option.style.color = '';
                    option.title = '';
                }
            }
        }
        
        // If current selection is not valid for production mode, reset selection
        if (isProduction && selectedOption && selectedOption.dataset.producible === 'false') {
            storageIdSelect.value = '';
        }
        
        // Toggle storage-only fields and production date display
        document.querySelectorAll('.storage-only').forEach(el => el.style.display = isProduction ? 'none' : 'block');
        const prodDiv = document.getElementById('production_dates');
        if (prodDiv) prodDiv.style.display = isProduction ? 'block' : 'none';
        // Ensure expiration_date required state changes with mode
        if (expirationInput) {
            if (isProduction) {
                expirationInput.removeAttribute('required');
            } else {
                expirationInput.setAttribute('required', '');
            }
        }
        
        // Update labels
        document.querySelector('label[for="start_date"]').textContent = 
            isProduction ? '생산 시작일:' : '보관 시작일:';
        // expiration label only shown in storage mode; production shows min/max inputs
        const expLabel = document.querySelector('label[for="expiration_date"]');
        if (expLabel) expLabel.textContent = isProduction ? '' : '보관 기한:';
        
        if (startDateInput.value) {
            updateEndDateConstraints();
        }
    }
    
    // Set today as the min date for start_date
    const today = new Date();
    startDateInput.min = formatDate(today);
    
    // Event listeners
    modeStorage.addEventListener('change', updateFormForMode);
    modeProduction.addEventListener('change', updateFormForMode);
    storageIdSelect.addEventListener('change', updateFormForMode);
    startDateInput.addEventListener('change', updateEndDateConstraints);
    
    // Initialize form state
    updateFormForMode();
});