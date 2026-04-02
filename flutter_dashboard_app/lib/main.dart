import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:xml/xml.dart';

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
      ),
      home: const DashboardPage(),
    );
  }
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  late Future<DashboardData> _future;

  static const _stocksBr = <MarketItem>[
    MarketItem('PETR4', 'PETR4.SA', 'R\$', Color(0xFFE8B4B8)),
    MarketItem('VALE3', 'VALE3.SA', 'R\$', Color(0xFFA5B4C4)),
    MarketItem('ITUB4', 'ITUB4.SA', 'R\$', Color(0xFF82B8A0)),
    MarketItem('BBAS3', 'BBAS3.SA', 'R\$', Color(0xFFD4B482)),
  ];

  static const _stocksUs = <MarketItem>[
    MarketItem('AAPL', 'AAPL', 'US\$', Color(0xFFC4A5D4)),
    MarketItem('MSFT', 'MSFT', 'US\$', Color(0xFFB4D4E8)),
    MarketItem('NVDA', 'NVDA', 'US\$', Color(0xFFE6CF8B)),
    MarketItem('AMZN', 'AMZN', 'US\$', Color(0xFF8BCFD4)),
  ];

  static const _commodities = <MarketItem>[
    MarketItem('Dólar', 'USDBRL=X', 'R\$', Color(0xFF9DB4C6)),
    MarketItem('Bitcoin', 'BTC-USD', 'US\$', Color(0xFFF2C27B)),
    MarketItem('Milho', 'ZC=F', 'US\$', Color(0xFFC6B38D)),
    MarketItem('Soja', 'ZS=F', 'US\$', Color(0xFFB3D49E)),
  ];

  @override
  void initState() {
    super.initState();
    _future = _loadData();
  }

  Future<DashboardData> _loadData() async {
    final weatherFuture = _fetchWeather();
    final brFuture = _fetchQuotes(_stocksBr);
    final usFuture = _fetchQuotes(_stocksUs);
    final commoditiesFuture = _fetchQuotes(_commodities);
    final newsFuture = _fetchNews();
    final mediaFuture = _fetchMedia();

    final values = await Future.wait([
      weatherFuture,
      brFuture,
      usFuture,
      commoditiesFuture,
      newsFuture,
      mediaFuture,
    ]);

    return DashboardData(
      weather: values[0] as WeatherData,
      brStocks: values[1] as List<MarketCardData>,
      usStocks: values[2] as List<MarketCardData>,
      commodities: values[3] as List<MarketCardData>,
      news: values[4] as List<NewsItem>,
      media: values[5] as List<MediaItem>,
    );
  }

  Future<List<MarketCardData>> _fetchQuotes(List<MarketItem> items) async {
    final futures = items.map(_fetchQuote);
    return Future.wait(futures);
  }

  Future<MarketCardData> _fetchQuote(MarketItem item) async {
    final uri = Uri.parse(
      'https://query1.finance.yahoo.com/v8/finance/chart/${Uri.encodeComponent(item.symbol)}?interval=1d&range=5d',
    );

    try {
      final response = await http.get(uri).timeout(const Duration(seconds: 8));
      if (response.statusCode != 200) {
        return MarketCardData.error(item, 'Erro ${response.statusCode}');
      }

      final map = jsonDecode(response.body) as Map<String, dynamic>;
      final result = ((map['chart'] as Map<String, dynamic>)['result'] as List).first
          as Map<String, dynamic>;
      final meta = result['meta'] as Map<String, dynamic>;
      final price = (meta['regularMarketPrice'] as num?)?.toDouble();
      final previous = (meta['previousClose'] as num?)?.toDouble();

      if (price == null || previous == null || previous == 0) {
        return MarketCardData.error(item, 'Sem cotação');
      }

      final change = ((price - previous) / previous) * 100;
      return MarketCardData(
        item: item,
        value: _formatValue(price, item.unit),
        variation: '${change >= 0 ? '+' : ''}${change.toStringAsFixed(2)}%',
        isPositive: change >= 0,
        error: null,
      );
    } catch (_) {
      return MarketCardData.error(item, 'Falha de rede');
    }
  }

  String _formatValue(double value, String unit) {
    if (unit == 'pts') return '${value.toStringAsFixed(0)} pts';
    final decimals = value >= 100 ? 2 : 4;
    return '$unit ${value.toStringAsFixed(decimals)}';
  }

  Future<WeatherData> _fetchWeather() async {
    final uri = Uri.parse(
      'https://api.open-meteo.com/v1/forecast?latitude=-19.7474&longitude=-47.939&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
    );

    try {
      final response = await http.get(uri).timeout(const Duration(seconds: 8));
      if (response.statusCode != 200) {
        return const WeatherData.error();
      }
      final map = jsonDecode(response.body) as Map<String, dynamic>;
      final current = map['current'] as Map<String, dynamic>?;
      if (current == null) return const WeatherData.error();

      return WeatherData(
        temperature: (current['temperature_2m'] as num?)?.toDouble(),
        humidity: (current['relative_humidity_2m'] as num?)?.toInt(),
        wind: (current['wind_speed_10m'] as num?)?.toDouble(),
        code: (current['weather_code'] as num?)?.toInt(),
        hasError: false,
      );
    } catch (_) {
      return const WeatherData.error();
    }
  }

  Future<List<NewsItem>> _fetchNews() async {
    final uri = Uri.parse(
      'https://news.google.com/rss/search?q=agroneg%C3%B3cio+OR+soja+OR+milho+Brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    );

    try {
      final response = await http.get(uri).timeout(const Duration(seconds: 8));
      if (response.statusCode != 200) return [];
      final doc = XmlDocument.parse(response.body);
      final items = doc.findAllElements('item').take(6);
      return items.map((item) {
        final title = item.getElement('title')?.innerText ?? 'Sem título';
        final link = item.getElement('link')?.innerText ?? '';
        return NewsItem(title: title, link: link);
      }).toList();
    } catch (_) {
      return [];
    }
  }

  Future<List<MediaItem>> _fetchMedia() async {
    final movieUri = Uri.parse(
      'https://itunes.apple.com/search?term=filme&media=movie&lang=pt_br&limit=4',
    );
    final tvUri = Uri.parse('https://api.tvmaze.com/shows?page=1');

    try {
      final movieRes = await http.get(movieUri).timeout(const Duration(seconds: 8));
      final tvRes = await http.get(tvUri).timeout(const Duration(seconds: 8));

      final media = <MediaItem>[];
      if (movieRes.statusCode == 200) {
        final map = jsonDecode(movieRes.body) as Map<String, dynamic>;
        final results = (map['results'] as List<dynamic>? ?? []).take(4);
        media.addAll(results.map((m) {
          final row = m as Map<String, dynamic>;
          return MediaItem(
            title: (row['trackName'] ?? 'Filme').toString(),
            subtitle: (row['primaryGenreName'] ?? 'Filme').toString(),
          );
        }));
      }

      if (tvRes.statusCode == 200) {
        final list = (jsonDecode(tvRes.body) as List<dynamic>).take(4);
        media.addAll(list.map((s) {
          final row = s as Map<String, dynamic>;
          return MediaItem(
            title: (row['name'] ?? 'Série').toString(),
            subtitle: ((row['genres'] as List?)?.take(2).join(' / ') ?? 'Série')
                .toString(),
          );
        }));
      }

      return media.take(8).toList();
    } catch (_) {
      return [];
    }
  }

  void _reload() {
    setState(() {
      _future = _loadData();
    });
  }

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final dateText =
        '${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year} ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Meu Dashboard Completo'),
        actions: [
          IconButton(
            onPressed: _reload,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: FutureBuilder<DashboardData>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (!snapshot.hasData) {
            return const Center(child: Text('Erro ao carregar dashboard'));
          }

          final data = snapshot.data!;

          return ListView(
            padding: const EdgeInsets.all(14),
            children: [
              Text('Atualizado em $dateText',
                  style: Theme.of(context)
                      .textTheme
                      .bodyMedium
                      ?.copyWith(color: Colors.white70)),
              const SizedBox(height: 12),
              SectionTitle('🌤️ Clima agora'),
              WeatherCard(data: data.weather),
              const SizedBox(height: 14),
              SectionTitle('🇧🇷 Mercado Brasil'),
              MarketGrid(cards: data.brStocks),
              const SizedBox(height: 14),
              SectionTitle('🇺🇸 Mercado EUA'),
              MarketGrid(cards: data.usStocks),
              const SizedBox(height: 14),
              SectionTitle('🌾 Commodities & Ativos'),
              MarketGrid(cards: data.commodities),
              const SizedBox(height: 14),
              SectionTitle('📰 Notícias'),
              ...data.news.map((n) => NewsTile(item: n)),
              if (data.news.isEmpty) const InfoCard(text: 'Sem notícias no momento.'),
              const SizedBox(height: 14),
              SectionTitle('🎬 Filmes & Séries'),
              if (data.media.isEmpty)
                const InfoCard(text: 'Sem dados de mídia no momento.')
              else
                SizedBox(
                  height: 170,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemBuilder: (context, i) => MediaCard(item: data.media[i]),
                    separatorBuilder: (_, __) => const SizedBox(width: 10),
                    itemCount: data.media.length,
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

class DashboardData {
  const DashboardData({
    required this.weather,
    required this.brStocks,
    required this.usStocks,
    required this.commodities,
    required this.news,
    required this.media,
  });

  final WeatherData weather;
  final List<MarketCardData> brStocks;
  final List<MarketCardData> usStocks;
  final List<MarketCardData> commodities;
  final List<NewsItem> news;
  final List<MediaItem> media;
}

class MarketItem {
  const MarketItem(this.label, this.symbol, this.unit, this.color);
  final String label;
  final String symbol;
  final String unit;
  final Color color;
}

class MarketCardData {
  const MarketCardData({
    required this.item,
    required this.value,
    required this.variation,
    required this.isPositive,
    required this.error,
  });

  factory MarketCardData.error(MarketItem item, String message) => MarketCardData(
        item: item,
        value: '--',
        variation: message,
        isPositive: false,
        error: message,
      );

  final MarketItem item;
  final String value;
  final String variation;
  final bool isPositive;
  final String? error;
}

class WeatherData {
  const WeatherData({
    required this.temperature,
    required this.humidity,
    required this.wind,
    required this.code,
    required this.hasError,
  });

  const WeatherData.error()
      : temperature = null,
        humidity = null,
        wind = null,
        code = null,
        hasError = true;

  final double? temperature;
  final int? humidity;
  final double? wind;
  final int? code;
  final bool hasError;
}

class NewsItem {
  const NewsItem({required this.title, required this.link});
  final String title;
  final String link;
}

class MediaItem {
  const MediaItem({required this.title, required this.subtitle});
  final String title;
  final String subtitle;
}

class SectionTitle extends StatelessWidget {
  const SectionTitle(this.text, {super.key});
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        text,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }
}

class WeatherCard extends StatelessWidget {
  const WeatherCard({required this.data, super.key});
  final WeatherData data;

  @override
  Widget build(BuildContext context) {
    if (data.hasError) return const InfoCard(text: 'Falha ao carregar clima.');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _metric('Temp', '${data.temperature?.toStringAsFixed(1) ?? '--'}°C'),
            _metric('Umidade', '${data.humidity ?? '--'}%'),
            _metric('Vento', '${data.wind?.toStringAsFixed(1) ?? '--'} km/h'),
          ],
        ),
      ),
    );
  }

  Widget _metric(String label, String value) {
    return Column(
      children: [
        Text(label),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
      ],
    );
  }
}

