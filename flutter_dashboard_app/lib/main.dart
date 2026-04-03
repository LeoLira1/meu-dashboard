import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

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

// ─── Data models ────────────────────────────────────────────────────────────

class QuoteData {
  final String value;
  final String change;
  final bool isPositive;

  const QuoteData({
    required this.value,
    required this.change,
    required this.isPositive,
  });
}

class WeatherData {
  final double tempMax;
  final double tempMin;
  final double tempCurrent;
  final int humidity;
  final String description;

  const WeatherData({
    required this.tempMax,
    required this.tempMin,
    required this.tempCurrent,
    required this.humidity,
    required this.description,
  });
}

// ─── Static news content ─────────────────────────────────────────────────────

const _newsItems = [
  _NewsItem(
    title: 'Ibovespa avança com expectativa de corte na Selic e fluxo externo positivo.',
    source: 'Valor Econômico',
  ),
  _NewsItem(
    title: 'Dólar recua frente ao real com melhora do apetite por ativos emergentes.',
    source: 'Folha de S.Paulo',
  ),
  _NewsItem(
    title: 'IA generativa impulsiona resultados das big techs no primeiro trimestre de 2025.',
    source: 'Reuters',
  ),
  _NewsItem(
    title: 'Agronegócio mantém saldo comercial positivo e supera projeções do setor.',
    source: 'G1 Economia',
  ),
];

class _NewsItem {
  final String title;
  final String source;
  const _NewsItem({required this.title, required this.source});
}

// ─── Static media content ────────────────────────────────────────────────────

const _mediaItems = [
  _MediaItem(title: 'Duna: Parte 2', genre: 'Ficção científica', rating: '8.6'),
  _MediaItem(title: 'Ruptura', genre: 'Drama / Suspense', rating: '8.7'),
  _MediaItem(title: 'The Last of Us', genre: 'Ação / Drama', rating: '8.8'),
  _MediaItem(title: 'Succession', genre: 'Drama', rating: '8.9'),
  _MediaItem(title: 'Oppenheimer', genre: 'Drama / Histórico', rating: '8.3'),
];

class _MediaItem {
  final String title;
  final String genre;
  final String rating;
  const _MediaItem({required this.title, required this.genre, required this.rating});
}

