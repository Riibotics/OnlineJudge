#!/usr/bin/env python3
"""
컨테이너 내부에서 Import 기능을 직접 테스트하는 스크립트
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
sys.path.insert(0, '/app')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from problem.views.admin import ImportProblemAPI

def test_import(zip_path):
    """ZIP 파일 import 테스트"""
    print(f"\n{'='*60}")
    print(f"Testing Import: {zip_path}")
    print(f"{'='*60}\n")
    
    # 파일 읽기
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    # Mock request 생성
    factory = RequestFactory()
    request = factory.post('/api/admin/problem/import_problem/',
                          data={})
    
    # Admin 사용자 가져오기
    User = get_user_model()
    try:
        request.user = User.objects.filter(admin_type='Super Admin').first()
        if not request.user:
            print("❌ Super Admin 사용자를 찾을 수 없습니다!")
            return
        print(f"✓ 사용자: {request.user.username}")
    except Exception as e:
        print(f"❌ 사용자 조회 실패: {e}")
        return
    
    # 업로드 파일 생성
    uploaded_file = SimpleUploadedFile(
        "problem-export.zip",
        zip_content,
        content_type="application/zip"
    )
    
    request.FILES['file'] = uploaded_file
    
    # Import API 호출
    api = ImportProblemAPI()
    try:
        response = api.post(request)
        print(f"\n응답 상태: {response.status_code}")
        print(f"응답 내용: {response.content.decode('utf-8')}\n")
    except Exception as e:
        print(f"\n❌ Import 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_import_internal.py <zip_file_path>")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    if not os.path.exists(zip_path):
        print(f"❌ 파일을 찾을 수 없습니다: {zip_path}")
        sys.exit(1)
    
    test_import(zip_path)
