# Storaged Ingredient 시각화 로직 문서
# 작성일: 2025년 10월 5일

## 1. 개요
이 문서는 storaged ingredient의 시각화 로직, 특히 게이지 바 계산 방식을 설명합니다.

## 2. 데이터 구조
### 입력 데이터
- storaged-ingredient 테이블의 각 항목:
  - storage-id: 식재료 ID
  - mode: 'production' 또는 'storage'
  - start_date: 시작일
  - mass_g: 질량(g)
  - 생산 모드인 경우:
    - min_end_date: 최소 예상 완료일
    - max_end_date: 최대 예상 완료일
  - 저장 모드인 경우:
    - expiration_date: 유통기한
    - shelf_life: 보관 수명 (문자열, 예: "1 year 2 months 3 days")

### 출력 데이터
- 생산 모드:
  ```python
  {
      'name': str,              # 식재료 한글 이름
      'mass_g': float,          # 질량(g)
      'start_date': str,        # YYYY-MM-DD
      'is_production': True,    # 생산 모드 표시
      'grey_width': float,      # 미래 시작 구간 너비(%)
      'green_left': float,      # 진행 바 시작 위치(%)
      'green_width': float,     # 진행 바 너비(%)
      'expected_left': float,   # 예상 구간 시작 위치(%)
      'expected_width': float,  # 예상 구간 너비(%)
      'today_pos': float,       # 현재 날짜 위치(%)
      'start_pos': float,       # 시작일 위치(%)
      'min_end_date': str,      # YYYY-MM-DD
      'max_end_date': str       # YYYY-MM-DD
  }
  ```

- 저장 모드:
  ```python
  {
      'name': str,              # 식재료 한글 이름
      'mass_g': float,          # 질량(g)
      'start_date': str,        # YYYY-MM-DD
      'is_production': False,   # 저장 모드 표시
      'current_progress': float,# 진행률(%)
      'expiration_date': str    # YYYY-MM-DD
  }
  ```

## 3. 게이지 계산 로직

### 3.1 생산 모드
1. 기준점 설정
   - bar_start = min(start_date, today)
   - bar_end = max_end_date
   - span_days = (bar_end - bar_start).days

2. 날짜 오프셋 계산
   ```python
   def pct(days):
       return max(0.0, min(100.0, (days / span_days) * 100.0))
   
   start_offset = (start_date - bar_start).days
   today_offset = (today - bar_start).days
   min_offset = (min_end_date - bar_start).days
   max_offset = (max_end_date - bar_start).days
   ```

3. 구간별 계산
   - 회색 구간 (미래 시작)
     ```python
     grey_width = pct(start_offset - today_offset) if start_date > today else 0
     ```
   
   - 초록색 구간 (현재 진행)
     ```python
     green_left = pct(start_offset) if start_offset >= 0 else 0
     if today >= start_date:
         current_time = min(today, max_end_date)
         current_offset = (current_time - bar_start).days
         green_width = pct(max(0, current_offset - start_offset))
     ```
   
   - 하늘색 구간 (예상 범위)
     ```python
     expected_left = pct(min_offset)
     expected_width = pct(max_offset - min_offset)
     ```

### 3.2 저장 모드
1. 유통기한 계산
   - expiration_date가 직접 제공되거나
   - shelf_life 문자열에서 계산 (정규식으로 년/월/일 추출)

2. 진행률 계산
   ```python
   total_duration = (expiration_date - start_date).days
   current_time = min(today, expiration_date)
   current_time = max(current_time, start_date)
   current_progress = ((current_time - start_date).days / total_duration) * 100
   ```

## 4. 템플릿 렌더링
- 생산 모드
  - 회색 영역: 시작 전 구간
  - 초록색 영역: 현재까지 진행
  - 하늘색 영역: 예상 생산 구간
- 저장 모드
  - 빨간색 영역: 저장 진행률

## 5. 주의사항
1. 날짜 유효성 검증 필수
2. 음수 기간 체크 (continue로 처리)
3. 진행률 0-100% 범위 제한

## 6. 예시 시나리오

### 6.1 생산 모드
1. 미래 시작
   - today < start_date:
     - 회색 구간: today~start_date
     - 하늘색 구간: min~max

2. 생산 중
   - start_date ≤ today:
     - 초록색 구간: start_date~today
     - 하늘색 구간: min~max

### 6.2 저장 모드
- 단순 진행률: (현재 - 시작) / (유통기한 - 시작)
- 시작 전이면 0%, 유통기한 지나면 100%