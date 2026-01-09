# Online Judge 보안 강화 구현 완료

## 구현된 변경사항

### 1. 데이터베이스 변경사항

#### User 모델 수정 ([account/models.py](account/models.py))
- `is_approved` 필드 추가: 관리자의 계정 승인 여부를 추적

#### 마이그레이션 파일 생성
- `0013_user_is_approved.py`: is_approved 필드 추가
- `0014_approve_existing_admins.py`: 기존 관리자 계정 자동 승인

### 2. 문제(Problem) 접근 제어

#### [problem/views/oj.py](problem/views/oj.py) 수정
다음 API에 로그인 및 승인 체크 추가:
- `ProblemTagAPI`: 문제 태그 조회
- `PickOneAPI`: 랜덤 문제 선택
- `ProblemAPI`: 문제 목록 및 상세 조회

**동작**: 로그인하지 않았거나 승인되지 않은 사용자는 문제를 볼 수 없음 (관리자 제외)

### 3. 회원가입 프로세스 수정

#### [account/views/oj.py](account/views/oj.py) 수정

**UserRegisterAPI**:
- 새로 가입한 사용자는 `is_approved=False`로 설정
- 성공 메시지 변경: "관리자 승인을 기다려주세요"

**UserLoginAPI**:
- 로그인 시 승인되지 않은 계정 체크 추가
- 승인되지 않은 사용자는 로그인 후에도 컨텐츠 접근 불가

### 4. Submission(제출) 접근 제어

#### [submission/views/oj.py](submission/views/oj.py) 수정
다음 API에 승인 체크 추가:
- `SubmissionAPI.post()`: 제출 생성
- `SubmissionAPI.get()`: 제출 조회
- `SubmissionAPI.put()`: 제출 공유
- `SubmissionListAPI.get()`: 제출 목록

### 5. Contest(대회) 접근 제어

#### [contest/views/oj.py](contest/views/oj.py) 수정
다음 API에 승인 체크 추가:
- `ContestAPI.get()`: 대회 상세 조회
- `ContestListAPI.get()`: 대회 목록
- `ContestPasswordVerifyAPI.post()`: 대회 비밀번호 확인
- `ContestAccessAPI.get()`: 대회 접근 권한 확인

#### [account/decorators.py](account/decorators.py) 수정
- `check_contest_permission` 데코레이터에 승인 체크 추가
- Contest 관련 모든 protected API에 자동 적용

### 6. Admin 기능 추가

#### [account/serializers.py](account/serializers.py) 수정
다음 Serializer에 `is_approved` 필드 추가:
- `UserAdminSerializer`
- `UserSerializer`
- `EditUserSerializer`

#### [account/views/admin.py](account/views/admin.py) 수정

**UserAdminAPI.put()**:
- 관리자가 사용자 편집 시 `is_approved` 필드 업데이트 가능

**UserAdminAPI.post() (Import User)**:
- 관리자가 import하는 사용자는 자동 승인 (`is_approved=True`)

**GenerateUserAPI.post()**:
- 관리자가 생성하는 사용자는 자동 승인 (`is_approved=True`)

## 적용 방법

### 1. 데이터베이스 마이그레이션 실행

```bash
cd /Users/jinyongjeong/git/OnlineJudge
python manage.py migrate
```

### 2. 변경사항 확인

마이그레이션 실행 후:
- 기존 관리자 계정은 자동으로 승인됨
- 새로 가입하는 사용자는 승인 대기 상태가 됨
- 관리자는 Admin 페이지에서 사용자의 `is_approved` 필드를 수정하여 승인 가능

## 주요 보안 개선사항

### ✅ 요구사항 1: 로그인 필수
- 모든 Problem, Contest, Submission API에 `@login_required` 데코레이터 추가
- 비로그인 사용자는 홈 화면과 Announcement만 볼 수 있음

### ✅ 요구사항 2: 관리자 승인 시스템
- 회원가입 후 자동으로 `is_approved=False` 설정
- 로그인은 가능하지만 컨텐츠 접근 불가
- 관리자만 사용자 승인 가능
- 관리자가 직접 생성하는 계정은 자동 승인

## 관리자 역할

승인되지 않은 사용자(is_approved=False)도 다음과 같은 경우 제한 없이 접근 가능:
- Admin 또는 Super Admin 권한을 가진 경우 (`user.is_admin_role()`)

## 참고사항

- Announcement(공지사항)는 로그인 없이도 접근 가능 (홈 화면)
- 관리자 페이지 (/admin)는 기존과 동일하게 관리자만 접근 가능
- 승인되지 않은 사용자가 API를 호출하면 명확한 에러 메시지 반환:
  ```
  "Your account is not approved yet. Please wait for admin approval."
  ```
