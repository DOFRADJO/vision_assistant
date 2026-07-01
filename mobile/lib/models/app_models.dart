class DetectionRecord {
  const DetectionRecord({
    this.id,
    required this.labelFr,
    required this.labelEn,
    required this.confidence,
    required this.createdAt,
  });

  final int? id;
  final String labelFr;
  final String labelEn;
  final double confidence;
  final DateTime createdAt;

  Map<String, Object?> toMap() => {
        'label_fr': labelFr,
        'label_en': labelEn,
        'confidence': confidence,
        'created_at': createdAt.toIso8601String(),
      };

  factory DetectionRecord.fromMap(Map<String, Object?> map) {
    return DetectionRecord(
      id: map['id'] as int?,
      labelFr: map['label_fr'] as String,
      labelEn: map['label_en'] as String,
      confidence: (map['confidence'] as num).toDouble(),
      createdAt: DateTime.parse(map['created_at'] as String),
    );
  }
}

class AppNotificationRecord {
  const AppNotificationRecord({
    this.id,
    required this.title,
    required this.body,
    required this.createdAt,
    this.read = false,
  });

  final int? id;
  final String title;
  final String body;
  final DateTime createdAt;
  final bool read;

  Map<String, Object?> toMap() => {
        'title': title,
        'body': body,
        'created_at': createdAt.toIso8601String(),
        'read': read ? 1 : 0,
      };

  factory AppNotificationRecord.fromMap(Map<String, Object?> map) {
    return AppNotificationRecord(
      id: map['id'] as int?,
      title: map['title'] as String,
      body: map['body'] as String,
      createdAt: DateTime.parse(map['created_at'] as String),
      read: (map['read'] as int? ?? 0) == 1,
    );
  }
}

class DetectionBox {
  const DetectionBox({
    required this.cocoClassId,
    required this.navisLabel,
    required this.labelFr,
    required this.confidence,
    required this.x1,
    required this.y1,
    required this.x2,
    required this.y2,
  });

  final int cocoClassId;
  final String navisLabel;
  final String labelFr;
  final double confidence;
  final double x1;
  final double y1;
  final double x2;
  final double y2;
}
