#!/bin/bash
# 제출 디버깅 스크립트

echo "=== Judge 서버 상태 확인 ==="
docker exec oj-backend-dev sh -c "cd /app && python manage.py shell << 'EOF'
from conf.models import JudgeServer
servers = JudgeServer.objects.filter(is_disabled=False)
for s in servers:
    print(f'{s.hostname}: {s.status} (Tasks: {s.task_number})')
EOF"

echo -e "\n=== 최근 제출 확인 ==="
docker exec oj-postgres-dev psql -U onlinejudge -d onlinejudge -c "
SELECT 
    id, 
    language, 
    result,
    CASE 
        WHEN result = -2 THEN 'Compile Error'
        WHEN result = -1 THEN 'Wrong Answer'
        WHEN result = 0 THEN 'Accepted'
        WHEN result = 1 THEN 'CPU Time Limit Exceeded'
        WHEN result = 2 THEN 'Real Time Limit Exceeded'
        WHEN result = 3 THEN 'Memory Limit Exceeded'
        WHEN result = 4 THEN 'Runtime Error'
        WHEN result = 5 THEN 'System Error'
        WHEN result = 6 THEN 'Pending'
        WHEN result = 7 THEN 'Judging'
        WHEN result = 8 THEN 'Partially Accepted'
        ELSE 'Unknown'
    END as status_text,
    substring(statistic_info::text, 1, 100) as error_info
FROM submission 
ORDER BY create_time DESC 
LIMIT 5;
"

echo -e "\n=== Judge 서버 로그 (최근 10줄) ==="
docker logs oj-judge-server-dev --tail 10 2>&1

echo -e "\n=== 백엔드 Judge 관련 로그 ==="
docker logs oj-backend-dev --tail 50 2>&1 | grep -i "judge\|error" | tail -10
