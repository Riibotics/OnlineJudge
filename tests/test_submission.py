#!/usr/bin/env python3
"""
간단한 제출 테스트 스크립트
"""
import os
import sys
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from problem.models import Problem
from submission.models import Submission, JudgeStatus

User = get_user_model()

def test_submission():
    """간단한 A+B 문제로 제출 테스트"""
    print("\n" + "="*60)
    print("제출 테스트")
    print("="*60 + "\n")
    
    # 사용자 가져오기
    user = User.objects.filter(admin_type='Super Admin').first()
    if not user:
        print("❌ Super Admin 사용자를 찾을 수 없습니다!")
        return False
    
    print(f"✓ 사용자: {user.username}")
    
    # 문제 가져오기 (첫 번째 문제)
    problem = Problem.objects.filter(visible=True, contest_id__isnull=True).first()
    if not problem:
        print("❌ 테스트할 문제를 찾을 수 없습니다!")
        return False
    
    print(f"✓ 문제: {problem.title} (ID: {problem._id})")
    print(f"  Languages: {', '.join(problem.languages)}")
    
    # 간단한 Python 코드 (표준 입출력)
    test_code = """
a, b = map(int, input().split())
print(a + b)
""".strip()
    
    # 제출 생성
    submission = Submission.objects.create(
        user_id=user.id,
        username=user.username,
        language='Python3' if 'Python3' in problem.languages else problem.languages[0],
        code=test_code,
        problem_id=problem.id,
        ip='127.0.0.1'
    )
    
    print(f"\n✓ 제출 생성됨 (ID: {submission.id})")
    print(f"  언어: {submission.language}")
    print(f"  초기 상태: {JudgeStatus.PENDING}")
    
    # Judge 태스크 실행
    from judge.tasks import judge_task
    print("\n⏳ Judge 태스크 전송 중...")
    judge_task.send(submission.id, problem.id)
    
    # 결과 대기
    print("\n⏳ 결과 대기 중 (최대 30초)...")
    for i in range(30):
        time.sleep(1)
        submission.refresh_from_db()
        
        status_map = {
            JudgeStatus.PENDING: "대기 중",
            JudgeStatus.JUDGING: "채점 중",
            JudgeStatus.ACCEPTED: "정답",
            JudgeStatus.WRONG_ANSWER: "오답",
            JudgeStatus.TIME_LIMIT_EXCEEDED: "시간 초과",
            JudgeStatus.MEMORY_LIMIT_EXCEEDED: "메모리 초과",
            JudgeStatus.RUNTIME_ERROR: "런타임 에러",
            JudgeStatus.SYSTEM_ERROR: "시스템 에러",
            JudgeStatus.COMPILE_ERROR: "컴파일 에러"
        }
        
        status_text = status_map.get(submission.result, f"알 수 없음({submission.result})")
        print(f"  [{i+1}s] 상태: {status_text}", end='\r')
        
        if submission.result not in [JudgeStatus.PENDING, JudgeStatus.JUDGING]:
            break
    
    print("\n")
    
    # 최종 결과
    print("\n" + "="*60)
    print("최종 결과")
    print("="*60)
    print(f"상태: {status_map.get(submission.result, '알 수 없음')}")
    
    if hasattr(submission, 'statistic_info') and submission.statistic_info:
        if 'time_cost' in submission.statistic_info:
            print(f"실행 시간: {submission.statistic_info['time_cost']}ms")
        if 'memory_cost' in submission.statistic_info:
            print(f"메모리: {submission.statistic_info['memory_cost']/1024:.2f}KB")
        if 'score' in submission.statistic_info:
            print(f"점수: {submission.statistic_info['score']}")
    
    if submission.result == JudgeStatus.ACCEPTED:
        print("\n✅ 테스트 성공! Judge 서버가 정상 작동합니다.")
        return True
    elif submission.result == JudgeStatus.COMPILE_ERROR:
        print("\n⚠️  컴파일 에러:")
        if hasattr(submission, 'statistic_info') and 'err_info' in submission.statistic_info:
            print(submission.statistic_info['err_info'])
        return False
    else:
        print(f"\n⚠️  예상치 못한 결과: {submission.result}")
        if hasattr(submission, 'info') and submission.info:
            import json
            print(json.dumps(submission.info, indent=2))
        return False

if __name__ == '__main__':
    success = test_submission()
    sys.exit(0 if success else 1)
