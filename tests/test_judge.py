#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from problem.models import Problem
from submission.models import Submission
from judge.tasks import judge_task
import time

User = get_user_model()

# 간단한 C++ 코드
cpp_code = """#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}"""

user = User.objects.filter(admin_type='Super Admin').first()
problem = Problem.objects.filter(visible=True, contest_id__isnull=True).first()

print(f"문제: {problem.title}")
print(f"언어: C++")

# 제출 생성
submission = Submission.objects.create(
    user_id=user.id,
    username=user.username,
    language='C++',
    code=cpp_code,
    problem_id=problem.id,
    ip='127.0.0.1'
)

print(f"제출 ID: {submission.id}")

# Judge 태스크 전송
judge_task.send(submission.id, problem.id)
print("Judge 태스크 전송 완료")

# 결과 대기
print("\n결과 대기 중...")
for i in range(20):
    time.sleep(1)
    submission.refresh_from_db()
    print(f"[{i+1}s] Result: {submission.result}", end='\r')
    if submission.result not in [6, 1]:  # PENDING, JUDGING
        break

print(f"\n\n최종 결과: {submission.result}")
if submission.info:
    import json
    print("상세 정보:")
    print(json.dumps(submission.info, indent=2))
