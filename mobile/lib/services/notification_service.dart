import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:vibration/vibration.dart';

import '../core/navis_text.dart';
import '../models/app_models.dart';
import 'local_database.dart';

class NotificationService {
  NotificationService._();
  static final NotificationService instance = NotificationService._();

  final _plugin = FlutterLocalNotificationsPlugin();
  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;
    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    const ios = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    await _plugin.initialize(
      const InitializationSettings(android: android, iOS: ios),
      onDidReceiveNotificationResponse: (_) {},
    );
    await _plugin
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.requestNotificationsPermission();
    _initialized = true;
  }

  Future<void> notifyDetection({
    required String title,
    required String body,
    bool vibrate = true,
    bool playSound = true,
  }) async {
    await init();

    const details = NotificationDetails(
      android: AndroidNotificationDetails(
        'navis_detections',
        'Detections NAVIS',
        channelDescription: 'Alertes lors de la detection d objets importants',
        importance: Importance.high,
        priority: Priority.high,
        playSound: true,
        enableVibration: true,
      ),
      iOS: DarwinNotificationDetails(presentSound: true, presentBadge: true),
    );

    final safeTitle = NavisText.clean(title);
    final safeBody = NavisText.clean(body);

    await _plugin.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      safeTitle,
      safeBody,
      details,
    );

    await LocalDatabase.instance.insertNotification(
      AppNotificationRecord(
        title: safeTitle,
        body: safeBody,
        createdAt: DateTime.now(),
      ),
    );

    if (vibrate && await Vibration.hasVibrator()) {
      await Vibration.vibrate(duration: 120);
    }
  }
}
