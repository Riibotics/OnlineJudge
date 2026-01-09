# 데이터 영속성 가이드 (Data Persistence Guide)

## 개요

이 프로젝트는 Docker Named Volume을 사용하여 컨테이너가 삭제되거나 재생성되어도 데이터가 유지되도록 설정되어 있습니다.

## Named Volume 목록

### 1. `oj-postgres-data`
- **용도**: PostgreSQL 데이터베이스 데이터
- **저장 내용**: 모든 사용자, 문제, 제출 기록 등의 데이터베이스 데이터
- **중요도**: ⚠️ 매우 높음 - 삭제 시 모든 데이터 손실

### 2. `oj-redis-data`
- **용도**: Redis 캐시 및 세션 데이터
- **저장 내용**: 세션 정보, 캐시된 데이터
- **중요도**: 중간 - 삭제 시 재생성 가능하지만 사용자 로그아웃 발생

### 3. `oj-backend-data`
- **용도**: 백엔드 애플리케이션 데이터
- **저장 내용**: 업로드된 파일, 설정 파일 등
- **중요도**: 높음

### 4. `oj-backend-logs`
- **용도**: 애플리케이션 로그
- **저장 내용**: 백엔드 로그 파일
- **중요도**: 낮음 - 디버깅 목적

## 로컬 마운트 디렉토리

다음 디렉토리는 로컬 파일 시스템에 직접 마운트되어 쉽게 접근 가능합니다:

- `./backend/data/test_case` → 테스트 케이스 파일
- `./backend/data/public` → 공개 파일 (아바타 이미지 등)

## 사용 방법

### 컨테이너 재시작 (데이터 유지됨)
```bash
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

### 컨테이너 완전 삭제 후 재생성 (데이터 유지됨)
```bash
docker-compose -f docker-compose.dev.yml down
docker rm -f oj-backend-dev oj-postgres-dev oj-redis-dev oj-frontend-dev
docker-compose -f docker-compose.dev.yml up -d
```

### 볼륨 목록 확인
```bash
docker volume ls | grep oj-
```

### 특정 볼륨 상세 정보 확인
```bash
docker volume inspect onlinejudge_oj-postgres-data
```

### 볼륨 백업

#### PostgreSQL 데이터베이스 백업
```bash
# 백업 생성
docker exec oj-postgres-dev pg_dump -U onlinejudge onlinejudge > backup_$(date +%Y%m%d_%H%M%S).sql

# 백업 복원
docker exec -i oj-postgres-dev psql -U onlinejudge onlinejudge < backup_20260109_120000.sql
```

#### 볼륨 직접 백업
```bash
# 볼륨을 tar 파일로 백업
docker run --rm -v onlinejudge_oj-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-data-backup.tar.gz -C /data .

# 백업에서 복원
docker run --rm -v onlinejudge_oj-postgres-data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-data-backup.tar.gz -C /data
```

### 볼륨 완전 삭제 (주의!)

⚠️ **경고**: 다음 명령어는 모든 데이터를 영구적으로 삭제합니다!

```bash
# 컨테이너 중지 및 삭제
docker-compose -f docker-compose.dev.yml down

# 볼륨까지 삭제 (데이터 완전 삭제)
docker-compose -f docker-compose.dev.yml down -v

# 또는 개별 볼륨 삭제
docker volume rm onlinejudge_oj-postgres-data
docker volume rm onlinejudge_oj-redis-data
docker volume rm onlinejudge_oj-backend-data
docker volume rm onlinejudge_oj-backend-logs
```

## 기존 데이터 마이그레이션

기존 `./backend/data/` 디렉토리에 데이터가 있다면 다음과 같이 마이그레이션할 수 있습니다:

### PostgreSQL 데이터 마이그레이션
```bash
# 1. 새 컨테이너 시작
docker-compose -f docker-compose.dev.yml up -d oj-postgres

# 2. 기존 데이터를 새 볼륨으로 복사
docker cp ./backend/data/postgres/. oj-postgres-dev:/var/lib/postgresql/data/

# 3. 권한 수정
docker exec oj-postgres-dev chown -R postgres:postgres /var/lib/postgresql/data

# 4. 컨테이너 재시작
docker-compose -f docker-compose.dev.yml restart oj-postgres
```

### Redis 데이터 마이그레이션
```bash
# 1. 새 컨테이너 시작
docker-compose -f docker-compose.dev.yml up -d oj-redis

# 2. 기존 데이터 복사
docker cp ./backend/data/redis/. oj-redis-dev:/data/

# 3. 컨테이너 재시작
docker-compose -f docker-compose.dev.yml restart oj-redis
```

## 볼륨 저장 위치

Docker Named Volume은 다음 위치에 저장됩니다:

- **macOS**: `/var/lib/docker/volumes/` (Docker Desktop VM 내부)
- **Linux**: `/var/lib/docker/volumes/`
- **Windows**: `\\wsl$\docker-desktop-data\version-pack-data\community\docker\volumes\`

## 모범 사례

1. **정기 백업**: 중요한 데이터는 정기적으로 백업하세요
2. **백업 테스트**: 백업된 데이터가 정상적으로 복원되는지 테스트하세요
3. **볼륨 모니터링**: 볼륨 크기를 주기적으로 확인하세요
   ```bash
   docker system df -v
   ```
4. **로그 관리**: 로그 볼륨이 너무 커지지 않도록 주기적으로 정리하세요

## 트러블슈팅

### 데이터가 여전히 사라지는 경우

1. Named Volume이 제대로 생성되었는지 확인:
   ```bash
   docker volume ls | grep oj-
   ```

2. 컨테이너가 올바른 볼륨을 마운트했는지 확인:
   ```bash
   docker inspect oj-postgres-dev | grep -A 10 Mounts
   ```

3. 볼륨을 강제로 삭제하는 명령어(`-v` 옵션)를 사용하지 않았는지 확인

### 기존 데이터와 충돌

새로운 Named Volume을 사용할 때 기존 데이터와 충돌이 발생할 수 있습니다. 이 경우 위의 "기존 데이터 마이그레이션" 섹션을 참고하여 데이터를 이전하세요.

## 추가 정보

- [Docker Volume 공식 문서](https://docs.docker.com/storage/volumes/)
- [Docker Compose Volume 설정](https://docs.docker.com/compose/compose-file/compose-file-v3/#volumes)
