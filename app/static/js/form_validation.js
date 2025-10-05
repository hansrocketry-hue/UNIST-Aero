/**
 * 폼 유효성 검사 관련 JavaScript
 */

// 연구 자료 폼 유효성 검사
function validateResearchForm() {
    const form = document.getElementById('researchForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        const title = document.getElementById('title').value.trim();
        const authors = document.getElementById('authors').value.trim();
        const year = document.getElementById('year').value.trim();
        const summaryKor = document.getElementById('summary_kor').value.trim();
        const summaryEng = document.getElementById('summary_eng').value.trim();

        let isValid = true;
        let errorMessage = '';

        if (!title) {
            errorMessage += '제목을 입력해주세요.\n';
            isValid = false;
        }

        if (!authors) {
            errorMessage += '저자를 입력해주세요.\n';
            isValid = false;
        }

        if (!year) {
            errorMessage += '출판년도를 입력해주세요.\n';
            isValid = false;
        } else if (!/^\d{4}$/.test(year)) {
            errorMessage += '출판년도는 4자리 숫자로 입력해주세요.\n';
            isValid = false;
        }

        if (!summaryKor) {
            errorMessage += '한글 요약을 입력해주세요.\n';
            isValid = false;
        }

        if (!summaryEng) {
            errorMessage += '영문 요약을 입력해주세요.\n';
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            alert(errorMessage);
        }
    });
}

// 식재료 폼 유효성 검사
function validateIngredientForm() {
    const form = document.getElementById('ingredientForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        const nameKor = document.getElementById('name_kor').value.trim();
        const nameEng = document.getElementById('name_eng').value.trim();
        const producible = document.getElementById('producible').checked;
        
        let isValid = true;
        let errorMessage = '';

        if (!nameKor) {
            errorMessage += '한글 이름을 입력해주세요.\n';
            isValid = false;
        }

        if (!nameEng) {
            errorMessage += '영문 이름을 입력해주세요.\n';
            isValid = false;
        }

        // 생산 가능 체크 시 관련 필드 검사
        if (producible) {
            const minTime = document.getElementById('min_time').value;
            const maxTime = document.getElementById('max_time').value;

            if (!minTime) {
                errorMessage += '최소 생산 시간을 입력해주세요.\n';
                isValid = false;
            }

            if (!maxTime) {
                errorMessage += '최대 생산 시간을 입력해주세요.\n';
                isValid = false;
            }

            if (Number(minTime) > Number(maxTime)) {
                errorMessage += '최소 생산 시간은 최대 생산 시간보다 작아야 합니다.\n';
                isValid = false;
            }
        }

        // 영양 정보 유효성 검사
        const nutritionInputs = document.querySelectorAll('input[name^="nutrition_"]');
        nutritionInputs.forEach(input => {
            if (input.value && Number(input.value) < 0) {
                errorMessage += '영양 정보는 음수가 될 수 없습니다.\n';
                isValid = false;
            }
        });

        if (!isValid) {
            e.preventDefault();
            alert(errorMessage);
        }
    });
}

// 조리 방법 폼 유효성 검사
function validateCookingMethodForm() {
    const form = document.getElementById('cookingMethodForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        const nameKor = document.getElementById('name_kor').value.trim();
        const nameEng = document.getElementById('name_eng').value.trim();
        const descriptionKor = document.getElementById('description_kor').value.trim();
        const descriptionEng = document.getElementById('description_eng').value.trim();

        let isValid = true;
        let errorMessage = '';

        if (!nameKor) {
            errorMessage += '한글 이름을 입력해주세요.\n';
            isValid = false;
        }

        if (!nameEng) {
            errorMessage += '영문 이름을 입력해주세요.\n';
            isValid = false;
        }

        if (!descriptionKor) {
            errorMessage += '한글 설명을 입력해주세요.\n';
            isValid = false;
        }

        if (!descriptionEng) {
            errorMessage += '영문 설명을 입력해주세요.\n';
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            alert(errorMessage);
        }
    });
}

// 요리 폼 유효성 검사
function validateDishForm() {
    const form = document.getElementById('dishForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        const nameKor = document.getElementById('name_kor').value.trim();
        const nameEng = document.getElementById('name_eng').value.trim();
        const ingredientRows = document.querySelectorAll('.ingredient-row');
        const cookingMethodIds = document.querySelectorAll('input[name="cooking_method_ids[]"]:checked');
        const instructionsKor = document.getElementById('instructions_kor').value.trim();
        const instructionsEng = document.getElementById('instructions_eng').value.trim();

        let isValid = true;
        let errorMessage = '';

        if (!nameKor) {
            errorMessage += '한글 이름을 입력해주세요.\n';
            isValid = false;
        }

        if (!nameEng) {
            errorMessage += '영문 이름을 입력해주세요.\n';
            isValid = false;
        }

        // 재료 검사
        if (ingredientRows.length === 0) {
            errorMessage += '최소 하나의 재료를 추가해주세요.\n';
            isValid = false;
        }

        ingredientRows.forEach((row, index) => {
            const select = row.querySelector('.ingredient-select');
            const amount = row.querySelector('input[name="ingredient_amounts[]"]');

            if (!select.value) {
                errorMessage += `${index + 1}번째 재료를 선택해주세요.\n`;
                isValid = false;
            }

            if (!amount.value || amount.value <= 0) {
                errorMessage += `${index + 1}번째 재료의 양을 올바르게 입력해주세요.\n`;
                isValid = false;
            }
        });

        // 조리 방법 검사
        if (cookingMethodIds.length === 0) {
            errorMessage += '최소 하나의 조리 방법을 선택해주세요.\n';
            isValid = false;
        }

        // 조리 설명 검사
        if (!instructionsKor) {
            errorMessage += '한글 조리 설명을 입력해주세요.\n';
            isValid = false;
        }

        if (!instructionsEng) {
            errorMessage += '영문 조리 설명을 입력해주세요.\n';
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            alert(errorMessage);
        }
    });
}

// 모든 폼 초기화
document.addEventListener('DOMContentLoaded', function() {
    validateResearchForm();
    validateIngredientForm();
    validateCookingMethodForm();
    validateDishForm();
});