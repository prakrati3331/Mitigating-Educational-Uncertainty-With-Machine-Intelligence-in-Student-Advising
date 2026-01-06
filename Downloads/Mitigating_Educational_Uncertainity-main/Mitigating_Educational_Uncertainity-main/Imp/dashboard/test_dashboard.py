#!/usr/bin/env python3
"""
Test script for the dashboard backend
"""

import requests
import json
import time
from datetime import datetime

# Dashboard base URL
BASE_URL = "http://localhost:5007"

def test_dashboard_endpoints():
    """Test all dashboard endpoints"""
    
    print("🧪 Testing Dashboard Backend")
    print("=" * 50)
    
    # Test user ID
    test_user_id = f"test_user_{int(time.time())}"
    
    # Test cases
    test_cases = [
        {
            "name": "Dashboard Overview",
            "url": f"{BASE_URL}/api/dashboard/overview/{test_user_id}",
            "method": "GET",
            "expected_status": 200
        },
        {
            "name": "Full Dashboard Data",
            "url": f"{BASE_URL}/api/dashboard/{test_user_id}",
            "method": "GET", 
            "expected_status": 200
        },
        {
            "name": "Stream Prediction",
            "url": f"{BASE_URL}/api/stream/predict",
            "method": "POST",
            "data": {
                "user_id": test_user_id,
                "math": 85,
                "science": 90,
                "biology": 75,
                "english": 80,
                "social": 70,
                "language": 85,
                "logical": 88,
                "analytical": 82,
                "numerical": 86,
                "creativity": 78,
                "communication": 83,
                "artistic": 72,
                "practical": 80
            },
            "expected_status": 200
        },
        {
            "name": "Course Recommendations",
            "url": f"{BASE_URL}/api/courses/recommend/pcm",
            "method": "POST",
            "data": {
                "user_id": test_user_id,
                "user_profile": {
                    "Physics": 85,
                    "Chemistry": 80,
                    "Mathematics": 90,
                    "ComputerScience": 88,
                    "Statistics": 82,
                    "LogicalReasoning": 86,
                    "AnalyticalThinking": 84,
                    "InterestArea": 85
                }
            },
            "expected_status": 200
        },
        {
            "name": "Quiz Submission",
            "url": f"{BASE_URL}/api/quiz/submit",
            "method": "POST",
            "data": {
                "user_id": test_user_id,
                "quiz_type": "Aptitude",
                "score": 85,
                "total_questions": 20
            },
            "expected_status": 200
        },
        {
            "name": "Career Assessment",
            "url": f"{BASE_URL}/api/career/assess",
            "method": "POST",
            "data": {
                "user_id": test_user_id,
                "interests": ["Technology", "Science", "Mathematics"],
                "skills": ["Programming", "Problem Solving", "Analysis"],
                "personality": ["Analytical", "Detail-oriented", "Curious"]
            },
            "expected_status": 200
        },
        {
            "name": "Dropout Risk Assessment",
            "url": f"{BASE_URL}/api/dropout-risk/assess",
            "method": "POST",
            "data": {
                "user_id": test_user_id,
                "grades": 85,
                "attendance": 90,
                "assignments": 88,
                "exams": 82,
                "participation": 75,
                "absences": 2,
                "tardiness": 1,
                "behavioral_issues": 0,
                "financial_stress": 20,
                "work_hours": 10,
                "family_support": 85,
                "health_status": 90,
                "course_load": 75,
                "major_fit": 88,
                "faculty_interaction": 70,
                "campus_involvement": 65,
                "peer_network": 80,
                "mentorship": 75,
                "bullying": 0,
                "commute_time": 30,
                "family_responsibilities": 15,
                "work_life_balance": 70,
                "motivation": 85,
                "self_efficacy": 80,
                "stress_level": 25,
                "previous_dropout": 0,
                "grade_retention": 0,
                "school_changes": 0,
                "lms_activity": 85,
                "online_engagement": 80,
                "warning_signs": 10,
                "early_alerts": 5
            },
            "expected_status": 200
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n📋 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        print(f"   Method: {test['method']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            else:
                response = requests.post(
                    test['url'], 
                    json=test.get('data', {}),
                    timeout=10
                )
            
            if response.status_code == test['expected_status']:
                print(f"   ✅ PASS - Status: {response.status_code}")
                
                # Try to parse JSON response
                try:
                    data = response.json()
                    if 'error' in data:
                        print(f"   ⚠️  Warning: API returned error - {data['error']}")
                    else:
                        print(f"   📄 Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   📄 Response: {response.text[:200]}...")
                
                passed += 1
            else:
                print(f"   ❌ FAIL - Expected: {test['expected_status']}, Got: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                failed += 1
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ FAIL - Connection error. Is the dashboard running?")
            failed += 1
        except requests.exceptions.Timeout:
            print(f"   ❌ FAIL - Request timeout")
            failed += 1
        except Exception as e:
            print(f"   ❌ FAIL - {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Dashboard is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the dashboard logs.")
    
    print("=" * 50)
    
    return failed == 0

def test_dashboard_ui():
    """Test if dashboard UI loads"""
    print("\n🖥️  Testing Dashboard UI")
    print("=" * 30)
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard UI loads successfully")
            if "Career Guidance Dashboard" in response.text:
                print("✅ Dashboard title found")
            else:
                print("⚠️  Dashboard title not found")
            return True
        else:
            print(f"❌ Dashboard UI failed to load - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing UI: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Dashboard Backend Test Suite")
    print("=" * 50)
    print(f"Testing URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test UI first
    ui_ok = test_dashboard_ui()
    
    # Test API endpoints
    api_ok = test_dashboard_endpoints()
    
    # Overall result
    print("\n🏁 Final Results")
    print("=" * 30)
    print(f"UI Test: {'✅ PASS' if ui_ok else '❌ FAIL'}")
    print(f"API Test: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if ui_ok and api_ok:
        print("\n🎉 Dashboard is fully functional!")
        exit(0)
    else:
        print("\n⚠️  Dashboard has issues that need to be addressed.")
        exit(1)

if __name__ == "__main__":
    main()
