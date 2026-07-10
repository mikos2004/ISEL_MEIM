// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:wakelock_plus/wakelock_plus.dart';
import 'home_screen.dart';
import 'alarm_logger_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  await WakelockPlus.enable();
  await AlarmLoggerService.initLogFile();
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Alarm App',
      theme: ThemeData(
        colorScheme: const ColorScheme.light(
          primary: Color(0xFF44A8E6),
          secondary: Color(0xFF44A8E6),
          surface: Colors.white,
          error: Colors.red,
          onPrimary: Colors.white,
          onSecondary: Colors.white,
        ),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}