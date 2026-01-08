#!/usr/bin/env python3
"""
Online Judge 보안 기능 테스트 스크립트
"""
import requests
import json

BASE_URL = "http://localhost:8000"

class OJTester:
    def __init__(self):
        self.session = requests.Session()
        
    def test_no_login_problem_access(self):
        """테스트 1: 로그인 없이 문제 접근 시도 (차단되어야 함)"""
        print("\n=== 테스트 1: 로그인 없이 문제 접근 ===")
        resp = self.session.get(f"{BASE_URL}/api/problem?limit=10")
        data = resp.json()
        if data.get('error') == 'permission-denied':
            print("✅ PASS: 로그인 없이 문제 접근 차단됨")
            print(f"   메시지: {data.get('data')}")
            return True
        else:
            print("❌ FAIL: 로그인 없이 문제에 접근할 수 있음")
            return False
    
    def login(self, username, password):
        """로그인"""
        # CSRF 토큰 가져오기
        self.session.get(f"{BASE_URL}/api/website")
        csrf_token = self.session.cookies.get('csrftoken')
        
        # 로그인
        resp = self.session.post(
            f"{BASE_URL}/api/login",
            json={"username": username, "password": password},
            headers={"X-CSRFToken": csrf_token}
        )
        
        try:
            return resp.json()
        except:
            print(f"   응답 상태: {resp.status_code}")
            print(f"   응답 내용: {resp.text[:200]}")
            return {"error": "parse_error", "data": resp.text}
    
    def test_unapproved_user_login(self):
        """테스트 2: 승인되지 않은 사용자 로그인 시도"""
        print("\n=== 테스트 2: 승인되지 않은 사용자 로그인 ===")
        result = self.login("testuser", "testpass123")
        
        if result.get('error') and 'not approved' in result.get('data', ''):
            print("✅ PASS: 승인되지 않은 사용자 로그인 차단됨")
            print(f"   메시지: {result.get('data')}")
            return True
        else:
            print("❌ FAIL: 승인되지 않은 사용자가 로그인할 수 있음")
            print(f"   응답: {result}")
            return False
    
    def test_admin_login_and_access(self):
        """테스트 3: 관리자 로그인 및 문제 접근"""
        print("\n=== 테스트 3: 관리자 로그인 및 접근 ===")
        result = self.login("root", "rootroot")
        
        if result.get('error'):
            print(f"❌ FAIL: 관리자 로그인 실패 - {result}")
            return False
        
        print("✅ 관리자 로그인 성공")
        
        # 문제 접근 시도
        resp = self.session.get(f"{BASE_URL}/api/problem?limit=10")
        data = resp.json()
        
        if data.get('error'):
            print(f"❌ FAIL: 관리자가 문제에 접근할 수 없음 - {data}")
            return False
        else:
            print("✅ PASS: 관리자가 문제에 정상 접근 가능")
            return True
    
    def test_contest_access_without_approval(self):
        """테스트 4: 승인되지 않은 사용자의 대회 접근"""
        print("\n=== 테스트 4: 승인되지 않은 사용자의 대회 접근 ===")
        # 새 세션으로 미승인 사용자 로그인 시도
        test_session = requests.Session()
        test_session.get(f"{BASE_URL}/api/website")
        
        # Contest 접근 (로그인 없이)
        resp = test_session.get(f"{BASE_URL}/api/contests?limit=10")
        data = resp.json()
        
        if data.get('error') == 'permission-denied':
            print("✅ PASS: 로그인 없이 대회 접근 차단됨")
            return True
        else:
            print("❌ FAIL: 로그인 없이 대회에 접근 가능")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 60)
        print("Online Judge 보안 기능 테스트 시작")
        print("=" * 60)
        
        results = []
        results.append(self.test_no_login_problem_access())
        results.append(self.test_unapproved_user_login())
        results.append(self.test_admin_login_and_access())
        results.append(self.test_contest_access_without_approval())
        
        print("\n" + "=" * 60)
        print(f"테스트 결과: {sum(results)}/{len(results)} 통과")
        print("=" * 60)
        
        if all(results):
            print("\n🎉 모든 테스트 통과!")
            return True
        else:
            print("\n⚠️  일부 테스트 실패")
            return False

if __name__ == "__main__":
    tester = OJTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
