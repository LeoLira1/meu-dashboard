import 'package:flutter/material.dart';

void main() {
  runApp(const MeuDashboardApp());
}

class MeuDashboardApp extends StatelessWidget {
  const MeuDashboardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Meu Dashboard',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFF0F0F1A),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFE8B4B8),
          brightness: Brightness.dark,
        ),
        cardTheme: CardThemeData(
          color: Colors.white.withValues(alpha: 0.07),
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
            side: BorderSide(
              color: Colors.white.withValues(alpha: 0.14),
            ),
          ),
        ),
      ),
      home: const DashboardPage(),
    );
  }
}

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final titleStyle = Theme.of(context).textTheme.titleMedium?.copyWith(
      fontWeight: FontWeight.w700,
      letterSpacing: 0.6,
    );

    return Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'MEU DASHBOARD',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w300,
                        letterSpacing: 4,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Atualizado em ${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white70,
                      ),
                    ),
                    const SizedBox(height: 20),
                    Text('Visão geral', style: titleStyle),
                    const SizedBox(height: 12),
                    GridView.count(
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.2,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      children: const [
                        StatCard(
                          label: 'Saldo Total',
                          value: 'R\$ 54.920',
                          subtitle: '+3.2% no mês',
                          accentColor: Color(0xFF82B8A0),
                        ),
                        StatCard(
                          label: 'Meta Mensal',
                          value: '78%',
                          subtitle: 'R\$ 7.800 / R\$ 10.000',
                          accentColor: Color(0xFFE8B4B8),
                        ),
                        StatCard(
                          label: 'Dólar',
                          value: 'R\$ 5,12',
                          subtitle: '-0.3% hoje',
                          accentColor: Color(0xFFA5B4C4),
                        ),
                        StatCard(
                          label: 'BTC',
                          value: 'US\$ 68.400',
                          subtitle: '+1.1% hoje',
                          accentColor: Color(0xFFD4B482),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    Text('Notícias', style: titleStyle),
                    const SizedBox(height: 10),
                    const NewsCard(
                      title: 'Mercado fecha em alta com dados positivos de inflação.',
                      source: 'Valor Econômico',
                    ),
                    const SizedBox(height: 10),
                    const NewsCard(
                      title: 'Tecnologia e IA lideram investimentos no trimestre.',
                      source: 'Reuters',
                    ),
                    const SizedBox(height: 24),
                    Text('Filmes e séries', style: titleStyle),
                    const SizedBox(height: 12),
                    SizedBox(
                      height: 180,
                      child: ListView(
                        scrollDirection: Axis.horizontal,
                        children: const [
                          MediaCard(
                            title: 'Duna: Parte 2',
                            genre: 'Ficção científica',
                            rating: '8.6',
                          ),
                          MediaCard(
                            title: 'Ruptura',
                            genre: 'Drama / Suspense',
                            rating: '8.7',
                          ),
                          MediaCard(
                            title: 'The Last of Us',
                            genre: 'Ação / Drama',
                            rating: '8.8',
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    Text('Próximos passos', style: titleStyle),
                    const SizedBox(height: 8),
                    const Card(
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('• Conectar APIs reais (cotação, clima e notícias).'),
                            SizedBox(height: 8),
                            Text('• Habilitar autenticação para dados pessoais.'),
                            SizedBox(height: 8),
                            Text('• Publicar APK automático no GitHub Releases.'),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class StatCard extends StatelessWidget {
  const StatCard({
    required this.label,
    required this.value,
    required this.subtitle,
    required this.accentColor,
    super.key,
  });

  final String label;
  final String value;
  final String subtitle;
  final Color accentColor;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: accentColor,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(label, style: Theme.of(context).textTheme.labelLarge),
              ],
            ),
            const Spacer(),
            Text(
              value,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.white70,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class NewsCard extends StatelessWidget {
  const NewsCard({
    required this.title,
    required this.source,
    super.key,
  });

  final String title;
  final String source;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title),
            const SizedBox(height: 6),
            Text(
              source,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.white70,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class MediaCard extends StatelessWidget {
  const MediaCard({
    required this.title,
    required this.genre,
    required this.rating,
    super.key,
  });

  final String title;
  final String genre;
  final String rating;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 150,
      margin: const EdgeInsets.only(right: 12),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Align(
                alignment: Alignment.topRight,
                child: Chip(
                  label: Text('⭐ $rating'),
                  backgroundColor: Colors.black26,
                  visualDensity: VisualDensity.compact,
                ),
              ),
              const Spacer(),
              Text(
                title,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                genre,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.white70,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
