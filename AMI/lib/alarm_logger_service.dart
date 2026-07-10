// lib/services/alarm_logger_service.dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Service for logging alarm events to CSV file.
class AlarmLoggerService {
  static const String _logFileName = 'usability_log.csv';
  static const String _sessionKey = 'session_id';
  static const String _exportCounterKey = 'export_counter';
  static const String _lastExportTimeKey = 'last_export_time';
  static const String _eventsSinceExportKey = 'events_since_export';

  /// Returns the full path to the log file.
  static Future<String> _getLogFilePath() async {
    final dir = await getApplicationDocumentsDirectory();
    return '${dir.path}/$_logFileName';
  }

  /// Initializes the log file with proper headers.
  static Future<void> initLogFile() async {
    final path = await _getLogFilePath();
    final file = File(path);
    
    if (await file.exists()) {
      final firstLine = await file.readAsLines().then(
        (lines) => lines.isNotEmpty ? lines.first : ''
      );
      
      if (!firstLine.contains('session_id')) {
        final oldContent = await file.readAsString();
        await file.delete();
        await _writeHeaders(file);
        
        if (oldContent.trim().isNotEmpty) {
          await file.writeAsString(oldContent, mode: FileMode.append);
        }
      }
    } else {
      await _writeHeaders(file);
    }
  }

  /// Writes CSV headers to the file.
  static Future<void> _writeHeaders(File file) async {
    await file.writeAsString(
      'session_id,timestamp,event,alarm_armed,alarm_triggered,pin_attempts,'
      'pin_success,time_to_disable_ms,sound_played,vibration_on,torch_on,'
      'motion_detected,app_version\n'
    );
  }

  /// Gets or creates a session ID.
  static Future<String> _getSessionId() async {
    final prefs = await SharedPreferences.getInstance();
    String? sessionId = prefs.getString(_sessionKey);
    
    if (sessionId == null) {
      sessionId = DateTime.now().millisecondsSinceEpoch.toString();
      await prefs.setString(_sessionKey, sessionId);
    }
    
    return sessionId;
  }

  /// Logs an alarm event with the given parameters.
  static Future<void> logEvent({
    required String event,
    bool? alarmArmed,
    bool? alarmTriggered,
    int? pinAttempts,
    bool? pinSuccess,
    int? timeToDisableMs,
    bool? soundPlayed,
    bool? vibrationOn,
    bool? torchOn,
    bool? motionDetected,
  }) async {
    try {
      final sessionId = await _getSessionId();
      final timestamp = DateTime.now().toIso8601String();
      final path = await _getLogFilePath();
      final file = File(path);
      const appVersion = '1.0.0';

      final line = [
        sessionId,
        timestamp,
        event,
        alarmArmed?.toString() ?? '',
        alarmTriggered?.toString() ?? '',
        pinAttempts?.toString() ?? '',
        pinSuccess?.toString() ?? '',
        timeToDisableMs?.toString() ?? '',
        soundPlayed?.toString() ?? '',
        vibrationOn?.toString() ?? '',
        torchOn?.toString() ?? '',
        motionDetected?.toString() ?? '',
        appVersion,
      ].join(',');

      await file.writeAsString('$line\n', mode: FileMode.append);
      await _autoExportIfNeeded();
    } catch (e) {
      debugPrint('Error writing log: $e');
    }
  }

  /// Automatically exports log based on event count or time elapsed.
  static Future<void> _autoExportIfNeeded() async {
    final prefs = await SharedPreferences.getInstance();
    final lastExport = prefs.getInt(_lastExportTimeKey) ?? 0;
    final now = DateTime.now().millisecondsSinceEpoch;
    final eventsSinceLastExport = prefs.getInt(_eventsSinceExportKey) ?? 0;
    
    if (eventsSinceLastExport >= 10 || (now - lastExport) > 5 * 60 * 1000) {
      await exportLogToExternalStorage();
      await prefs.setInt(_lastExportTimeKey, now);
      await prefs.setInt(_eventsSinceExportKey, 0);
    } else {
      await prefs.setInt(_eventsSinceExportKey, eventsSinceLastExport + 1);
    }
  }

  /// Exports the log file to external storage.
  static Future<String?> exportLogToExternalStorage() async {
    try {
      final internalLogPath = await _getLogFilePath();
      final internalFile = File(internalLogPath);
      
      if (!await internalFile.exists()) {
        debugPrint('Log file does not exist');
        return null;
      }

      final logContent = await internalFile.readAsString();
      if (logContent.isEmpty) return null;

      String? externalPath;
      
      if (Platform.isAndroid) {
        final downloadsDir = Directory('/storage/emulated/0/Download');
        if (await downloadsDir.exists()) {
          final timestamp = DateTime.now().millisecondsSinceEpoch;
          final exportFileName = 'alarm_usability_log_$timestamp.csv';
          externalPath = '${downloadsDir.path}/$exportFileName';
          
          final exportFile = File(externalPath);
          await exportFile.writeAsString(logContent);
          debugPrint('Log exported to: $externalPath');
        }
      }
      
      if (externalPath == null) {
        final docsDir = await getApplicationDocumentsDirectory();
        final timestamp = DateTime.now().millisecondsSinceEpoch;
        final exportFileName = 'alarm_usability_log_$timestamp.csv';
        externalPath = '${docsDir.path}/$exportFileName';
        
        final exportFile = File(externalPath);
        await exportFile.writeAsString(logContent);
        debugPrint('Log exported to: $externalPath');
      }
      
      final prefs = await SharedPreferences.getInstance();
      final exportCount = prefs.getInt(_exportCounterKey) ?? 0;
      await prefs.setInt(_exportCounterKey, exportCount + 1);
      
      return externalPath;
    } catch (e) {
      debugPrint('Error exporting log: $e');
      return null;
    }
  }

  /// Forces immediate export when alarm is stopped.
  static Future<void> forceExportOnAlarmStop() async {
    await exportLogToExternalStorage();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_lastExportTimeKey, DateTime.now().millisecondsSinceEpoch);
    await prefs.setInt(_eventsSinceExportKey, 0);
  }

  /// Resets the current session.
  static Future<void> resetSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_sessionKey);
  }
}