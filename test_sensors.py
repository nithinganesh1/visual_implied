#!/usr/bin/env python3
"""
Test script for HC-SR04 Ultrasonic Sensor and Buzzer Module
Run independently to verify hardware setup
"""

import time
import sys
from ultrasonic_module import UltrasonicModule
from buzzer_module import BuzzerModule
from utils import logger


def test_buzzer_only():
    """Test buzzer module independently"""
    print("\n=== BUZZER TEST ===")
    print("Testing continuous buzzer tones and patterns...\n")
    
    try:
        buzzer = BuzzerModule(buzzer_pin=26)
        
        # Test 1: Single continuous tone
        print("1. Continuous tone (2 seconds)...")
        buzzer.play_continuous(frequency=1000, volume=0.8)
        time.sleep(2)
        buzzer.stop_tone()
        time.sleep(0.5)
        
        # Test 2: Different frequencies
        print("2. Testing different frequencies...")
        for freq in [500, 800, 1000, 1500, 2000]:
            print(f"   Playing {freq}Hz...")
            buzzer.play_continuous(frequency=freq, volume=0.8)
            time.sleep(1)
            buzzer.stop_tone()
            time.sleep(0.3)
        
        # Test 3: Proximity patterns
        print("\n3. Testing proximity-based patterns:")
        
        test_distances = [25, 15, 8, 3]
        for dist in test_distances:
            print(f"   Distance: {dist}cm (adaptive pattern for 3 seconds)...")
            buzzer.obstacle_warning_adaptive(distance_cm=dist, max_distance=30)
            time.sleep(3)
            buzzer.stop_tone()
            time.sleep(0.5)
        
        buzzer.cleanup()
        print("\n✓ Buzzer test complete\n")
        
    except Exception as e:
        print(f"✗ Buzzer test failed: {e}\n")
        sys.exit(1)


def test_ultrasonic_only():
    """Test ultrasonic sensor independently"""
    print("\n=== ULTRASONIC SENSOR TEST ===")
    print("Testing HC-SR04 distance measurement...")
    print("Hold hand at different distances from sensor...\n")
    
    try:
        ultrasonic = UltrasonicModule(trigger_pin=23, echo_pin=24, threshold_distance=30)
        
        # Monitor for 10 seconds
        for i in range(10):
            distance = ultrasonic.get_distance()
            is_obstacle = ultrasonic.is_obstacle_detected()
            
            if distance:
                alert_status = "🔴 ALERT" if is_obstacle else "✓ Clear"
                print(f"[{i}] Distance: {distance:.1f}cm | {alert_status}")
            else:
                print(f"[{i}] Reading...")
            
            time.sleep(1)
        
        ultrasonic.cleanup()
        print("\n✓ Ultrasonic test complete\n")
        
    except Exception as e:
        print(f"✗ Ultrasonic test failed: {e}\n")
        sys.exit(1)


def test_integrated():
    """Test ultrasonic + buzzer together"""
    print("\n=== INTEGRATED TEST (Ultrasonic + Buzzer) ===")
    print("Move hand toward sensor to trigger buzzer...\n")
    
    try:
        buzzer = BuzzerModule(buzzer_pin=26)
        
        def on_obstacle(distance):
            print(f"🔴 OBSTACLE ALERT at {distance:.1f}cm - Playing warning!")
            buzzer.beep_async(duration=0.3, frequency='alert', volume=0.8)
        
        def on_clear():
            print("✓ Obstacle cleared - Playing confirmation!")
            buzzer.beep_async(duration=0.2, frequency='done', volume=0.6)
        
        ultrasonic = UltrasonicModule(trigger_pin=23, echo_pin=24, threshold_distance=30)
        ultrasonic.on_obstacle_alert = on_obstacle
        ultrasonic.on_obstacle_clear = on_clear
        
        # Monitor for 15 seconds
        print("Monitoring for 15 seconds...\n")
        for i in range(15):
            distance = ultrasonic.get_distance()
            
            if distance:
                is_obstacle = ultrasonic.is_obstacle_detected()
                status = "🔴 ALERT" if is_obstacle else "✓"
                print(f"[{i}] {status} Distance: {distance:.1f}cm")
            
            time.sleep(1)
        
        ultrasonic.cleanup()
        buzzer.cleanup()
        print("\n✓ Integrated test complete\n")
        
    except Exception as e:
        print(f"✗ Integrated test failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("HC-SR04 & BUZZER HARDWARE TEST")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "buzzer":
            test_buzzer_only()
        elif test_type == "ultrasonic":
            test_ultrasonic_only()
        elif test_type == "integrated":
            test_integrated()
        else:
            print(f"Unknown test: {test_type}")
            print("\nUsage: python3 test_sensors.py [buzzer|ultrasonic|integrated]")
            sys.exit(1)
    else:
        # Run all tests
        test_buzzer_only()
        test_ultrasonic_only()
        test_integrated()
    
    print("=" * 50)
    print("All tests complete!")
    print("=" * 50)
