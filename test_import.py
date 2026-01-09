#!/usr/bin/env python3
"""
Problem Import ZIP 파일 구조 검증 도구
"""
import sys
import zipfile
import json
from pathlib import Path

def test_zip_file(zip_path):
    """ZIP 파일 구조를 검증합니다."""
    print(f"\n{'='*60}")
    print(f"Testing ZIP file: {zip_path}")
    print(f"{'='*60}\n")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            name_list = zf.namelist()
            print(f"✓ ZIP 파일이 정상적으로 열렸습니다.")
            print(f"\n총 {len(name_list)}개의 파일이 포함되어 있습니다:\n")
            
            for name in sorted(name_list):
                print(f"  - {name}")
            
            # problem.json 파일 찾기
            problem_jsons = [n for n in name_list if '/problem.json' in n]
            print(f"\n{'='*60}")
            print(f"발견된 problem.json 파일: {len(problem_jsons)}개")
            print(f"{'='*60}\n")
            
            if not problem_jsons:
                print("❌ ERROR: problem.json 파일을 찾을 수 없습니다!")
                print("   예상 경로: 1/problem.json, 2/problem.json, ...")
                return False
            
            for pj_path in problem_jsons:
                print(f"\n📄 {pj_path} 검증 중...")
                
                # JSON 파싱 테스트
                try:
                    with zf.open(pj_path) as f:
                        problem_data = json.load(f)
                    print(f"  ✓ JSON 파싱 성공")
                    
                    # 필수 필드 확인
                    required_fields = [
                        'display_id', 'title', 'description', 'input_description',
                        'output_description', 'hint', 'test_case_score', 'time_limit',
                        'memory_limit', 'samples', 'template', 'rule_type', 'source',
                        'answers', 'tags'
                    ]
                    
                    missing_fields = [f for f in required_fields if f not in problem_data]
                    if missing_fields:
                        print(f"  ❌ 누락된 필드: {', '.join(missing_fields)}")
                        return False
                    else:
                        print(f"  ✓ 모든 필수 필드 존재")
                    
                    print(f"  - display_id: {problem_data.get('display_id')}")
                    print(f"  - title: {problem_data.get('title')}")
                    print(f"  - rule_type: {problem_data.get('rule_type')}")
                    
                    # 테스트 케이스 디렉토리 확인
                    problem_num = pj_path.split('/')[0]
                    testcase_prefix = f"{problem_num}/testcase/"
                    testcase_files = [n for n in name_list if n.startswith(testcase_prefix)]
                    
                    print(f"\n  테스트 케이스 파일 ({len(testcase_files)}개):")
                    
                    if not testcase_files:
                        print(f"    ❌ ERROR: {testcase_prefix} 디렉토리에 테스트 케이스가 없습니다!")
                        return False
                    
                    in_files = [f for f in testcase_files if f.endswith('.in')]
                    out_files = [f for f in testcase_files if f.endswith('.out')]
                    
                    print(f"    - .in 파일: {len(in_files)}개")
                    print(f"    - .out 파일: {len(out_files)}개")
                    
                    if problem_data.get('spj') is None and len(in_files) != len(out_files):
                        print(f"    ⚠️  WARNING: .in과 .out 파일 수가 다릅니다!")
                    
                    # 테스트 케이스 파일 목록 표시
                    for tc_file in sorted(testcase_files):
                        size = zf.getinfo(tc_file).file_size
                        print(f"      - {tc_file.replace(testcase_prefix, '')} ({size} bytes)")
                    
                    print(f"  ✓ 문제 검증 완료\n")
                    
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON 파싱 실패: {e}")
                    return False
                except Exception as e:
                    print(f"  ❌ 오류: {e}")
                    return False
            
            print(f"\n{'='*60}")
            print(f"✅ ZIP 파일 검증 완료!")
            print(f"   - {len(problem_jsons)}개의 문제가 정상적으로 import될 것으로 예상됩니다.")
            print(f"{'='*60}\n")
            return True
            
    except zipfile.BadZipFile:
        print(f"❌ ERROR: 잘못된 ZIP 파일입니다.")
        return False
    except FileNotFoundError:
        print(f"❌ ERROR: 파일을 찾을 수 없습니다: {zip_path}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 test_import.py <zip_file_path>")
        print("\nExample:")
        print("  python3 test_import.py problem-export.zip")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    success = test_zip_file(zip_path)
    sys.exit(0 if success else 1)
