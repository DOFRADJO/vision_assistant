import '../core/navis_text.dart';
import '../models/app_models.dart';

/// Analyse la scene pour produire des annonces utiles aux malvoyants :
/// position, distance estimee, nombre de personnes, approche, dangers.
class SceneInterpreter {
  SceneInterpreter._();
  static final SceneInterpreter instance = SceneInterpreter._();

  final Map<String, double> _prevAreaByKey = {};
  final Map<String, DateTime> _lastAlertByKey = {};

  static const _vehicles = {'car', 'bus', 'truck', 'train', 'bicycle', 'motorcycle'};
  static const _danger = {'stop_sign', 'traffic_light'};

  SceneAnalysis analyze(
    List<DetectionBox> boxes, {
    required int frameWidth,
    required int frameHeight,
  }) {
    if (boxes.isEmpty) {
      return const SceneAnalysis.empty();
    }

    final people = boxes.where((b) => b.navisLabel == 'person').toList();
    final vehicles = boxes.where((b) => _vehicles.contains(b.navisLabel)).toList();
    final dangers = boxes.where((b) => _danger.contains(b.navisLabel)).toList();
    final others = boxes
        .where((b) => b.navisLabel != 'person' && !_vehicles.contains(b.navisLabel) && !_danger.contains(b.navisLabel))
        .toList();

    final alerts = <String>[];
    final details = <String>[];

    if (people.isNotEmpty) {
      final countMsg = people.length == 1
          ? 'Une personne autour de vous'
          : '${people.length} personnes autour de vous';
      alerts.add(countMsg);
      details.add(_peopleSummary(people, frameWidth, frameHeight));
    }

    for (final v in vehicles) {
      final phrase = _objectPhrase(v, frameWidth, frameHeight, isVehicle: true);
      details.add(phrase);
      if (_isApproaching(v, frameWidth, frameHeight)) {
        alerts.add('Attention, ${v.labelFr.toLowerCase()} qui s approche ${_sector(v, frameWidth)}');
      }
    }

    for (final d in dangers) {
      final phrase = _objectPhrase(d, frameWidth, frameHeight);
      details.add(phrase);
      if (d.distanceLevel(frameWidth, frameHeight) == DistanceLevel.veryClose) {
        alerts.add('Attention, ${d.labelFr.toLowerCase()} ${_sector(d, frameWidth)}');
      }
    }

    for (final o in others.take(3)) {
      details.add(_objectPhrase(o, frameWidth, frameHeight));
    }

    final summary = _buildSummary(people.length, vehicles.length, dangers.isNotEmpty);
    final spoken = _composeSpeech(alerts, details, summary);

    return SceneAnalysis(
      summary: summary,
      spokenText: spoken,
      peopleCount: people.length,
      vehicleCount: vehicles.length,
      hasDanger: dangers.isNotEmpty || alerts.isNotEmpty,
      isUrgent: alerts.isNotEmpty,
    );
  }

  bool shouldAnnounce(SceneAnalysis analysis, {Duration cooldown = const Duration(milliseconds: 1200)}) {
    if (analysis.spokenText.isEmpty) return false;
    final key = analysis.isUrgent
        ? 'urgent_${analysis.summary}_${analysis.peopleCount}_${analysis.vehicleCount}'
        : '${analysis.summary}_${analysis.peopleCount}_${analysis.vehicleCount}';
    final last = _lastAlertByKey[key];
    final gap = analysis.isUrgent ? const Duration(milliseconds: 1800) : cooldown;
    if (last != null && DateTime.now().difference(last) < gap) return false;
    _lastAlertByKey[key] = DateTime.now();
    return true;
  }

  String _peopleSummary(List<DetectionBox> people, int w, int h) {
    if (people.length == 1) {
      final p = people.first;
      return 'Une personne ${_distance(p, w, h)} ${_sector(p, w)}';
    }
    final sectors = people.map((p) => _sector(p, w)).toSet();
    final where = sectors.length == 1 ? sectors.first : 'autour de vous';
    return '${people.length} personnes $where';
  }

