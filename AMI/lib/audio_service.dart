// lib/services/audio_service.dart
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import 'package:vibration/vibration.dart';
import 'package:torch_light/torch_light.dart';

/// Service for managing alarm audio, vibration, and torch.
class AudioService {
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool _isPlaying = false;
  bool _isVibrating = false;
  bool _isTorchOn = false;

  /// Plays the alarm sound from asset or file path.
  Future<void> playAlarmSound(String soundPath) async {
    try {
      await _audioPlayer.stop();
      
      if (soundPath.startsWith('/')) {
        await _audioPlayer.play(DeviceFileSource(soundPath));
      } else {
        await _audioPlayer.play(AssetSource('sounds/$soundPath'));
      }
      
      _isPlaying = true;
      _audioPlayer.setReleaseMode(ReleaseMode.loop);
    } catch (e) {
      debugPrint('Error playing alarm sound: $e');
    }
  }

  /// Stops the alarm sound.
  Future<void> stopAlarmSound() async {
    await _audioPlayer.stop();
    _isPlaying = false;
  }

  /// Starts vibration in a loop.
  Future<void> startVibration() async {
    if (await Vibration.hasVibrator()) {
      _isVibrating = true;
      _vibrationLoop();
    }
  }

  /// Internal vibration loop.
  void _vibrationLoop() async {
    while (_isVibrating) {
      await Vibration.vibrate(duration: 500);
      await Future.delayed(const Duration(milliseconds: 500));
    }
  }

  /// Stops vibration.
  Future<void> stopVibration() async {
    _isVibrating = false;
    await Vibration.cancel();
  }

  /// Enables the torch/flashlight.
  Future<void> enableTorch() async {
    try {
      final isAvailable = await TorchLight.isTorchAvailable();
      if (isAvailable) {
        await TorchLight.enableTorch();
        _isTorchOn = true;
      }
    } catch (e) {
      debugPrint('Error enabling torch: $e');
    }
  }

  /// Disables the torch/flashlight.
  Future<void> disableTorch() async {
    try {
      await TorchLight.disableTorch();
      _isTorchOn = false;
    } catch (e) {
      debugPrint('Error disabling torch: $e');
    }
  }

  /// Disposes all resources.
  void dispose() {
    _audioPlayer.dispose();
    _isVibrating = false;
  }

  bool get isPlaying => _isPlaying;
  bool get isVibrating => _isVibrating;
  bool get isTorchOn => _isTorchOn;
}