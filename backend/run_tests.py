#!/usr/bin/env python3
"""
سكريبت تشغيل الاختبارات
"""

import os
import sys
import subprocess

def run_tests():
    """تشغيل جميع الاختبارات"""
    print("🧪 بدء تشغيل الاختبارات...")
    
    # التأكد من وجود pytest
    try:
        import pytest
    except ImportError:
        print("❌ pytest غير مثبت. يرجى تثبيته أولاً:")
        print("pip install pytest pytest-flask pytest-cov")
        return False
    
    # تشغيل الاختبارات
    try:
        # اختبارات الوحدة
        print("\n📋 تشغيل اختبارات الوحدة...")
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', 
            '-v', 
            '--tb=short',
            '--cov=src',
            '--cov-report=term-missing'
        ], cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("\n✅ جميع الاختبارات نجحت!")
            return True
        else:
            print("\n❌ بعض الاختبارات فشلت!")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في تشغيل الاختبارات: {e}")
        return False

def run_specific_test(test_file):
    """تشغيل اختبار محدد"""
    print(f"🧪 تشغيل اختبار: {test_file}")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            f'tests/{test_file}', 
            '-v', 
            '--tb=short'
        ], cwd=os.path.dirname(__file__))
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل الاختبار: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    if len(sys.argv) > 1:
        # تشغيل اختبار محدد
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
    else:
        # تشغيل جميع الاختبارات
        success = run_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

