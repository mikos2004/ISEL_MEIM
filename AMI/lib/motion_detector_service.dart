// lib/services/motion_detector_service.dart
import 'dart:math';
import 'dart:async';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:sensors_plus/sensors_plus.dart';

/// Service for detecting sudden motion using accelerometer data.
class MotionDetectorService {
  static const double _motionThreshold = 3.0;
  static const int _consecutiveSamples = 2;
  static const double _filterAlpha = 0.2;
  static const int _maxSamples = 5;
  
  final List<double> _accelerationMagnitudes = [];
  double? _filteredMagnitude;
  bool _isMonitoring = false;
  VoidCallback? _onMotionDetected;
  StreamSubscription<AccelerometerEvent>? _subscription;

  /// Starts monitoring for motion events.
  void startMonitoring(VoidCallback onMotionDetected) {
    if (_isMonitoring) return;
    
    _onMotionDetected = onMotionDetected;
    _isMonitoring = true;
    _accelerationMagnitudes.clear();
    _filteredMagnitude = null;
    
    _subscription = accelerometerEvents.listen(
      _processAccelerometerEvent,
      onError: (error) => debugPrint('Accelerometer error: $error'),
    );
  }

  /// Processes incoming accelerometer events.
  void _processAccelerometerEvent(AccelerometerEvent event) {
    if (!_isMonitoring) return;
    
    final magnitude = sqrt(
      pow(event.x, 2) + pow(event.y, 2) + pow(event.z, 2)
    );
    
    _filteredMagnitude = _filteredMagnitude == null
        ? magnitude
        : _filterAlpha * magnitude + (1 - _filterAlpha) * _filteredMagnitude!;
    
    final effectiveAcceleration = (_filteredMagnitude! - 9.8).abs();
    _accelerationMagnitudes.add(effectiveAcceleration);
    
    while (_accelerationMagnitudes.length > _maxSamples) {
      _accelerationMagnitudes.removeAt(0);
    }
    
    if (_detectSuddenMotion(effectiveAcceleration)) {
      _onMotionDetected?.call();
    }
  }

  /// Detects if the current acceleration indicates sudden motion.
  bool _detectSuddenMotion(double currentAcceleration) {
    if (currentAcceleration <= _motionThreshold) return false;
    
    int consecutiveCount = 0;
    for (int i = _accelerationMagnitudes.length - 1; i >= 0; i--) {
      if (_accelerationMagnitudes[i] > _motionThreshold) {
        consecutiveCount++;
      } else {
        break;
      }
    }
    
    return consecutiveCount >= _consecutiveSamples;
  }

  /// Stops monitoring for motion events.
  void stopMonitoring() {
    _isMonitoring = false;
    _subscription?.cancel();
    _subscription = null;
    _accelerationMagnitudes.clear();
    _filteredMagnitude = null;
  }

  /// Returns whether monitoring is active.
  bool get isMonitoring => _isMonitoring;
}