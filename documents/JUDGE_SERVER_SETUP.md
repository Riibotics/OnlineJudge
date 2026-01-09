# Judge 서버 설정 가이드

## 문제 진단

현재 시스템에 **Judge 서버가 등록되지 않아** 코드 제출이 처리되지 않습니다.

### 확인된 문제점
1. Judge 서버가 등록되지 않음 (0개)
2. Judge 서버 토큰이 기본값("CHANGE_THIS")으로 설정됨

## 해결 방법

OnlineJudge는 백엔드와 별도로 Judge 서버를 실행해야 합니다.

### 방법 1: 공식 Judge 서버 사용 (권장)

#### 1. Judge 서버 Docker 이미지 실행

```bash
# Judge 서버 토큰 생성 (랜덤 문자열)
JUDGE_TOKEN=$(openssl rand -hex 32)
echo "Judge Server Token: $JUDGE_TOKEN"

# Judge 서버 실행
docker run -d \
  --name oj-judge-server \
  --restart always \
  --privileged \
  -p 127.0.0.1:12358:8080 \
  -e SERVICE_URL=http://oj-judge-server:8080 \
  -e BACKEND_URL=http://host.docker.internal:8000/api/judge_server_heartbeat/ \
  -e TOKEN=$JUDGE_TOKEN \
  registry.cn-hangzhou.aliyuncs.com/onlinejudge/judge_server
```

#### 2. 백엔드에 Judge 토큰 설정

[docker-compose.dev.yml](docker-compose.dev.yml) 파일 수정:

```yaml
oj-backend:
  environment:
    - JUDGE_SERVER_TOKEN=여기에_위에서_생성한_토큰_입력
```

#### 3. 백엔드 재시작

```bash
docker compose -f docker-compose.dev.yml restart oj-backend
```

#### 4. Judge 서버 등록

Admin 페이지에서 Judge 서버를 수동으로 등록하거나, 자동 heartbeat를 기다립니다 (약 1분).

**수동 등록:**
```bash
docker exec oj-backend-dev sh -c "cd /app && python manage.py shell << 'EOF'
from conf.models import JudgeServer
JudgeServer.objects.create(
    hostname='oj-judge-server',
    service_url='http://oj-judge-server:8080',
    cpu_core=4,
    memory_usage=0,
    cpu_usage=0,
    last_heartbeat='2026-01-09 00:00:00',
    create_time='2026-01-09 00:00:00',
    task_number=0,
    is_disabled=False
)
print('Judge server registered successfully')
EOF"
```

### 방법 2: Docker Compose에 Judge 서버 추가

#### 1. docker-compose.dev.yml에 Judge 서버 추가

파일 끝에 추가:

```yaml
  oj-judge-server:
    image: registry.cn-hangzhou.aliyuncs.com/onlinejudge/judge_server
    container_name: oj-judge-server-dev
    restart: always
    privileged: true
    ports:
      - "127.0.0.1:12358:8080"
    environment:
      - SERVICE_URL=http://oj-judge-server-dev:8080
      - BACKEND_URL=http://oj-backend:8000/api/judge_server_heartbeat/
      - TOKEN=YOUR_JUDGE_SERVER_TOKEN_HERE
    depends_on:
      - oj-backend
```

#### 2. 토큰 일치시키기

`oj-backend`와 `oj-judge-server`의 `TOKEN` / `JUDGE_SERVER_TOKEN`를 같은 값으로 설정.

#### 3. 실행

```bash
docker compose -f docker-compose.dev.yml up -d
```

### 방법 3: 로컬 개발 모드 (테스트용)

Judge 서버 없이 로컬에서 직접 실행 (보안 위험 있음, 개발 전용):

[backend/submission/views/oj.py](backend/submission/views/oj.py) 수정:

```python
# 현재 (89번째 줄 근처):
judge_task.send(submission.id, problem.id)

# 변경:
from judge.dispatcher import JudgeDispatcher
JudgeDispatcher(submission.id, problem.id).judge()
```

⚠️ **주의:** 이 방법은 보안상 안전하지 않으며, 실제 운영 환경에서는 사용하면 안 됩니다.

## 검증

### 1. Judge 서버 등록 확인

```bash
docker exec oj-backend-dev sh -c "cd /app && python manage.py shell << 'EOF'
from conf.models import JudgeServer
servers = JudgeServer.objects.all()
print(f'Total Judge Servers: {servers.count()}')
for server in servers:
    print(f'  - {server.hostname}: {server.service_url}')
    print(f'    Status: {server.status}, Disabled: {server.is_disabled}')
    print(f'    CPU Cores: {server.cpu_core}, Tasks: {server.task_number}')
EOF"
```

