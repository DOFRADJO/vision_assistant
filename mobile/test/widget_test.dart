import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:navis/main.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();
  databaseFactory = databaseFactoryFfi;

  testWidgets('NAVIS demarre sur l accueil vocal', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: NavisApp()));
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.text('NAVIS'), findsOneWidget);
    expect(find.text('Creer mon compte'), findsOneWidget);
    expect(find.text('Me connecter'), findsOneWidget);
  });
}
