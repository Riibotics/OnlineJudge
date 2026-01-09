# Apple Silicon(M1/M2/M3) Mac에서 Judge 서버 문제 해결

## 현재 상황

Apple Silicon (ARM64) Mac에서 x86_64 Judge 서버를 실행하면서 발생하는 문제:
- Signal 10 (SIGBUS) 에러
- System Error 발생
- 아키텍처 불일치로 인한 성능 저하

## 해결 방법

### 방법 1: Docker Desktop 설정 확인 (이미 적용됨)

`docker-compose.dev.yml`에 `platform: linux/amd64` 추가:
```yaml
oj-judge-server:
  platform: linux/amd64  # 명시적 플랫폼 지정
  ...
```

### 방법 2: Rosetta 2 활성화

Docker Desktop에서 Rosetta 2 에뮬레이션 활성화:

1. Docker Desktop 열기
2. Settings (⚙️) → General
3. "Use Rosetta for x86/amd64 emulation on Apple Silicon" 체크
4. Apply & Restart

### 방법 3: 대안 Judge 서버 (권장)

ARM64 네이티브 Judge 서버 빌드 또는 대안 사용을 고려할 수 있습니다.

**주의**: 공식 OnlineJudge Judge 서버는 아직 ARM64 네이티브 이미지를 제공하지 않습니다.

## 임시 해결책

현재 설정으로도 작동할 수 있지만, 다음 사항에 유의하세요:

### 성능 영향
- x86_64 에뮬레이션으로 인해 채점 속도가 느려질 수 있음
- CPU 사용률이 높아질 수 있음

### 안정성
- 일부 복잡한 프로그램에서 간헐적 오류 발생 가능
- Signal 오류가 계속 발생할 수 있음

## 테스트 방법

### 1. 간단한 코드로 테스트

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Hello World" << endl;
    return 0;
}
```

### 2. 입출력 테스트

```cpp
#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
```

### 3. 로그 확인

```bash
# Judge 서버 로그
docker logs oj-judge-server-dev --tail 50

# 백엔드 로그
docker logs oj-backend-dev --tail 50 | grep -i judge

# 최근 제출 확인
docker exec oj-postgres-dev psql -U onlinejudge -d onlinejudge -c \
  "SELECT id, language, result, info FROM submission ORDER BY create_time DESC LIMIT 5;"
```

## 완전한 해결책 (프로덕션 환경)

개발용으로는 현재 설정이 충분할 수 있지만, 프로덕션 환경에서는:

1. **Linux 서버에서 실행**: x86_64 Linux 서버 사용
2. **클라우드 서비스**: AWS, GCP, Azure 등의 x86_64 인스턴스 사용
3. **별도 머신**: Intel Mac 또는 x86_64 서버에서 Judge 서버만 실행

## 현재 적용된 수정사항

1. ✅ `platform: linux/amd64` 추가
2. ✅ C++ 컴파일 옵션 `-std=c++17`로 변경
3. ✅ 테스트 케이스 볼륨 공유
4. ✅ Judge 서버 heartbeat 확인

## 추가 디버깅

여전히 문제가 발생한다면:

```bash
# Judge 서버 내부에서 직접 테스트
docker exec -it oj-judge-server-dev /bin/sh

# 컴파일 테스트
echo '#include <iostream>
int main() { std::cout << "Test" << std::endl; }' > test.cpp
g++ -std=c++17 test.cpp -o test
./test

# 샌드박스 테스트
cd /code
python3 server.py
```

## 참고

- OnlineJudge GitHub: https://github.com/QingdaoU/OnlineJudge
- Judge Server GitHub: https://github.com/QingdaoU/JudgeServer
- Docker Rosetta: https://docs.docker.com/desktop/settings/mac/#use-rosetta-for-x86amd64-emulation-on-apple-silicon
