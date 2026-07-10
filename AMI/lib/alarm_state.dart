// lib/models/alarm_state.dart

/// Represents the current state of the alarm system.
class AlarmState {
  final bool isArmed;
  final bool isTriggered;
  final int pinAttempts;
  final DateTime? triggeredTime;

  const AlarmState({
    required this.isArmed,
    required this.isTriggered,
    this.pinAttempts = 0,
    this.triggeredTime,
  });

  AlarmState copyWith({
    bool? isArmed,
    bool? isTriggered,
    int? pinAttempts,
    DateTime? triggeredTime,
  }) {
    return AlarmState(
      isArmed: isArmed ?? this.isArmed,
      isTriggered: isTriggered ?? this.isTriggered,
      pinAttempts: pinAttempts ?? this.pinAttempts,
      triggeredTime: triggeredTime ?? this.triggeredTime,
    );
  }

  factory AlarmState.initial() {
    return const AlarmState(
      isArmed: false,
      isTriggered: false,
      pinAttempts: 0,
      triggeredTime: null,
    );
  }
}