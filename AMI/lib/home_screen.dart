// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:wakelock_plus/wakelock_plus.dart';
import 'alarm_logger_service.dart';
import 'motion_detector_service.dart';
import 'audio_service.dart';
import 'alarm_service.dart';
import 'alarm_state.dart';
import 'settings_screen.dart';

/// Main home screen of the alarm application.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with WidgetsBindingObserver {
  final MotionDetectorService _motionDetector = MotionDetectorService();
  final AudioService _audioService = AudioService();
  final TextEditingController _pinController = TextEditingController();
  
  AlarmState _alarmState = AlarmState.initial();
  String _correctPin = '1234567';
  bool _isPinVisible = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _loadSettings();
    _checkOverlayPermission();
    _updateSystemUI();
    WakelockPlus.enable();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _pinController.dispose();
    _audioService.dispose();
    _motionDetector.stopMonitoring();
    _restoreSystemUI();
    WakelockPlus.disable();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed && _alarmState.isTriggered) {
      _updateSystemUI();
      //_showOverlayIfNeeded();
    }
  }

  /// Updates system UI colors based on alarm state.
  void _updateSystemUI() {
    final barColor = _alarmState.isTriggered 
        ? const Color(0xFFB3261E) 
        : const Color(0xFF44A8E6);
    
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle(
      systemNavigationBarColor: barColor,
      systemNavigationBarIconBrightness: Brightness.light,
      statusBarColor: barColor,
      statusBarIconBrightness: Brightness.light,
    ));
    
    SystemChrome.setEnabledSystemUIMode(
      SystemUiMode.edgeToEdge,
      overlays: [SystemUiOverlay.top, SystemUiOverlay.bottom],
    );
  }

  /// Restores default system UI colors.
  void _restoreSystemUI() {
    SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
      systemNavigationBarColor: Color(0xFF44A8E6),
      systemNavigationBarIconBrightness: Brightness.light,
      statusBarColor: Color(0xFF44A8E6),
      statusBarIconBrightness: Brightness.light,
    ));
    
    SystemChrome.setEnabledSystemUIMode(
      SystemUiMode.edgeToEdge,
      overlays: [SystemUiOverlay.top, SystemUiOverlay.bottom],
    );
  }

  /// Loads saved settings from SharedPreferences.
  Future<void> _loadSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedPin = prefs.getString('alarm_pin');
      if (savedPin != null) {
        setState(() => _correctPin = savedPin);
      }
    } catch (e) {
      debugPrint('Error loading settings: $e');
    }
  }

  /// Checks and requests overlay permission.
  Future<void> _checkOverlayPermission() async {
    final hasOverlay = await AlarmService.hasOverlayPermission();
    
    if (!hasOverlay) {
      await AlarmService.requestOverlayPermission();
    }
  }

  /// Shows the overlay if alarm is triggered.
  /*void _showOverlayIfNeeded() {
    if (_alarmState.isTriggered && mounted) {
      AlarmOverlay.showOverlay(
        context,
        correctPin: _correctPin,
        onPinVerified: (pin) {
          _verifyPinWithValue(pin);
        },
      );
    }
  }*/

  /// Toggles alarm armed state.
  void _toggleAlarm() async {
    final newState = !_alarmState.isArmed;
    
    setState(() {
      _alarmState = _alarmState.copyWith(isArmed: newState);
    });

    await AlarmLoggerService.logEvent(
      event: newState ? 'alarm_armed' : 'alarm_disarmed',
      alarmArmed: newState,
      alarmTriggered: _alarmState.isTriggered,
    );
    
    if (newState) {
      _armAlarm();
    } else {
      _disarmAlarm();
    }
  }

  /// Arms the alarm and starts motion detection.
  void _armAlarm() {
    setState(() {
      _alarmState = _alarmState.copyWith(isTriggered: false);
    });
    
    _motionDetector.startMonitoring(() {
      if (mounted && !_alarmState.isTriggered && _alarmState.isArmed) {
        _triggerAlarm();
      }
    });
  }

  /// Disarms the alarm and stops all alert mechanisms.
  void _disarmAlarm() {
    _motionDetector.stopMonitoring();
    _audioService.stopAlarmSound();
    _audioService.stopVibration();
    _audioService.disableTorch();
    
    setState(() {
      _alarmState = _alarmState.copyWith(isTriggered: false);
    });
  }

  /// Triggers the alarm when motion is detected.
  Future<void> _triggerAlarm() async {
    if (_alarmState.isTriggered || !_alarmState.isArmed) return;

    setState(() {
      _alarmState = _alarmState.copyWith(
        isTriggered: true,
        triggeredTime: DateTime.now(),
        pinAttempts: 0,
      );
    });

    await AlarmLoggerService.logEvent(
      event: 'alarm_triggered',
      alarmArmed: _alarmState.isArmed,
      alarmTriggered: true,
      motionDetected: true,
    );

    _updateSystemUI();
    _motionDetector.stopMonitoring();
    
    await AlarmService.wakeScreen();
    await AlarmService.bringAppToForeground();
    
    //_showOverlayIfNeeded();
    
    await _activateAlerts();
  }

  /// Activates all alerts (sound, vibration, torch).
  Future<void> _activateAlerts() async {
    final prefs = await SharedPreferences.getInstance();
    final alarmSound = prefs.getString('alarm_sound') ?? 'sound1.wav';
    
    await _audioService.playAlarmSound(alarmSound);
    await _audioService.startVibration();
    await _audioService.enableTorch();
  }

  /// Verifies PIN and disables alarm if correct.
  Future<void> _verifyPin() async {
    await _verifyPinWithValue(_pinController.text);
  }

  /// Verifies the provided PIN value.
  Future<void> _verifyPinWithValue(String pinValue) async {
    final newAttempts = _alarmState.pinAttempts + 1;
    
    setState(() {
      _alarmState = _alarmState.copyWith(pinAttempts: newAttempts);
    });

    if (pinValue == _correctPin) {
      final timeToDisable = _alarmState.triggeredTime != null
          ? DateTime.now().difference(_alarmState.triggeredTime!).inMilliseconds
          : null;

      await AlarmLoggerService.logEvent(
        event: 'pin_verified',
        alarmArmed: _alarmState.isArmed,
        alarmTriggered: _alarmState.isTriggered,
        pinAttempts: newAttempts,
        pinSuccess: true,
        timeToDisableMs: timeToDisable,
        soundPlayed: _audioService.isPlaying,
        vibrationOn: _audioService.isVibrating,
        torchOn: _audioService.isTorchOn,
      );
      
      await AlarmLoggerService.forceExportOnAlarmStop();
      await _audioService.stopAlarmSound();
      await _audioService.stopVibration();
      await _audioService.disableTorch();
      
      //AlarmOverlay.hideOverlay();
      
      setState(() {
        _alarmState = AlarmState.initial();
      });
      
      _motionDetector.stopMonitoring();
      _updateSystemUI();
      _pinController.clear();
      
    } else {
      await AlarmLoggerService.logEvent(
        event: 'pin_failed',
        alarmArmed: _alarmState.isArmed,
        alarmTriggered: _alarmState.isTriggered,
        pinAttempts: newAttempts,
        pinSuccess: false,
      );
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('PIN incorreto. Tente outra vez.'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 2),
          ),
        );
      }
      _pinController.clear();
    }
  }

  /// Navigates to settings screen.
  void _navigateToSettings() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const SettingsScreen()),
    );
  }

  /// Shows help dialog.
  void _showDuvidasDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: const Color(0xFFE0F3FF),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Como Configurar',
                style: TextStyle(fontSize: 24),
              ),
              const SizedBox(height: 8),
              RichText(
                text: TextSpan(
                  style: const TextStyle(fontSize: 14, color: Colors.black),
                  children: [
                    const TextSpan(text: 'Clique no ícone '),
                    WidgetSpan(
                      child: Icon(
                        Icons.settings,
                        size: 16,
                        color: Colors.grey[700],
                      ),
                    ),
                    const TextSpan(
                      text:
                          ' para configurar o alarme.\n'
                          'Lá poderá escolher o som que o alarme emite e o PIN de desbloqueio.\n',
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Como Testar',
                style: TextStyle(fontSize: 24),
              ),
              const SizedBox(height: 8),
              const Text(
                'Ative o alarme e coloque o telemóvel pousado sobre a mesa.\nDepois puxe rapidamente o telemóvel para perto de si para verificar se o alarme dispara.',
                style: TextStyle(fontSize: 14),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _navigateToSettings();
              },
              child: const Text('Ir para Definições'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Fechar'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _alarmState.isTriggered ? const Color(0xFFB3261E) : Colors.white,
      appBar: AppBar(
        backgroundColor: _alarmState.isTriggered ? const Color(0xFFB3261E) : const Color(0xFF44A8E6),
        leading: !_alarmState.isTriggered
            ? IconButton(
                icon: const Icon(Icons.help_outline),
                tooltip: 'Ajuda',
                onPressed: _showDuvidasDialog,
              )
            : null,
        title: const Text(''),
        centerTitle: true,
        foregroundColor: Colors.white,
        actions: [
          if (!_alarmState.isTriggered)
            IconButton(
              icon: const Icon(Icons.settings),
              tooltip: 'Definições',
              onPressed: _navigateToSettings,
            ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(
              width: 250,
              height: 250,
              child: SvgPicture.asset(
                _alarmState.isTriggered 
                  ? 'assets/notifications_active_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.svg'
                  : 'assets/notifications_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.svg',
                width: 250,
                height: 250,
                colorFilter: ColorFilter.mode(
                  _alarmState.isTriggered ? Colors.white : const Color(0xFF565656),
                  BlendMode.srcIn,
                ),
                placeholderBuilder: (context) => const CircularProgressIndicator(),
                errorBuilder: (context, error, stackTrace) => Icon(
                  _alarmState.isTriggered ? Icons.notifications_active : Icons.notifications,
                  size: 250,
                  color: _alarmState.isTriggered ? Colors.white : const Color(0xFF565656),
                ),
              ),
            ),
            const SizedBox(height: 30),
            
            if (_alarmState.isTriggered) ...[
              const SizedBox(height: 16),
              SizedBox(
                width: 250,
                child: TextField(
                  controller: _pinController,
                  obscureText: !_isPinVisible,
                  keyboardType: TextInputType.number,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 16, color: Colors.black),
                  decoration: InputDecoration(
                    hintText: 'PIN',
                    hintStyle: const TextStyle(color: Color(0xFF49454F), fontSize: 16),
                    filled: true,
                    fillColor: const Color(0xFFE6E0E9),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _isPinVisible ? Icons.visibility_off : Icons.visibility,
                        color: const Color(0xFF49454F),
                      ),
                      onPressed: () => setState(() => _isPinVisible = !_isPinVisible),
                    ),
                  ),
                  onSubmitted: (_) => _verifyPin(),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Insira o PIN para desativar',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
              ),
            ],
            
            if (!_alarmState.isTriggered) ...[
              const SizedBox(height: 30),
              SizedBox(
                width: 150,
                height: 56,
                child: ElevatedButton(
                  onPressed: _toggleAlarm,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF79747E),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(50)),
                    elevation: 2,
                  ),
                  child: Text(
                    _alarmState.isArmed ? 'DESATIVAR' : 'ATIVAR',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}