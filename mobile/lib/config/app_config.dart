/// Configuration NAVIS — 100 % hors ligne.
abstract final class AppConfig {
  static const appName = 'NAVIS';
  static const appTagline = 'Vision assistee, entierement vocale';
  static const companyName = 'Propenta Tech';
  static const appUrl = 'https://navis.app';

  static const modelAsset = 'assets/models/navis_18classes.onnx';
  static const labelsAsset = 'assets/config/navis_labels.json';
  static const inputSize = 640;
  static const confThreshold = 0.28;
  static const iouThreshold = 0.45;
}
