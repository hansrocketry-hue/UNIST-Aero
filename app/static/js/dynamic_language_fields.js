const availableLanguages = ['kor', 'eng', 'jpn', 'rus'];

/**
 * Create dynamic multilingual input fields with optional initial values.
 * initialValues: optional array of objects: [{code: 'kor', value: '쌀'}, ...]
 */
function createDynamicLanguageFields(fieldId, fieldName, placeholder, initialValues) {
    let usedLanguages = [];

    function createEntry(selectedLang, textValue) {
        const container = document.getElementById(fieldId);
        const entry = document.createElement('div');
        entry.className = 'lang-entry';

        const langSelect = document.createElement('select');
        langSelect.name = fieldName + '_codes';
        // Build options including already used languages — we'll prevent duplicates
        availableLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang.toUpperCase();
            if (lang === selectedLang) option.selected = true;
            langSelect.appendChild(option);
        });

        const textInput = document.createElement('input');
        textInput.type = 'text';
        textInput.name = fieldName + '_names';
        textInput.placeholder = placeholder;
        textInput.required = true;
        if (textValue) textInput.value = textValue;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.textContent = '삭제';
        removeBtn.onclick = function() {
            const selected = entry.querySelector('select').value;
            const index = usedLanguages.indexOf(selected);
            if (index > -1) usedLanguages.splice(index, 1);
            container.removeChild(entry);
        };

        entry.appendChild(langSelect);
        entry.appendChild(textInput);
        entry.appendChild(removeBtn);
        container.appendChild(entry);

        // Track used language and prevent duplicates via change handler
        usedLanguages.push(langSelect.value);
        langSelect.addEventListener('change', (e) => {
            const newLang = e.target.value;
            const oldLang = e.target.getAttribute('data-old-lang');
            if (newLang === oldLang) return;
            if (usedLanguages.includes(newLang)) {
                alert(`Language '${newLang.toUpperCase()}' is already in use.`);
                e.target.value = oldLang;
                return;
            }
            const idx = usedLanguages.indexOf(oldLang);
            if (idx > -1) usedLanguages[idx] = newLang;
            e.target.setAttribute('data-old-lang', newLang);
        });
        langSelect.setAttribute('data-old-lang', langSelect.value);
    }

    function addField() {
        // Find a language not already used
        const remaining = availableLanguages.filter(l => !usedLanguages.includes(l));
        if (remaining.length === 0) {
            alert('모든 언어를 추가했습니다.');
            return;
        }
        createEntry(remaining[0], '');
    }

    // If initialValues provided, render them first
    if (Array.isArray(initialValues) && initialValues.length > 0) {
        initialValues.forEach(it => {
            // Only add if code is valid and not already used
            if (!it || !it.code) return;
            if (usedLanguages.includes(it.code)) return;
            if (!availableLanguages.includes(it.code)) return;
            createEntry(it.code, it.value || '');
        });
    } else {
        // Default: add one empty field
        addField();
    }

    return addField;
}