class MarketGrid extends StatelessWidget {
  const MarketGrid({required this.cards, super.key});
  final List<MarketCardData> cards;

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      itemCount: cards.length,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
        childAspectRatio: 1.25,
      ),
      itemBuilder: (context, index) => MarketCard(card: cards[index]),
    );
  }
}

class MarketCard extends StatelessWidget {
  const MarketCard({required this.card, super.key});
  final MarketCardData card;

  @override
  Widget build(BuildContext context) {
    final varColor =
        card.error != null ? Colors.orangeAccent : (card.isPositive ? Colors.greenAccent : Colors.redAccent);

    return Card(
      color: Colors.white.withValues(alpha: 0.08),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(card.item.label, style: Theme.of(context).textTheme.labelLarge),
            const Spacer(),
            Text(card.value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            const SizedBox(height: 4),
            Text(card.variation, style: TextStyle(color: varColor, fontWeight: FontWeight.w600)),
            Text(card.item.symbol, style: const TextStyle(color: Colors.white60, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

class NewsTile extends StatelessWidget {
  const NewsTile({required this.item, super.key});
  final NewsItem item;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(item.title),
        subtitle: Text(item.link, maxLines: 1, overflow: TextOverflow.ellipsis),
      ),
    );
  }
}

class MediaCard extends StatelessWidget {
  const MediaCard({required this.item, super.key});
  final MediaItem item;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 210,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        color: Colors.white.withValues(alpha: 0.08),
        border: Border.all(color: Colors.white24),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            item.title,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 8),
          Text(item.subtitle, maxLines: 2, overflow: TextOverflow.ellipsis),
        ],
      ),
    );
  }
}

class InfoCard extends StatelessWidget {
  const InfoCard({required this.text, super.key});
  final String text;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Text(text),
      ),
    );
  }
}
