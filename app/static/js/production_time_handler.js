document.addEventListener('DOMContentLoaded', function() {
    const storageIdSelect = document.getElementById('storage_id');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const modeStorage = document.getElementById('mode_storage');
    const modeProduction = document.getElementById('mode_production');
    
    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    function updateEndDateConstraints() {
        const selectedOption = storageIdSelect.options[storageIdSelect.selectedIndex];
        const isProduction = modeProduction.checked;
        const startDate = new Date(startDateInput.value);
        
        if (isProduction) {
            const minTime = parseInt(selectedOption.dataset.minTime);
            const maxTime = parseInt(selectedOption.dataset.maxTime);
            
            if (minTime && maxTime) {
                const minEndDate = new Date(startDate);
                minEndDate.setDate(startDate.getDate() + minTime);
                
                const maxEndDate = new Date(startDate);
                maxEndDate.setDate(startDate.getDate() + maxTime);
                
                endDateInput.min = formatDate(minEndDate);
                endDateInput.max = formatDate(maxEndDate);
                
                // Add or update helper text
                const helperText = document.getElementById('end-date-helper');
                if (!helperText) {
                    const helper = document.createElement('small');
                    helper.id = 'end-date-helper';
                    helper.style.display = 'block';
                    helper.style.marginTop = '5px';
                    endDateInput.parentNode.insertBefore(helper, endDateInput.nextSibling);
                }
                helperText.textContent = `생산 기간: ${minTime}~${maxTime}일 (${formatDate(minEndDate)} ~ ${formatDate(maxEndDate)})`;
            }
        } else {
            // For storage mode, end date should be same as start date
            endDateInput.value = startDateInput.value;
            endDateInput.disabled = true;
            
            // Remove helper text if exists
            const helperText = document.getElementById('end-date-helper');
            if (helperText) {
                helperText.remove();
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
        
        // Update end date field
        endDateInput.disabled = !isProduction;
        if (!isProduction && startDateInput.value) {
            endDateInput.value = startDateInput.value;
        }
        
        // Update labels
        document.querySelector('label[for="start_date"]').textContent = 
            isProduction ? '생산 시작일:' : '보관 시작일:';
        document.querySelector('label[for="end_date"]').textContent = 
            isProduction ? '생산 종료일:' : '보관 시작일:';
        
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