### 2. Judge 서버 상태 확인

```bash
curl http://localhost:12358/ping
# 예상 응답: {"data": "pong", "err": null}
```

### 3. 제출 테스트

1. 문제 페이지에서 간단한 코드 제출
2. 제출 목록에서 상태 확인
3. 로그 확인:
   ```bash
   docker logs -f oj-backend-dev 2>&1 | grep -i judge
   ```

### 4. 제출 상태 확인

```bash
docker exec oj-postgres-dev psql -U onlinejudge -d onlinejudge -c "
SELECT id, username, language, result, 
       CASE 
         WHEN result = 0 THEN 'Pending'
         WHEN result = 1 THEN 'Running'
         WHEN result = 2 THEN 'Compile Error'
         WHEN result = 3 THEN 'Wrong Answer'
         WHEN result = 4 THEN 'Runtime Error'
         WHEN result = 5 THEN 'Time Limit Exceeded'
         WHEN result = 6 THEN 'Memory Limit Exceeded'
         WHEN result = 7 THEN 'System Error'
         WHEN result = 0 THEN 'Accepted'
         ELSE 'Unknown'
       END as status
FROM submission 
ORDER BY id DESC 
LIMIT 10;
"
```

## Judge 서버 아키텍처

```
┌─────────────┐          ┌─────────────────┐
│   Browser   │          │   Judge Server  │
│             │          │   (Sandboxed)   │
└──────┬──────┘          └────────┬────────┘
       │                          │
       │ Submit Code              │ Heartbeat
       ▼                          ▼
┌──────────────────────────────────────────┐
│         Backend (Django)                 │
│                                          │
│  - Receives submissions                  │
│  - Queues judge tasks (dramatiq)        │
│  - Sends to Judge Server                │
│  - Updates submission results           │
└──────────────────────────────────────────┘
       │                          ▲
       │ Judge Request            │ Result
       ▼                          │
┌─────────────────────────────────────────┐
│         Judge Server                    │
│                                         │
│  - Compiles code                        │
│  - Runs test cases                      │
│  - Returns results                      │
└─────────────────────────────────────────┘
```

## 일반적인 문제 해결

### Judge 서버가 등록되지 않음

**원인:** Judge 서버가 백엔드에 heartbeat를 보내지 못함

**해결:**
1. Judge 서버의 `BACKEND_URL` 확인
2. 네트워크 연결 확인
3. 토큰 일치 여부 확인
4. 수동으로 등록 (위 참조)

### 제출이 "Pending" 상태에서 멈춤

**원인:** Judge 서버가 없거나 모든 서버가 disabled 상태

**해결:**
```bash
# Judge 서버 상태 확인
docker exec oj-backend-dev sh -c "cd /app && python manage.py shell << 'EOF'
from conf.models import JudgeServer
JudgeServer.objects.all().update(is_disabled=False)
print('All judge servers enabled')
EOF"
```

### 제출이 "System Error"

**원인:** Judge 서버 통신 실패 또는 테스트 케이스 누락

**해결:**
1. Judge 서버 로그 확인:
   ```bash
   docker logs oj-judge-server
   ```
2. 테스트 케이스 존재 확인:
   ```bash
   docker exec oj-backend-dev ls -la /data/test_case/
   ```

### 토큰 불일치

**증상:** Judge 서버가 등록되지 않음, heartbeat 실패

**해결:**
1. 백엔드 토큰 확인:
   ```bash
   docker exec oj-backend-dev env | grep JUDGE_SERVER_TOKEN
   ```
2. Judge 서버 토큰 확인:
   ```bash
   docker exec oj-judge-server env | grep TOKEN
   ```
3. 두 값을 일치시킨 후 재시작

## 권장 설정

### Production 환경
- Judge 서버를 별도의 머신에서 실행
- 여러 개의 Judge 서버를 로드 밸런싱
- Judge 서버는 sandboxed 환경에서 실행
- 강력한 토큰 사용 (최소 32자)

### Development 환경
- Docker Compose로 모든 서비스 통합
- 단일 Judge 서버로 충분
- 로컬 테스트용 간단한 토큰 사용 가능

## 참고 자료

- OnlineJudge 공식 문서: https://docs.onlinejudge.me/
- Judge 서버 GitHub: https://github.com/QingdaoU/JudgeServer
- Docker Hub: https://hub.docker.com/r/qduoj/judge_server
