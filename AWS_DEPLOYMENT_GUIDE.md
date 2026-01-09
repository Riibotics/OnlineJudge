# AWS 서버 배포 체크리스트

## 문제: 8080 포트 접속 불가

IP: 3.27.120.144
포트: 8080

## 해결 방법

### 1. AWS Security Group 설정 (가장 중요!)

AWS EC2 콘솔에서:

1. EC2 대시보드 → 인스턴스 선택
2. 하단 탭에서 "Security" 클릭
3. Security Groups 링크 클릭
4. "Inbound rules" 탭 → "Edit inbound rules" 클릭
5. "Add rule" 클릭하여 다음 규칙 추가:

**필수 규칙:**
```
Type: Custom TCP
Port range: 8080
Source: 0.0.0.0/0 (또는 Anywhere-IPv4)
Description: OnlineJudge Frontend

Type: Custom TCP
Port range: 8000
Source: 0.0.0.0/0 (또는 Anywhere-IPv4)
Description: OnlineJudge Backend API

Type: SSH
Port range: 22
Source: My IP (보안을 위해)
Description: SSH Access
```

6. "Save rules" 클릭

### 2. 서버 내 방화벽 확인

SSH로 서버 접속 후:

```bash
# 방화벽 상태 확인 (Ubuntu/Debian)
sudo ufw status

# 만약 활성화되어 있다면:
sudo ufw allow 8080/tcp
sudo ufw allow 8000/tcp
sudo ufw reload

# CentOS/Amazon Linux의 경우:
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 3. Docker 컨테이너 실행 확인

서버에서:

```bash
# 컨테이너 상태 확인
docker ps

# 예상 출력: oj-frontend-dev, oj-backend-dev, oj-postgres-dev, oj-redis-dev가 모두 Up 상태

# 로그 확인
docker logs oj-frontend-dev --tail 50
docker logs oj-backend-dev --tail 50

# 포트 리스닝 확인
sudo netstat -tlnp | grep 8080
sudo netstat -tlnp | grep 8000
# 또는
sudo ss -tlnp | grep 8080
```

### 4. 서비스 시작

서버에서:

```bash
cd /path/to/OnlineJudge
./scripts/start.sh
```

### 5. 접속 테스트

로컬에서:

```bash
# 8080 포트 테스트
curl -I http://3.27.120.144:8080

# 8000 포트 테스트
curl http://3.27.120.144:8000/api/website/

# 성공 시 HTML 또는 JSON 응답이 와야 함
```

브라우저에서:
- http://3.27.120.144:8080

## 추가 설정 (선택사항)

### 도메인 설정

도메인이 있다면:

1. DNS 레코드 추가:
   - Type: A
   - Name: @  (또는 judge)
   - Value: 3.27.120.144

2. 접속:
   - http://yourdomain.com:8080

### HTTPS 설정 (Nginx + Let's Encrypt)

프로덕션 환경에서는 HTTPS를 권장합니다.

## 일반적인 문제 해결

### 문제 1: "Connection refused"
- Docker 컨테이너가 실행 중이 아님
- 해결: `./scripts/start.sh` 실행

### 문제 2: "Connection timeout"
- Security Group에서 포트가 열려있지 않음
- 해결: 위의 "1. AWS Security Group 설정" 참조

### 문제 3: 서비스는 실행 중이지만 접속 불가
- 방화벽 문제
- 해결: 위의 "2. 서버 내 방화벽 확인" 참조

### 문제 4: 502 Bad Gateway
- 백엔드가 실행 중이 아니거나 응답 없음
- 해결: `docker logs oj-backend-dev` 확인

## 프로덕션 환경 추가 설정

### docker-compose.yml 사용

개발 환경(`docker-compose.dev.yml`) 대신 프로덕션 설정 사용:

```bash
# 프로덕션용 docker-compose.yml 생성 또는 수정
docker compose up -d

# 또는 개발 환경 그대로 사용
docker compose -f docker-compose.dev.yml up -d
```

### 환경 변수 설정

보안을 위해 `.env` 파일 생성:

```bash
# .env
JUDGE_SERVER_TOKEN=your-secure-random-token-here
POSTGRES_PASSWORD=your-secure-password-here
```

### 정기 백업 설정

```bash
# 데이터베이스 백업 스크립트
#!/bin/bash
docker exec oj-postgres-dev pg_dump -U onlinejudge onlinejudge > backup_$(date +%Y%m%d_%H%M%S).sql

# crontab에 추가 (매일 새벽 2시)
0 2 * * * /path/to/backup.sh
```

## 모니터링

### 서비스 상태 확인

```bash
# 모든 컨테이너 상태
docker ps -a

# 리소스 사용량
docker stats

# 로그 실시간 모니터링
docker logs -f oj-frontend-dev
docker logs -f oj-backend-dev
```

## 문제 지속 시

다음 정보를 확인해주세요:

```bash
# 서버에서 실행
echo "=== Docker 상태 ==="
docker ps -a

echo "=== 포트 리스닝 ==="
sudo netstat -tlnp | grep -E "8080|8000"

echo "=== 방화벽 상태 ==="
sudo ufw status verbose

echo "=== 프로세스 ==="
ps aux | grep -E "docker|nginx"

echo "=== 로그 ==="
docker logs oj-frontend-dev --tail 20
docker logs oj-backend-dev --tail 20
```

위 명령어 실행 결과를 공유해주시면 더 정확한 진단이 가능합니다.
