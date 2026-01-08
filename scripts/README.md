# Scripts

이 디렉토리에는 Online Judge 개발 환경을 관리하는 유틸리티 스크립트들이 있습니다.

## 사용 가능한 스크립트

### start.sh
개발 환경의 모든 서비스를 시작합니다.

```bash
./scripts/start.sh
```

실행 내용:
- Docker 이미지 빌드
- PostgreSQL, Redis, Backend, Frontend 컨테이너 시작
- 서비스 상태 확인 및 접속 정보 표시

### stop.sh
모든 서비스를 중지하고 컨테이너를 제거합니다.

```bash
./scripts/stop.sh
```

### restart.sh
모든 서비스를 재시작합니다 (stop → start).

```bash
./scripts/restart.sh
```

코드 변경 후 전체 환경을 리셋할 때 유용합니다.

### logs.sh
서비스 로그를 실시간으로 확인합니다.

```bash
# 모든 서비스 로그 보기
./scripts/logs.sh

# 특정 서비스 로그만 보기
./scripts/logs.sh oj-backend-dev
./scripts/logs.sh oj-frontend-dev
./scripts/logs.sh oj-postgres-dev
./scripts/logs.sh oj-redis-dev
```

종료: `Ctrl+C`

## 빠른 시작

```bash
# 1. 서비스 시작
./scripts/start.sh

# 2. 브라우저에서 확인
# - http://localhost:8080 (사용자 페이지)
# - http://localhost:8080/admin (관리자 페이지)

# 3. 로그 확인
./scripts/logs.sh

# 4. 종료
./scripts/stop.sh
```

## 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# 기존 컨테이너 확인 및 제거
docker ps -a
docker rm -f oj-backend-dev oj-frontend-dev oj-postgres-dev oj-redis-dev
```

### 데이터 초기화가 필요한 경우
```bash
# 주의: 모든 데이터가 삭제됩니다
./scripts/stop.sh
rm -rf data/ backend/data/
./scripts/start.sh
```

### 권한 오류
```bash
chmod +x scripts/*.sh
```