  String _objectPhrase(DetectionBox box, int w, int h, {bool isVehicle = false}) {
    final dist = _distance(box, w, h);
    final sector = _sector(box, w);
    if (isVehicle && box.distanceLevel(w, h) == DistanceLevel.veryClose) {
      return '${box.labelFr} $dist $sector';
    }
    return '${box.labelFr} $dist $sector';
  }

  String _distance(DetectionBox box, int w, int h) {
    return switch (box.distanceLevel(w, h)) {
      DistanceLevel.veryClose => 'tres proche',
      DistanceLevel.near => 'proche',
      DistanceLevel.mid => 'a quelques metres',
      DistanceLevel.far => 'au loin',
    };
  }

  String _sector(DetectionBox box, int w) {
    final cx = box.centerX / w;
    if (cx < 0.33) return 'a votre gauche';
    if (cx > 0.67) return 'a votre droite';
    return 'devant vous';
  }

  bool _isApproaching(DetectionBox box, int w, int h) {
    final key = '${box.navisLabel}_${_sector(box, w)}';
    final area = box.area;
    final prev = _prevAreaByKey[key];
    _prevAreaByKey[key] = area;
    if (prev == null) return box.distanceLevel(w, h) == DistanceLevel.veryClose;
    final level = box.distanceLevel(w, h);
    return area > prev * 1.35 && (level == DistanceLevel.near || level == DistanceLevel.veryClose);
  }

  String _buildSummary(int people, int vehicles, bool danger) {
    final parts = <String>[];
    if (people > 0) parts.add('$people personne${people > 1 ? 's' : ''}');
    if (vehicles > 0) parts.add('$vehicles vehicule${vehicles > 1 ? 's' : ''}');
    if (danger) parts.add('signalisation');
    return parts.isEmpty ? 'objets detectes' : parts.join(', ');
  }

  String _composeSpeech(List<String> alerts, List<String> details, String summary) {
    final buffer = StringBuffer();
    if (alerts.isNotEmpty) {
      buffer.write(alerts.first);
      if (alerts.length > 1) buffer.write('. ${alerts[1]}');
      buffer.write('. ');
    }
    if (details.isNotEmpty) {
      buffer.write(details.take(3).join('. '));
      buffer.write('. ');
    }
    buffer.write('Scene: ${NavisText.clean(summary)}.');
    return NavisText.clean(buffer.toString().trim());
  }
}

enum DistanceLevel { veryClose, near, mid, far }

class SceneAnalysis {
  const SceneAnalysis({
    required this.summary,
    required this.spokenText,
    required this.peopleCount,
    required this.vehicleCount,
    required this.hasDanger,
    required this.isUrgent,
  });

  const SceneAnalysis.empty()
      : summary = '',
        spokenText = '',
        peopleCount = 0,
        vehicleCount = 0,
        hasDanger = false,
        isUrgent = false;

  final String summary;
  final String spokenText;
  final int peopleCount;
  final int vehicleCount;
  final bool hasDanger;
  final bool isUrgent;
}

extension DetectionBoxScene on DetectionBox {
  double get centerX => (x1 + x2) / 2;
  double get centerY => (y1 + y2) / 2;
  double get area => (x2 - x1) * (y2 - y1);

  double areaRatio(int frameW, int frameH) => area / (frameW * frameH);

  DistanceLevel distanceLevel(int frameW, int frameH) {
    final r = areaRatio(frameW, frameH);
    final bottom = y2 / frameH;
    if (r > 0.10 || bottom > 0.75) return DistanceLevel.veryClose;
    if (r > 0.04 || bottom > 0.55) return DistanceLevel.near;
    if (r > 0.015) return DistanceLevel.mid;
    return DistanceLevel.far;
  }

  String distancePhrase(int frameW, int frameH) => switch (distanceLevel(frameW, frameH)) {
        DistanceLevel.veryClose => 'tres proche, moins de 2 metres',
        DistanceLevel.near => 'proche, environ 2 a 5 metres',
        DistanceLevel.mid => 'a quelques metres',
        DistanceLevel.far => 'au loin',
      };

  bool get isVehicle => const {'car', 'bus', 'truck', 'train', 'bicycle', 'motorcycle'}.contains(navisLabel);
  bool get isPerson => navisLabel == 'person';
  bool get isDangerSign => const {'stop_sign', 'traffic_light'}.contains(navisLabel);
}
