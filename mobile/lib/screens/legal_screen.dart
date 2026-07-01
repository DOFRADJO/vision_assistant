import 'package:flutter/material.dart';
import '../config/app_config.dart';
import '../theme/navis_theme.dart';

class PrivacyScreen extends StatelessWidget {
  const PrivacyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return _LegalScaffold(
      title: 'Confidentialite',
      sections: [
        const _Section('100 % local', 'NAVIS ne collecte aucun email. Votre prenom et code secret sont stockes uniquement sur votre telephone.'),
        const _Section('Images et camera', 'Les images sont traitees en direct sur l appareil. Aucune image n est envoyee sur internet.'),
        const _Section('Hors connexion', 'Detection, historique, notifications et voix fonctionnent sans internet.'),
        _Section('Editeur', AppConfig.companyName),
      ],
    );
  }
}

class TermsScreen extends StatelessWidget {
  const TermsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return _LegalScaffold(
      title: 'Conditions d utilisation',
      sections: [
        const _Section('Objet', 'NAVIS aide les personnes malvoyantes a comprendre leur environnement par la voix.'),
        const _Section('Compte local', 'Vous creez un compte vocalement. Vos identifiants restent sur cet appareil.'),
        _Section('Editeur', AppConfig.companyName),
      ],
    );
  }
}

class _Section {
  const _Section(this.title, this.body);
  final String title;
  final String body;
}

class _LegalScaffold extends StatelessWidget {
  const _LegalScaffold({required this.title, required this.sections});

  final String title;
  final List<_Section> sections;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NavisColors.offWhite,
      appBar: AppBar(title: Text(title)),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          for (final s in sections) ...[
            Text(s.title, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(s.body, style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.6)),
            const SizedBox(height: 24),
          ],
        ],
      ),
    );
  }
}
