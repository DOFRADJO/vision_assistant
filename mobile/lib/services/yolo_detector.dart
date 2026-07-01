import 'dart:convert';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/services.dart';
import 'package:flutter_onnxruntime/flutter_onnxruntime.dart';
import 'package:image/image.dart' as img;

import '../config/app_config.dart';
import '../core/coco_classes.dart';
import '../models/app_models.dart';

class YoloDetector {
  YoloDetector._();
  static final YoloDetector instance = YoloDetector._();

  OrtSession? _session;
  String? _inputName;
  bool _ready = false;

  bool get isReady => _ready;

  Future<void> init() async {
    if (_ready) return;
    final ort = OnnxRuntime();
    _session = await ort.createSessionFromAsset(AppConfig.modelAsset);
    _inputName = _session!.inputNames.first;
    _ready = true;
  }

  Future<List<DetectionBox>> detectFromBytes(Uint8List bytes, {int width = 0, int height = 0}) async {
    if (!_ready) await init();
    final decoded = img.decodeImage(bytes);
    if (decoded == null) return [];
    return detectFromImage(decoded);
  }

  Future<List<DetectionBox>> detectFromImage(img.Image source, {double? confThreshold}) async {
    if (!_ready) await init();

    final letterbox = _letterbox(source, AppConfig.inputSize);
    final input = _imageToTensor(letterbox.image);
    final inputTensor = await OrtValue.fromList(input, [1, 3, AppConfig.inputSize, AppConfig.inputSize]);
    final outputs = await _session!.run({_inputName!: inputTensor});
    final outputTensor = outputs[_session!.outputNames.first] ?? outputs.values.first;
    final raw = await outputTensor.asList();
    await inputTensor.dispose();
    await outputTensor.dispose();

    final flat = _flattenDoubles(raw);
    final threshold = confThreshold ?? AppConfig.confThreshold;

    return _decodeOutputs(
      flat,
      sourceWidth: source.width,
      sourceHeight: source.height,
      scale: letterbox.scale,
      padX: letterbox.padX,
      padY: letterbox.padY,
      confThreshold: threshold,
    );
  }

  List<DetectionBox> _decodeOutputs(
    List flat, {
    required int sourceWidth,
    required int sourceHeight,
    required double scale,
    required double padX,
    required double padY,
    required double confThreshold,
  }) {
    // YOLOv8 ONNX output: [1, 84, 8400] flattened — 80 classes COCO
    const numClasses = CocoClasses.count;
    const numAnchors = 8400;
    const channels = 4 + numClasses;

    if (flat.length < channels * numAnchors) return [];

    final candidates = <DetectionBox>[];

    for (var i = 0; i < numAnchors; i++) {
      var bestClass = -1;
      var bestScore = 0.0;
      for (var c = 0; c < numClasses; c++) {
        final score = _asDouble(flat[(4 + c) * numAnchors + i]);
        if (score > bestScore) {
          bestScore = score;
          bestClass = c;
        }
      }
      if (bestScore < confThreshold) continue;
      if (bestClass < 0 || bestClass >= CocoClasses.count) continue;

      final cx = _asDouble(flat[0 * numAnchors + i]);
      final cy = _asDouble(flat[1 * numAnchors + i]);
      final w = _asDouble(flat[2 * numAnchors + i]);
      final h = _asDouble(flat[3 * numAnchors + i]);

      final x1 = ((cx - w / 2) - padX) / scale;
      final y1 = ((cy - h / 2) - padY) / scale;
      final x2 = ((cx + w / 2) - padX) / scale;
      final y2 = ((cy + h / 2) - padY) / scale;

      final navisKey = CocoClasses.keyForId(bestClass);
      candidates.add(
        DetectionBox(
          cocoClassId: bestClass,
          navisLabel: navisKey,
          labelFr: CocoClasses.labelFr(navisKey),
          confidence: bestScore,
          x1: x1.clamp(0, sourceWidth.toDouble()),
          y1: y1.clamp(0, sourceHeight.toDouble()),
          x2: x2.clamp(0, sourceWidth.toDouble()),
          y2: y2.clamp(0, sourceHeight.toDouble()),
        ),
      );
    }

    return _nms(candidates, AppConfig.iouThreshold);
  }

  List<DetectionBox> _nms(List<DetectionBox> boxes, double iouThreshold) {
    boxes.sort((a, b) => b.confidence.compareTo(a.confidence));
    final kept = <DetectionBox>[];
    final suppressed = List<bool>.filled(boxes.length, false);

    for (var i = 0; i < boxes.length; i++) {
      if (suppressed[i]) continue;
      kept.add(boxes[i]);
      for (var j = i + 1; j < boxes.length; j++) {
        if (suppressed[j]) continue;
        if (boxes[i].navisLabel == boxes[j].navisLabel && _iou(boxes[i], boxes[j]) > iouThreshold) {
          suppressed[j] = true;
        }
      }
    }
    return kept;
  }

  double _iou(DetectionBox a, DetectionBox b) {
    final interX1 = math.max(a.x1, b.x1);
    final interY1 = math.max(a.y1, b.y1);
    final interX2 = math.min(a.x2, b.x2);
    final interY2 = math.min(a.y2, b.y2);
    final interArea = math.max(0, interX2 - interX1) * math.max(0, interY2 - interY1);
    final areaA = (a.x2 - a.x1) * (a.y2 - a.y1);
    final areaB = (b.x2 - b.x1) * (b.y2 - b.y1);
    return interArea / (areaA + areaB - interArea + 1e-6);
  }

  List<double> _flattenDoubles(List<dynamic> raw) {
    final out = <double>[];
    void walk(dynamic node) {
      if (node is List) {
        for (final item in node) {
          walk(item);
        }
      } else if (node is num) {
        out.add(node.toDouble());
      }
    }
    walk(raw);
    return out;
  }

  double _asDouble(Object? v) => v is num ? v.toDouble() : double.parse(v.toString());

  List<double> _imageToTensor(img.Image image) {
    final data = <double>[];
    for (var c = 0; c < 3; c++) {
      for (var y = 0; y < image.height; y++) {
        for (var x = 0; x < image.width; x++) {
          final pixel = image.getPixel(x, y);
          final channel = switch (c) {
            0 => pixel.r,
            1 => pixel.g,
            _ => pixel.b,
          };
          data.add(channel / 255.0);
        }
      }
    }
    return data;
  }

  _LetterboxResult _letterbox(img.Image source, int size) {
    final scale = math.min(size / source.width, size / source.height);
    final nw = (source.width * scale).round();
    final nh = (source.height * scale).round();
    final resized = img.copyResize(source, width: nw, height: nh);
    final canvas = img.Image(width: size, height: size);
    img.fill(canvas, color: img.ColorRgb8(114, 114, 114));
    final padX = (size - nw) / 2;
    final padY = (size - nh) / 2;
    img.compositeImage(canvas, resized, dstX: padX.round(), dstY: padY.round());
    return _LetterboxResult(image: canvas, scale: scale, padX: padX, padY: padY);
  }

  Future<List<String>> loadClassNames() async {
    final jsonStr = await rootBundle.loadString(AppConfig.labelsAsset);
    final data = jsonDecode(jsonStr) as Map<String, dynamic>;
    return (data['names'] as List).cast<String>();
  }
}

class _LetterboxResult {
  const _LetterboxResult({
    required this.image,
    required this.scale,
    required this.padX,
    required this.padY,
  });

  final img.Image image;
  final double scale;
  final double padX;
  final double padY;
}
