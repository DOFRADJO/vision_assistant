import 'dart:io';

import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';

/// Prepare la video demo une seule fois au demarrage (evite le blocage UI).
class DemoVideoService {
  DemoVideoService._();
  static final DemoVideoService instance = DemoVideoService._();

  File? _file;
  bool _preparing = false;

  Future<File> getVideoFile() async {
    if (_file != null && await _file!.exists()) return _file!;
    return prepare();
  }

  bool get isReady => _file != null;

  Future<File> prepare() async {
    if (_file != null && await _file!.exists()) return _file!;
    if (_preparing) {
      while (_preparing) {
        await Future<void>.delayed(const Duration(milliseconds: 100));
      }
      if (_file != null) return _file!;
    }

    _preparing = true;
    try {
      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/navis_demo.mp4');
      // Toujours recopier l'asset pour prendre en compte une nouvelle video demo.
      final data = await rootBundle.load('assets/videos/demo.mp4');
      await file.writeAsBytes(data.buffer.asUint8List(), flush: true);
      _file = file;
      return file;
    } finally {
      _preparing = false;
    }
  }
}