// ─── Dashboard page ───────────────────────────────────────────────────────────

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  QuoteData? _dollar;
  QuoteData? _btc;
  WeatherData? _weather;
  bool _loading = true;
  bool _hasConnectivity = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    if (mounted) {
      setState(() {
        _loading = true;
        _hasConnectivity = true;
      });
    }

    final results = await Future.wait([
      _fetchDollar(),
      _fetchBtc(),
      _fetchWeather(),
    ]);

    if (mounted) {
      setState(() {
        _loading = false;
        // Show connectivity warning only if all three failed
        _hasConnectivity = results.any((ok) => ok);
      });
    }
  }

  Future<bool> _fetchDollar() async {
    try {
      final uri = Uri.parse('https://economia.awesomeapi.com.br/json/last/USD-BRL');
      final res = await http.get(uri).timeout(const Duration(seconds: 12));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        final usdbrl = data['USDBRL'] as Map<String, dynamic>;
        final bid = double.parse(usdbrl['bid'] as String);
        final pct = double.parse(usdbrl['pctChange'] as String);
        final sign = pct >= 0 ? '+' : '';
        if (mounted) {
          setState(() {
            _dollar = QuoteData(
              value: 'R\$ ${bid.toStringAsFixed(2).replaceAll('.', ',')}',
              change: '$sign${pct.toStringAsFixed(2)}% hoje',
              isPositive: pct >= 0,
            );
          });
        }
        return true;
      }
    } catch (_) {
      // Fail silently — show placeholder in the card
    }
    return false;
  }

  Future<bool> _fetchBtc() async {
    try {
      final uri = Uri.parse(
        'https://api.coingecko.com/api/v3/simple/price'
        '?ids=bitcoin&vs_currencies=usd&include_24hr_change=true',
      );
      final res = await http.get(
        uri,
        headers: {'Accept': 'application/json'},
      ).timeout(const Duration(seconds: 12));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        final btcData = data['bitcoin'] as Map<String, dynamic>;
        final price = (btcData['usd'] as num).toDouble();
        final change = (btcData['usd_24h_change'] as num).toDouble();
        final sign = change >= 0 ? '+' : '';
        if (mounted) {
          setState(() {
            _btc = QuoteData(
              value: 'US\$ ${_formatPrice(price)}',
              change: '$sign${change.toStringAsFixed(1)}% hoje',
              isPositive: change >= 0,
            );
          });
        }
        return true;
      }
    } catch (_) {
      // Fail silently — show placeholder in the card
    }
    return false;
  }

  Future<bool> _fetchWeather() async {
    try {
      // Quirinópolis, GO
      final uri = Uri.parse(
        'https://api.open-meteo.com/v1/forecast'
        '?latitude=-18.4486&longitude=-50.4519'
        '&current=temperature_2m,weathercode,relative_humidity_2m'
        '&daily=temperature_2m_max,temperature_2m_min'
        '&timezone=America%2FSao_Paulo'
        '&forecast_days=1',
      );
      final res = await http.get(uri).timeout(const Duration(seconds: 12));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        final current = data['current'] as Map<String, dynamic>;
        final daily = data['daily'] as Map<String, dynamic>;
        final code = current['weathercode'] as int;
        if (mounted) {
          setState(() {
            _weather = WeatherData(
              tempCurrent: (current['temperature_2m'] as num).toDouble(),
              humidity: (current['relative_humidity_2m'] as num).toInt(),
              tempMax: (daily['temperature_2m_max'] as List).first as double,
              tempMin: (daily['temperature_2m_min'] as List).first as double,
              description: _weatherDescription(code),
            );
          });
        }
        return true;
      }
    } catch (_) {
      // Fail silently — weather card will be hidden
    }
    return false;
  }

  String _formatPrice(double price) {
    final parts = price.toStringAsFixed(0).split('');
    final result = StringBuffer();
    for (var i = 0; i < parts.length; i++) {
      if (i > 0 && (parts.length - i) % 3 == 0) result.write('.');
      result.write(parts[i]);
    }
    return result.toString();
  }

  String _weatherDescription(int code) {
    if (code == 0) return 'Céu limpo';
    if (code <= 2) return 'Parcialmente nublado';
    if (code == 3) return 'Nublado';
    if (code <= 49) return 'Neblina';
    if (code <= 59) return 'Garoa';
    if (code <= 69) return 'Chuva';
    if (code <= 79) return 'Neve';
    if (code <= 84) return 'Aguaceiro';
    return 'Tempestade';
  }

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final titleStyle = Theme.of(context).textTheme.titleMedium?.copyWith(
      fontWeight: FontWeight.w700,
      letterSpacing: 0.6,
    );

    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadData,
          color: const Color(0xFFE8B4B8),
          backgroundColor: const Color(0xFF1A1A2E),
          child: CustomScrollView(
            slivers: [
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // ── Header ──────────────────────────────────────────
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
                      if (_loading) ...[
                        const SizedBox(height: 16),
                        const LinearProgressIndicator(
                          backgroundColor: Colors.transparent,
                          color: Color(0xFFE8B4B8),
                        ),
                      ] else if (!_hasConnectivity) ...[
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.orange.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: Colors.orange.withValues(alpha: 0.3)),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.wifi_off, color: Colors.orange, size: 16),
                              const SizedBox(width: 8),
                              const Expanded(
                                child: Text(
                                  'Sem conexão — dados podem estar desatualizados.',
                                  style: TextStyle(color: Colors.orange, fontSize: 12),
                                ),
                              ),
                              GestureDetector(
                                onTap: _loadData,
                                child: const Icon(Icons.refresh, color: Colors.orange, size: 16),
                              ),
                            ],
                          ),
                        ),
                      ],

                      // ── Stats grid (always visible) ──────────────────
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
                        children: [
                          const StatCard(
                            label: 'Saldo Total',
                            value: 'R\$ 54.920',
                            subtitle: 'Carteira BR + US',
                            accentColor: Color(0xFF82B8A0),
                          ),
                          const StatCard(
                            label: 'Meta Mensal',
                            value: '78%',
                            subtitle: 'R\$ 7.800 / R\$ 10.000',
                            accentColor: Color(0xFFE8B4B8),
                          ),
                          StatCard(
                            label: 'Dólar',
                            value: _loading ? '...' : (_dollar?.value ?? '—'),
                            subtitle: _dollar?.change ?? '',
                            accentColor: const Color(0xFFA5B4C4),
                            subtitlePositive: _dollar?.isPositive,
                          ),
                          StatCard(
                            label: 'BTC',
                            value: _loading ? '...' : (_btc?.value ?? '—'),
                            subtitle: _btc?.change ?? '',
                            accentColor: const Color(0xFFD4B482),
                            subtitlePositive: _btc?.isPositive,
                          ),
                        ],
                      ),

                      // ── Weather ──────────────────────────────────────
                      if (_weather != null) ...[
                        const SizedBox(height: 24),
                        Text('Clima — Quirinópolis, GO', style: titleStyle),
                        const SizedBox(height: 12),
                        WeatherCard(weather: _weather!),
                      ],

                      // ── News ─────────────────────────────────────────
                      const SizedBox(height: 24),
                      Text('Notícias', style: titleStyle),
                      const SizedBox(height: 10),
                      ...List.generate(_newsItems.length, (i) => Padding(
                        padding: EdgeInsets.only(bottom: i < _newsItems.length - 1 ? 10 : 0),
                        child: NewsCard(
                          title: _newsItems[i].title,
                          source: _newsItems[i].source,
                        ),
                      )),

                      // ── Media ─────────────────────────────────────────
                      const SizedBox(height: 24),
                      Text('Filmes e séries', style: titleStyle),
                      const SizedBox(height: 12),
                      SizedBox(
                        height: 180,
                        child: ListView.builder(
                          scrollDirection: Axis.horizontal,
                          itemCount: _mediaItems.length,
                          itemBuilder: (_, i) => MediaCard(
                            title: _mediaItems[i].title,
                            genre: _mediaItems[i].genre,
                            rating: _mediaItems[i].rating,
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Widgets ─────────────────────────────────────────────────────────────────

class StatCard extends StatelessWidget {
  const StatCard({
    required this.label,
    required this.value,
    required this.subtitle,
    required this.accentColor,
    this.subtitlePositive,
    super.key,
  });

  final String label;
  final String value;
  final String subtitle;
  final Color accentColor;
  final bool? subtitlePositive;

  @override
  Widget build(BuildContext context) {
    Color subtitleColor = Colors.white70;
    if (subtitlePositive == true) subtitleColor = const Color(0xFF82B8A0);
    if (subtitlePositive == false) subtitleColor = const Color(0xFFE8B4B8);

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
                Flexible(
                  child: Text(
                    label,
                    style: Theme.of(context).textTheme.labelLarge,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
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
                color: subtitleColor,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class WeatherCard extends StatelessWidget {
  const WeatherCard({required this.weather, super.key});

  final WeatherData weather;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${weather.tempCurrent.toStringAsFixed(0)}°C',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    weather.description,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.white70,
                    ),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${weather.tempMax.toStringAsFixed(0)}° / ${weather.tempMin.toStringAsFixed(0)}°',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  'Umidade: ${weather.humidity}%',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.white70,
                  ),
                ),
              ],
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
