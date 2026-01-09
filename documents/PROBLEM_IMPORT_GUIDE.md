# Problem Import 가이드

## 개요
Admin 페이지에서 문제를 ZIP 파일로 import하는 기능이 수정되었습니다.

## 수정 내용

### 1. 상세한 에러 로깅
- 모든 단계에서 상세한 로그가 기록됩니다
- 어느 단계에서 실패했는지 명확하게 파악 가능

### 2. 개선된 에러 메시지
- 구체적인 에러 원인을 표시
- 문제 해결을 위한 힌트 제공

### 3. 디렉토리 권한 문제 해결
- TEST_CASE_DIR이 존재하지 않으면 자동 생성
- 디렉토리 생성 실패 시 명확한 에러 메시지

## ZIP 파일 구조

문제를 import하려면 다음과 같은 구조의 ZIP 파일이 필요합니다:

```
problem-export.zip
├── 1/
│   ├── problem.json          # 문제 메타데이터
│   └── testcase/
│       ├── 1.in              # 테스트 케이스 입력
│       ├── 1.out             # 테스트 케이스 출력
│       ├── 2.in
│       ├── 2.out
│       └── ...
├── 2/
│   ├── problem.json
│   └── testcase/
│       ├── 1.in
│       ├── 1.out
│       └── ...
└── ...
```

### problem.json 구조 예시

```json
{
    "display_id": "A-plus-B",
    "title": "A+B Problem",
    "description": {
        "format": "html",
        "value": "<p>Calculate A+B</p>"
    },
    "input_description": {
        "format": "html",
        "value": "<p>Two integers A and B</p>"
    },
    "output_description": {
        "format": "html",
        "value": "<p>A+B</p>"
    },
    "hint": {
        "format": "html",
        "value": "<p>Sample hint</p>"
    },
    "test_case_score": [
        {"score": 10},
        {"score": 10}
    ],
    "time_limit": 1000,
    "memory_limit": 256,
    "samples": [
        {
            "input": "1 2",
            "output": "3"
        }
    ],
    "template": {
        "Python3": {
            "prepend": "",
            "template": "# Write your code here",
            "append": ""
        }
    },
    "spj": null,
    "rule_type": "ACM",
    "source": "Test Contest",
    "answers": [],
    "tags": ["math", "easy"]
}
```

## 사용 방법

### 1. 문제 Export
기존 문제를 export하여 템플릿으로 사용할 수 있습니다:
1. Admin 페이지 → Problem Management
2. 문제 선택 → Export
3. ZIP 파일 다운로드

### 2. 문제 Import
1. Admin 페이지 → Problem Management
2. "Import Problem" 버튼 클릭
3. ZIP 파일 선택
4. Import 결과 확인

## 문제 해결

### 로그 확인 방법

Docker 컨테이너가 실행 중인 경우:
```bash
docker logs -f oj-backend-dev 2>&1 | grep -i import
```

### 일반적인 에러와 해결 방법

#### 1. "No problem.json file found in zip"
- **원인**: ZIP 파일에 `1/problem.json`, `2/problem.json` 형식의 파일이 없음
- **해결**: ZIP 파일 구조 확인

#### 2. "No test case files found"
- **원인**: `testcase/` 디렉토리에 `.in`, `.out` 파일이 없음
- **해결**: 테스트 케이스 파일 확인
  - ACM 모드: `1.in`, `1.out`, `2.in`, `2.out` ...
  - SPJ 모드: `1.in`, `2.in` ...

#### 3. "Failed to create test case directory"
- **원인**: 권한 문제 또는 디스크 공간 부족
- **해결**: 
  ```bash
  # 컨테이너 내부에서 권한 확인
  docker exec -it oj-backend-dev ls -la /data/test_case
  
  # 디스크 공간 확인
  docker exec -it oj-backend-dev df -h
  ```

#### 4. "Invalid JSON"
- **원인**: problem.json 파일 형식 오류
- **해결**: JSON 문법 검사 도구로 확인 (https://jsonlint.com/)

#### 5. "Unsupported language"
- **원인**: template에 시스템에서 지원하지 않는 언어가 포함됨
- **해결**: 지원되는 언어만 사용
  - Python3, C, C++, Java 등

### 디버깅 모드에서 테스트

```bash
# 컨테이너 재시작 (로그 확인 가능)
docker-compose -f docker-compose.dev.yml restart oj-backend

# 실시간 로그 모니터링
docker logs -f oj-backend-dev
```

## 데이터 확인

Import가 성공한 후:

```bash
# 문제 목록 확인
docker exec -it oj-postgres-dev psql -U onlinejudge -d onlinejudge -c "SELECT id, _id, title FROM problem;"

# 테스트 케이스 확인
docker exec -it oj-backend-dev ls -la /data/test_case/
```

## 수동 Import (개발용)

Python shell을 통한 수동 import:

```bash
docker exec -it oj-backend-dev python manage.py shell

# Python shell에서
from problem.views.admin import ImportProblemAPI
import logging
logging.basicConfig(level=logging.DEBUG)

# 파일 업로드 시뮬레이션
# (실제 사용 시에는 웹 인터페이스 사용 권장)
```

## 추가 정보

### Test Case 파일 명명 규칙
- **숫자로 시작**: `1.in`, `1.out`, `2.in`, `2.out` ...
- **자연스러운 정렬**: `1`, `2`, `3`, ..., `10`, `11` (문자열 정렬 아님)
- **짝을 맞춰야 함**: 모든 `.in` 파일에는 대응하는 `.out` 파일 필요 (SPJ 제외)

### 성능 고려사항
- 대용량 ZIP 파일 (>100MB): 업로드 시간이 오래 걸릴 수 있음
- 많은 문제 (>50개): 트랜잭션 타임아웃 가능
- 해결: 문제를 여러 ZIP 파일로 분할하여 import

## 지원

문제가 계속되면:
1. 로그 파일 확인
2. ZIP 파일 구조 재확인
3. GitHub Issue 생성
