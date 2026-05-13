#!/usr/bin/env python3
"""
Tactical Analytics testlerini çalıştırır.
"""
import sys
import os
import subprocess
from pathlib import Path

# Backend dizinini Python path'e ekle
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def run_tests():
    """Testleri çalıştır."""
    print("PitchVision Tactical Analytics - Test Suite")
    print("=" * 50)
    
    # Test dosyası yolu
    test_file = backend_dir / "tests" / "test_tactical_analytics.py"
    
    if not test_file.exists():
        print(f"❌ Test dosyası bulunamadı: {test_file}")
        return False
    
    try:
        # pytest ile testleri çalıştır
        cmd = [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"]
        
        print(f"🧪 Testler çalıştırılıyor: {' '.join(cmd)}")
        print("-" * 50)
        
        result = subprocess.run(cmd, cwd=backend_dir, capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ Tüm testler başarılı!")
            return True
        else:
            print(f"\n❌ Testler başarısız! Exit code: {result.returncode}")
            return False
            
    except FileNotFoundError:
        print("❌ pytest bulunamadı. Lütfen pytest'i yükleyin:")
        print("   pip install pytest")
        return False
    except Exception as e:
        print(f"❌ Test çalıştırma hatası: {e}")
        return False


def run_example():
    """Örnek kullanım scriptini çalıştır."""
    print("\n" + "=" * 50)
    print("Örnek Kullanım Çalıştırılıyor")
    print("=" * 50)
    
    try:
        from app.analytics.example_usage import main as example_main
        example_main()
        print("\n✅ Örnek kullanım başarılı!")
        return True
        
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        print("Lütfen gerekli bağımlılıkları yükleyin:")
        print("   pip install numpy")
        return False
    except Exception as e:
        print(f"❌ Örnek çalıştırma hatası: {e}")
        return False


def check_dependencies():
    """Gerekli bağımlılıkları kontrol et."""
    print("Bağımlılık Kontrolü")
    print("-" * 20)
    
    required_packages = ["numpy", "pytest"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - eksik")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Eksik paketler: {', '.join(missing_packages)}")
        print("Yüklemek için:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✅ Tüm bağımlılıklar mevcut!")
    return True


def main():
    """Ana fonksiyon."""
    print("PitchVision Tactical Analytics Engine")
    print("Test ve Örnek Çalıştırma Scripti")
    print("=" * 60)
    
    # Bağımlılıkları kontrol et
    if not check_dependencies():
        sys.exit(1)
    
    # Testleri çalıştır
    test_success = run_tests()
    
    # Örnek kullanımı çalıştır
    example_success = run_example()
    
    # Sonuç
    print("\n" + "=" * 60)
    print("SONUÇ")
    print("=" * 60)
    
    if test_success and example_success:
        print("✅ Tüm işlemler başarılı!")
        print("\nTactical Analytics Engine kullanıma hazır!")
        print("\nAPI endpoint'lerini test etmek için:")
        print("   python -m uvicorn app.main:app --reload")
        sys.exit(0)
    else:
        print("❌ Bazı işlemler başarısız!")
        if not test_success:
            print("   - Testler başarısız")
        if not example_success:
            print("   - Örnek kullanım başarısız")
        sys.exit(1)


if __name__ == "__main__":
    main()