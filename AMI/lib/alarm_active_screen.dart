// lib/alarm_active.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:vibration/vibration.dart';
import 'package:torch_light/torch_light.dart';
import 'motion_detector_service.dart';

class AlarmActivePage extends StatefulWidget {
  const AlarmActivePage({super.key});
  

  @override
  State<AlarmActivePage> createState() => _AlarmActivePageState();
}

class _AlarmActivePageState extends State<AlarmActivePage> {
  final TextEditingController _pinController = TextEditingController();
  final AudioPlayer _audioPlayer = AudioPlayer();
  final MotionDetectorService _motionDetector = MotionDetectorService();
  
  bool _isPinVisible = false;
  String _correctPin = '1234567';
  String _alarmSound = 'sound1.wav';
  bool _isVibrating = false;
  bool _isAlarmTriggered = false;
  static const _wakeChannel = MethodChannel('com.alarm_app/wake_screen');


  @override
  void initState() {
    super.initState();
    _loadSettings();
    _enableFullScreen();
    
    // Usar Future.microtask para mostrar SnackBar após a construção inicial
    Future.microtask(() {
      if (mounted) {
        _enterStandbyMode();
      }
    });
  }

  @override
  void dispose() {
    _pinController.dispose();
    _audioPlayer.dispose();
    _stopVibration();
    _disableTorch();
    _disableFullScreen();
    _motionDetector.stopMonitoring();
    super.dispose();
  }

