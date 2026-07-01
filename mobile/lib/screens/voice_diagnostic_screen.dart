import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';

import '../services/tts_service.dart';
import '../services/voice_coach.dart';
import '../theme/navis_theme.dart';

class VoiceDiagnosticScreen extends StatefulWidget {
  const VoiceDiagnosticScreen({super.key});

  @override
  State<VoiceDiagnosticScreen> createState() => _VoiceDiagnosticScreenState();
}

class _VoiceDiagnosticScreenState extends State<VoiceDiagnosticScreen> {
  bool _running = false;
  String _ttsState = 'Non teste';
  String _sttState = 'Non teste';
  String _micState = 'Non teste';
  String _result = 'Lancez le diagnostic.';

  Future<void> _runDiagnostic() async {
    if (_running) return;
    setState(() {
      _running = true;
      _result = 'Diagnostic en cours...';
    });

    try {
      final mic = await Permission.microphone.request();
      _micState = mic.isGranted ? 'OK' : 'Refuse';

      try {
        await TtsService.instance.init();
        await TtsService.instance.speak(
          'Test de la voix NAVIS. Si vous entendez ce message, la synthese vocale fonctionne.',
          cooldown: Duration.zero,
        );
        _ttsState = 'OK';
      } catch (e) {
        _ttsState = 'Erreur: $e';
      }

      try {
        final sttReady = await VoiceCoach.instance.init();
        if (!sttReady) {
          _sttState = 'Non disponible';
        } else {
          final started = await VoiceCoach.instance.startListening();
          if (started) {
            await Future<void>.delayed(const Duration(seconds: 3));
            final heard = await VoiceCoach.instance.stopListeningAndGetText();
            _sttState = heard == null || heard.isEmpty ? 'OK, mais rien entendu' : 'OK, entendu: $heard';
          } else {
            _sttState = 'Impossible de demarrer';
          }
        }
      } catch (e) {
        _sttState = 'Erreur: $e';
      }

      setState(() {
        _result = 'Diagnostic termine';
      });
    } finally {
      if (mounted) {
        setState(() => _running = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      appBar: AppBar(title: const Text('Diagnostic voix')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _tile('Microphone', _micState),
          const SizedBox(height: 10),
          _tile('Synthese vocale TTS', _ttsState),
          const SizedBox(height: 10),
          _tile('Reconnaissance vocale STT', _sttState),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: NavisColors.borderSoft),
            ),
            child: Text(_result, style: Theme.of(context).textTheme.bodyLarge),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: _running ? null : _runDiagnostic,
            icon: Icon(_running ? Icons.hourglass_top : Icons.play_arrow_rounded),
            label: Text(_running ? 'Diagnostic...' : 'Lancer le diagnostic'),
          ),
        ],
      ),
    );
  }

  Widget _tile(String title, String value) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: NavisColors.borderSoft),
      ),
      child: Row(
        children: [
          Expanded(child: Text(title, style: const TextStyle(fontWeight: FontWeight.w600))),
          const SizedBox(width: 10),
          Flexible(child: Text(value, textAlign: TextAlign.right)),
        ],
      ),
    );
  }
}

