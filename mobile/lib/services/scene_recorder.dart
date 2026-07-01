import 'dart:io';
import 'dart:typed_data';

import 'package:image/image.dart' as img;
import 'package:intl/intl.dart';
import 'package:path_provider/path_provider.dart';

import '../models/app_models.dart';
import 'local_database.dart';

/// Sauvegarde une scene avec cadres et etiquettes sur l image.
class SceneRecorder {
  SceneRecorder._();
  static final SceneRecorder instance = SceneRecorder._();

  Future<SceneSnapshot?> save({
    required Uint8List imageBytes,
    required int frameWidth,
    required int frameHeight,
    required List<DetectionBox> boxes,
    required String summary,
    String source = 'camera',
  }) async {
    if (boxes.isEmpty && summary.isEmpty) return null;

    final decoded = img.decodeImage(imageBytes);
    if (decoded == null) return null;

    final annotated = _drawAnnotations(decoded, boxes);
    final jpeg = Uint8List.fromList(img.encodeJpg(annotated, quality: 88));

    final dir = await getApplicationDocumentsDirectory();
    final scenesDir = Directory('${dir.path}/navis_scenes');
    if (!await scenesDir.exists()) await scenesDir.create(recursive: true);

    final stamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final imagePath = '${scenesDir.path}/scene_$stamp.jpg';
    await File(imagePath).writeAsBytes(jpeg, flush: true);

    final labels = boxes.map((b) => '${b.labelFr} (${(b.confidence * 100).round()}%)').join(', ');

    await LocalDatabase.instance.insertDetection(
      DetectionRecord(
        labelFr: summary.isNotEmpty ? summary : labels,
        labelEn: source,
        confidence: boxes.isEmpty ? 0 : boxes.first.confidence,
        createdAt: DateTime.now(),
      ),
    );

    return SceneSnapshot(
      imagePath: imagePath,
      summary: summary,
      objectCount: boxes.length,
      labels: labels,
      createdAt: DateTime.now(),
    );
  }

  img.Image _drawAnnotations(img.Image source, List<DetectionBox> boxes) {
    final out = img.copyResize(source, width: source.width, height: source.height);
    for (final b in boxes) {
      final x1 = b.x1.round().clamp(0, out.width - 1);
      final y1 = b.y1.round().clamp(0, out.height - 1);
      final x2 = b.x2.round().clamp(x1 + 1, out.width);
      final y2 = b.y2.round().clamp(y1 + 1, out.height);

      img.drawRect(out, x1: x1, y1: y1, x2: x2, y2: y2, color: img.ColorRgb8(30, 123, 255));

      final tag = '${b.labelFr} ${(b.confidence * 100).round()}%';
      img.fillRect(
        out,
        x1: x1,
        y1: (y1 - 22).clamp(0, out.height - 22),
        x2: (x1 + tag.length * 9 + 12).clamp(0, out.width),
        y2: y1,
        color: img.ColorRgb8(11, 91, 212),
      );
      img.drawString(
        out,
        tag,
        font: img.arial14,
        x: x1 + 4,
        y: (y1 - 18).clamp(0, out.height - 14),
        color: img.ColorRgb8(255, 255, 255),
      );
    }
    return out;
  }
}

class SceneSnapshot {
  const SceneSnapshot({
    required this.imagePath,
    required this.summary,
    required this.objectCount,
    required this.labels,
    required this.createdAt,
  });

  final String imagePath;
  final String summary;
  final int objectCount;
  final String labels;
  final DateTime createdAt;
}