  // Enter standby mode (listening for motion but not alarming)
  void _enterStandbyMode() {
    setState(() {
      _isAlarmTriggered = false;
    });
    
    // Start motion detection
    _motionDetector.startMonitoring(() {
      // This callback is called when sudden motion is detected
      if (mounted && !_isAlarmTriggered) {
        _triggerAlarm();
      }
    });
    
    // Mostrar SnackBar apenas se o contexto estiver disponível
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Alarme em standby. Aguardando movimento...'),
          backgroundColor: Colors.orange,
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  // Trigger the alarm when motion is detected
  Future<void> _triggerAlarm() async {
    if (_isAlarmTriggered) return;

    setState(() {
      _isAlarmTriggered = true;
    });

    _motionDetector.stopMonitoring();

    // Acender o ecrã
    try {
      await _wakeChannel.invokeMethod('wakeScreen');
    } catch (e) {
      print('Erro ao acender ecrã: $e');
    }

    await _playAlarmSound();
    await _startVibration();
    await _enableTorch();
  }

  // Enable full screen mode
  void _enableFullScreen() {
    SystemChrome.setEnabledSystemUIMode(
      SystemUiMode.immersiveSticky,
      overlays: [],
    );
    
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
  }

  // Disable full screen mode
  void _disableFullScreen() {
    SystemChrome.setEnabledSystemUIMode(
      SystemUiMode.edgeToEdge,
      overlays: [
        SystemUiOverlay.top,
        SystemUiOverlay.bottom,
      ],
    );
    
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
  }

  // Enable torch/flashlight
  Future<void> _enableTorch() async {
    if (!_isAlarmTriggered) return;
    
    try {
      final isAvailable = await TorchLight.isTorchAvailable();
      if (isAvailable) {
        await TorchLight.enableTorch();
        setState(() {
        });
        print('Lanterna ligada com sucesso');
      }
    } on Exception catch (e) {
      print('Erro ao ligar lanterna: $e');
    }
  }

  // Disable torch/flashlight
  Future<void> _disableTorch() async {
    try {
      await TorchLight.disableTorch();
      setState(() {
      });
    } on Exception catch (e) {
      print('Erro ao desligar lanterna: $e');
    }
  }

  // Start vibration in a loop
  Future<void> _startVibration() async {
    if (!_isAlarmTriggered) return;
    
    if (await Vibration.hasVibrator()) {
      setState(() {
        _isVibrating = true;
      });
      _vibrationLoop();
    }
  }

  // Manual vibration loop
  void _vibrationLoop() async {
    while (_isVibrating && mounted && _isAlarmTriggered) {
      await Vibration.vibrate(duration: 500);
      await Future.delayed(const Duration(milliseconds: 500));
    }
  }

  // Stop vibration
  Future<void> _stopVibration() async {
    setState(() {
      _isVibrating = false;
    });
    await Vibration.cancel();
  }

  // Load saved settings
  Future<void> _loadSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      final savedPin = prefs.getString('alarm_pin');
      if (savedPin != null) {
        setState(() {
          _correctPin = savedPin;
        });
      }
      
      final savedSound = prefs.getString('alarm_sound');
      if (savedSound != null) {
        setState(() {
          _alarmSound = savedSound;
        });
      }
    } catch (e) {
      print('Erro ao carregar configurações: $e');
    }
  }

  // Play alarm sound
  Future<void> _playAlarmSound() async {
    if (!_isAlarmTriggered) return;
    
    try {
      await _audioPlayer.stop();
      
      if (_alarmSound.startsWith('/')) {
        await _audioPlayer.play(DeviceFileSource(_alarmSound));
      } else {
        await _audioPlayer.play(AssetSource('sounds/$_alarmSound'));
      }
      
      setState(() {
      });
      
      _audioPlayer.setReleaseMode(ReleaseMode.loop);
      
      print('Alarme a tocar: $_alarmSound');
    } catch (e) {
      print('Erro ao tocar alarme: $e');
    }
  }

  // Stop alarm sound
  Future<void> _stopAlarmSound() async {
    await _audioPlayer.stop();
    setState(() {
    });
  }

  void _verifyPin() async {
    if (_pinController.text == _correctPin) {
      // Stop alarm, vibration and torch
      await _stopAlarmSound();
      await _stopVibration();
      await _disableTorch();
      _motionDetector.stopMonitoring();

      
      Future.delayed(const Duration(seconds: 1), () {
        if (mounted) {
          Navigator.of(context).pop();
        }
      });
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('PIN incorreto! Tente novamente.'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 2),
          ),
        );
      }
      _pinController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        systemNavigationBarColor: _isAlarmTriggered ? const Color(0xFFB3261E) : const Color(0xFF4A4A4A),
        systemNavigationBarIconBrightness: Brightness.light,
        statusBarColor: _isAlarmTriggered ? const Color(0xFFB3261E) : const Color(0xFF4A4A4A),
        statusBarIconBrightness: Brightness.light,
      ),
      child: Scaffold(
        backgroundColor: _isAlarmTriggered ? const Color(0xFFB3261E) : const Color(0xFF2C2C2C),
        body: Container(
          color: _isAlarmTriggered ? const Color(0xFFB3261E) : const Color(0xFF2C2C2C),
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Status indicator
                if (!_isAlarmTriggered)
                  Container(
                    margin: const EdgeInsets.only(bottom: 20),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.orange.withOpacity(0.8),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.warning_amber_rounded, color: Colors.white, size: 20),
                        SizedBox(width: 8),
                        Text(
                          'STAND-BY - AGUARDANDO MOVIMENTO',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                
                // Bell icon
                SizedBox(
                  width: 250,
                  height: 250,
                  child: SvgPicture.asset(
                    _isAlarmTriggered 
                      ? 'assets/notifications_active_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.svg'
                      : 'assets/notifications_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.svg',
                    width: 250,
                    height: 250,
                    colorFilter: ColorFilter.mode(
                      _isAlarmTriggered ? Colors.white : Colors.grey[400]!,
                      BlendMode.srcIn,
                    ),
                    placeholderBuilder: (context) => const CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                    errorBuilder: (context, error, stackTrace) {
                      print('Erro ao carregar SVG: $error');
                      return Icon(
                        _isAlarmTriggered ? Icons.notifications_active : Icons.notifications,
                        size: 250,
                        color: _isAlarmTriggered ? Colors.white : Colors.grey[400],
                      );
                    },
                  ),
                ),
                const SizedBox(height: 30),
                
                // Status text
                if (!_isAlarmTriggered)
                  const Text(
                    'Coloque o telemóvel numa superfície fixa\nO alarme disparará ao detectar movimento brusco',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                
                if (_isAlarmTriggered) ...[
                  
                  const SizedBox(height: 16),
                  
                  // PIN field
                  SizedBox(
                    width: 250,
                    child: TextField(
                      controller: _pinController,
                      obscureText: !_isPinVisible,
                      keyboardType: TextInputType.number,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.black,
                      ),
                      decoration: InputDecoration(
                        hintText: 'PIN',
                        hintStyle: const TextStyle(
                          color: Color(0xFF49454F),
                          fontSize: 16,
                        ),
                        filled: true,
                        fillColor: const Color(0xFFE6E0E9),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: BorderSide.none,
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: BorderSide.none,
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _isPinVisible ? Icons.visibility_off : Icons.visibility,
                            color: const Color(0xFF49454F),
                          ),
                          onPressed: () {
                            setState(() {
                              _isPinVisible = !_isPinVisible;
                            });
                          },
                        ),
                      ),
                      onSubmitted: (value) {
                        _verifyPin();
                      },
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  const Text(
                    'Insira o PIN para desativar',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
