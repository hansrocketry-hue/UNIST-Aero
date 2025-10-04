const availableLanguages = ['kor', 'eng', 'jpn', 'rus'];

function createDynamicLanguageFields(fieldId, fieldName, placeholder) {
    let usedLanguages = [];

    function addField() {
        const container = document.getElementById(fieldId);
        const remainingLanguages = availableLanguages.filter(l => !usedLanguages.includes(l));

        if (remainingLanguages.length === 0) {
            alert("모든 언어를 추가했습니다.");
            return;
        }

        const entry = document.createElement('div');
        entry.className = 'lang-entry';

        const langSelect = document.createElement('select');
        langSelect.name = fieldName + '_codes';
        remainingLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang.toUpperCase();
            langSelect.appendChild(option);
        });

        const textInput = document.createElement('input');
        textInput.type = 'text';
        textInput.name = fieldName + '_names';
        textInput.placeholder = placeholder;
        textInput.required = true;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.textContent = '삭제';
        removeBtn.onclick = function() {
            const selectedLang = entry.querySelector('select').value;
            const index = usedLanguages.indexOf(selectedLang);
            if (index > -1) {
                usedLanguages.splice(index, 1);
            }
            container.removeChild(entry);
        };

        entry.appendChild(langSelect);
        entry.appendChild(textInput);
        entry.appendChild(removeBtn);
        container.appendChild(entry);

        usedLanguages.push(langSelect.value);

        langSelect.addEventListener('change', (e) => {
            const newLang = e.target.value;
            const oldLang = e.target.getAttribute('data-old-lang');

            // Check if the new language is already used by another dropdown
            if (usedLanguages.includes(newLang)) {
                alert(`Language '${newLang.toUpperCase()}' is already in use.`);
                e.target.value = oldLang; // Revert the change
                return;
            }

            // Update usedLanguages array
            const index = usedLanguages.indexOf(oldLang);
            if (index > -1) {
                usedLanguages[index] = newLang;
            }
            e.target.setAttribute('data-old-lang', newLang);
        });
        langSelect.setAttribute('data-old-lang', langSelect.value);
    }

    // Add initial field
    addField();

    // Return the function to be used by a button
    return addField;
}
