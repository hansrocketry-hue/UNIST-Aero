# ID 구조 업데이트 완료 보고서

## 작업 개요
dish.json과 ingredient.json의 ID를 구분하기 위해 prefix를 추가하고, 모든 관련 코드를 업데이트했습니다.

## ID 구조
- **Ingredient IDs**: `"i"` prefix (예: `"i1"`, `"i2"`, `"i10"`)
- **Dish IDs**: `"d"` prefix (예: `"d1"`, `"d2"`, `"d32"`)

## 데이터 구조 확인 결과

### ✅ 현재 상태
1. **ingredient.json** - "i" prefix 적용 완료
2. **dish.json** - "d" prefix 적용 완료
3. **storaged-ingredient.json** - storage-id에 "i" prefix 사용 중
4. **dish.json의 required_ingredients** - 새로운 구조 사용 중:
   ```json
   {
     "type": "ingredient" or "dish",
     "id": "i1" or "d1",
     "amount_g": 100.0
   }
   ```

## 수정된 파일 목록

### 1. 스크립트 파일
- **scripts/smoke_test_add_dish.py**
  - 테스트 데이터의 ID를 숫자에서 문자열로 변경 (1 → "i1", 10 → "i10")

### 2. 라우트 핸들러 (app/routes/)

#### add_data_routes.py
- **add_dish_route()**: 
  - `required_ingredient_ids` → `item_ids[]`로 변경
  - `required_ingredient_amounts` → `item_amounts[]`로 변경
  - `item_types[]` 추가하여 ingredient/dish 구분
  - `int()` 변환 제거
  - `all_dishes` 변수 추가하여 템플릿에 전달

- **add_storaged_ingredient_route()**:
  - storage_id의 `int()` 변환 제거

#### edit_data_routes.py
- **edit_ingredient_route()**: route decorator에서 `<int:ingredient_id>` → `<ingredient_id>`
- **edit_ingredient_submit()**: route decorator에서 `<int:ingredient_id>` → `<ingredient_id>`
- **edit_dish_route()**: route decorator에서 `<int:dish_id>` → `<dish_id>`
- **edit_dish_submit()**: 
  - route decorator에서 `<int:dish_id>` → `<dish_id>`
  - item ID의 `int()` 변환 제거
  - 누락된 `name` 변수 추가

#### visualize_routes.py
- **ingredient_detail()**: route decorator에서 `<int:ingredient_id>` → `<ingredient_id>`
- **dish_detail()**: route decorator에서 `<int:dish_id>` → `<dish_id>`

#### home_routes.py
- **add_intake()**: 
  - dish ID 비교 시 `int()` 변환 제거
  - intake 기록 저장 시 `int()` 변환 제거
  - 누락된 `if request.method == 'POST':` 블록 추가

### 3. HTML 템플릿 (app/templates/)

#### add_dish_form.html
- **재료 선택 부분 개선**:
  - ingredient만 선택 가능 → ingredient와 dish 모두 선택 가능하도록 변경
  - `<optgroup>`으로 Ingredients와 Dishes 구분
  - `data-type` 속성 추가하여 type 정보 저장
  - hidden input 필드명 변경:
    - `required_ingredient_ids` → `item_ids[]`
    - `required_ingredient_amounts` → `item_amounts[]`
    - `item_types[]` 추가

- **JavaScript 수정**:
  - `data-type` 속성을 읽어 type 정보 저장
  - 3개의 hidden input (type, id, amount) 생성

#### edit_dish_form.html
- 이미 올바른 구조로 되어 있음 (확인 완료)
- ingredient와 dish 모두 선택 가능
- type, id, amount 정보 모두 포함

## 데이터 생성/수정 페이지 검증

### ✅ Dish 생성 페이지 (add_dish_form.html)
- [x] ingredient와 dish 모두 선택 가능
- [x] type 정보 포함
- [x] id를 문자열로 처리
- [x] amount_g 정보 포함

### ✅ Dish 수정 페이지 (edit_dish_form.html)
- [x] ingredient와 dish 모두 선택 가능
- [x] type 정보 포함
- [x] id를 문자열로 처리
- [x] amount_g 정보 포함
- [x] 기존 데이터 올바르게 표시

### ✅ Ingredient 생성 페이지
- [x] 새로운 ID 형식으로 자동 생성 (database_handler.py의 _get_next_id 사용)

### ✅ Ingredient 수정 페이지
- [x] 문자열 ID 처리

### ✅ Storaged Ingredient 생성 페이지
- [x] storage-id를 문자열로 처리

## 핵심 변경 사항

### 1. ID 타입 변경
- **이전**: 숫자 (1, 2, 3, ...)
- **이후**: 문자열 ("i1", "i2", "d1", "d2", ...)

### 2. required_ingredients 구조 변경
- **이전**: 
  ```json
  {
    "id": 1,
    "amount_g": 100.0
  }
  ```
- **이후**:
  ```json
  {
    "type": "ingredient",
    "id": "i1",
    "amount_g": 100.0
  }
  ```

### 3. Route Parameter 타입 변경
- **이전**: `@bp.route('/dish/<int:dish_id>')`
- **이후**: `@bp.route('/dish/<dish_id>')`

## 테스트 권장 사항

1. **Dish 생성 테스트**
   - ingredient만 사용하는 dish 생성
   - dish를 포함하는 dish 생성 (복합 요리)
   - ingredient와 dish 혼합 사용

2. **Dish 수정 테스트**
   - 기존 dish의 required_ingredients 수정
   - type 변경 (ingredient ↔ dish)

3. **Storaged Ingredient 생성 테스트**
   - 새로운 ID 형식으로 storage-id 입력

4. **데이터 조회 테스트**
   - ingredient 상세 페이지
   - dish 상세 페이지
   - 관련 항목 링크 동작 확인

## 호환성

### ✅ 하위 호환성
- database_handler.py는 이미 문자열 ID를 지원하도록 구현되어 있음
- HTML 템플릿의 `{{ item.id }}`는 숫자와 문자열 모두 처리 가능

### ⚠️ 주의사항
- 기존 데이터베이스에 숫자 ID가 있다면 마이그레이션 필요
- 외부 시스템과의 연동이 있다면 ID 형식 변경 확인 필요

## 완료 일시
2025-10-05 21:10 (KST)
