// lib/services/alarm_service.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Service for native alarm functionality including foreground bring-up and overlay permissions.
class AlarmService {
  static const MethodChannel _channel = MethodChannel('com.alarm_app/alarm');
  static const MethodChannel _wakeChannel = MethodChannel('com.alarm_app/wake_screen');

  /// Brings the application to the foreground.
  static Future<void> bringAppToForeground() async {
    try {
      await _channel.invokeMethod('bringToForeground');
    } catch (e) {
      debugPrint('Error bringing app to foreground: $e');
    }
  }

  /// Shows the overlay alarm window.
  static Future<void> showOverlayAlarm() async {
    try {
      await _channel.invokeMethod('showOverlayAlarm');
    } catch (e) {
      debugPrint('Error showing overlay alarm: $e');
    }
  }

  /// Checks if overlay permission is granted.
  static Future<bool> hasOverlayPermission() async {
    try {
      final result = await _channel.invokeMethod('hasOverlayPermission');
      return result ?? false;
    } catch (e) {
      debugPrint('Error checking overlay permission: $e');
      return false;
    }
  }

  /// Requests overlay permission from the user.
  static Future<void> requestOverlayPermission() async {
    try {
      await _channel.invokeMethod('requestOverlayPermission');
    } catch (e) {
      debugPrint('Error requesting overlay permission: $e');
    }
  }

  /// Wakes up the screen.
  static Future<void> wakeScreen() async {
    try {
      await _wakeChannel.invokeMethod('wakeScreen');
    } catch (e) {
      debugPrint('Error waking screen: $e');
    }
  }
}