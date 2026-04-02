import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:xml/xml.dart';

void main() => runApp(const MeuDashboardApp());

class MeuDashboardApp extends StatelessWidget {
  const MeuDashboardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Meu Dashboard',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFE8B4B8),
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF0F0F1A),
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
  late Future<DashboardBundle> _future;

  static const carteiraBr = {
    'PRIO3.SA': [267.0, 42.38],
    'ALUP11.SA': [159.0, 28.79],
    'BBAS3.SA': [236.0, 27.24],
    'MOVI3.SA': [290.0, 6.82],
    'AGRO3.SA': [135.0, 24.98],
    'VALE3.SA': [25.0, 61.38],
    'VAMO3.SA': [226.0, 6.75],
    'BBSE3.SA': [19.0, 33.30],
    'FESA4.SA': [95.0, 8.14],
    'SLCE3.SA': [31.0, 18.00],
    'TTEN3.SA': [17.0, 14.61],
    'JALL3.SA': [43.0, 4.65],
    'AMOB3.SA': [3.0, 0.0],
    'GARE11.SA': [142.0, 9.10],
    'KNCR11.SA': [9.0, 103.30],
  };

  static const carteiraUs = {
    'VOO': [0.89425, 475.26],
    'QQQ': [0.54245, 456.28],
    'TSLA': [0.52762, 205.26],
    'VNQ': [2.73961, 82.48],
    'OKLO': [2.0, 9.75],
    'VT': [1.0785, 112.68],
    'VTI': [0.43415, 264.89],
    'SLYV': [1.42787, 80.54],
    'GOOGL': [0.32828, 174.61],
    'IWD': [0.34465, 174.09],
    'DIA': [0.1373, 400.58],
    'DVY': [0.46175, 121.34],
    'META': [0.08487, 541.77],
    'BLK': [0.04487, 891.02],
    'DE': [0.10018, 399.28],
    'NVDA': [0.2276, 87.79],
    'CAT': [0.07084, 352.91],
    'AMD': [0.19059, 157.41],
    'NUE': [0.14525, 172.12],
    'COP': [0.24956, 120.21],
    'DTE': [0.12989, 115.48],
    'MSFT': [0.02586, 409.90],
    'GLD': [0.08304, 240.85],
    'NXE': [3.32257, 7.52],
    'XOM': [0.33901, 117.99],
    'SPY': [0.0546, 549.27],
    'JNJ': [0.13323, 150.12],
    'MPC': [0.14027, 178.23],
    'AMZN': [0.05482, 182.42],
    'DUK': [0.09776, 102.29],
    'NEE': [0.13274, 75.34],
    'DVN': [0.26214, 38.15],
    'JPM': [0.02529, 197.71],
    'MAGS': [0.09928, 54.19],
    'INTR': [0.77762, 6.43],
  };

  static const topUs = ['VOO', 'QQQ', 'TSLA', 'OKLO', 'GOOGL'];

  @override
  void initState() {
    super.initState();
    _future = _loadDashboard();
  }

  Future<DashboardBundle> _loadDashboard() async {
    final symbols = {
      ...carteiraBr.keys,
      ...carteiraUs.keys,
      'USDBRL=X',
      '^BVSP',
      'BTC-USD',
      'GC=F',
      'CL=F',
      'ZS=F',
      'ZC=F',
      'SOXX',
    }.toList();

    final quoteEntries = await Future.wait(symbols.map((s) async => MapEntry(s, await _fetchQuote(s))));
    final quotes = {for (final e in quoteEntries) e.key: e.value};

    final usd = quotes['USDBRL=X']?.price ?? 5.5;
    final usdPrev = quotes['USDBRL=X']?.previous ?? usd;

    final brKpi = _calculateBr(carteiraBr, quotes);
    final usKpi = _calculateUs(carteiraUs, quotes, usd, usdPrev);

    final weatherNowFuture = _getWeather(-18.4486, -50.4519);
    final weatherNow2Future = _getWeather(-10.1264, -36.1756);
    final forecastQFuture = _getForecast(-18.4486, -50.4519);
    final forecastCFuture = _getForecast(-10.1264, -36.1756);

    final newsAgroFuture = _getNews('safra soja milho algodão Brasil');
    final newsDefFuture = _getNews('defensivos agrícolas herbicida inseticida Brasil');
    final newsIaFuture = _getNews('inteligência artificial tecnologia');
    final newsAlFuture = _getNews('Coruripe Alagoas');
    final newsGoFuture = _getNews('Quirinópolis Goiás');

    final mediaFuture = _getTmdbTrending();

    final weatherNow = await weatherNowFuture;
    final weatherNow2 = await weatherNow2Future;

    return DashboardBundle(
      quotes: quotes,
      brKpi: brKpi,
      usKpi: usKpi,
      weatherQ: weatherNow,
      weatherC: weatherNow2,
      forecastQ: await forecastQFuture,
      forecastC: await forecastCFuture,
      newsAgro: await newsAgroFuture,
      newsDef: await newsDefFuture,
      newsIa: await newsIaFuture,
      newsAl: await newsAlFuture,
      newsGo: await newsGoFuture,
      media: await mediaFuture,
      usd: usd,
    );
  }

  PortfolioKpi _calculateBr(Map<String, List<double>> carteira, Map<String, QuoteData> quotes) {
    double variacaoDia = 0;
    double patrimonio = 0;
    double custo = 0;

    for (final e in carteira.entries) {
      final q = quotes[e.key];
      if (q == null || q.price == null || q.previous == null) continue;
      final qtd = e.value[0];
      final pm = e.value[1];
      variacaoDia += (q.price! - q.previous!) * qtd;
      patrimonio += q.price! * qtd;
      custo += pm * qtd;
    }

    return PortfolioKpi(variacaoDia: variacaoDia, patrimonio: patrimonio, lucro: patrimonio - custo);
  }

  PortfolioKpi _calculateUs(
    Map<String, List<double>> carteira,
    Map<String, QuoteData> quotes,
    double usd,
    double usdPrev,
  ) {
    double variacaoDiaBr = 0;
    double patrimonioUsd = 0;
    double custoUsd = 0;

    for (final e in carteira.entries) {
      final q = quotes[e.key];
      if (q == null || q.price == null || q.previous == null) continue;
      final qtd = e.value[0];
      final pm = e.value[1];
      variacaoDiaBr += ((q.price! * qtd) * usd) - ((q.previous! * qtd) * usdPrev);
      patrimonioUsd += q.price! * qtd;
      custoUsd += pm * qtd;
    }

    return PortfolioKpi(
      variacaoDia: variacaoDiaBr,
      patrimonio: patrimonioUsd * usd,
      lucro: (patrimonioUsd - custoUsd) * usd,
    );
  }

  Future<QuoteData> _fetchQuote(String symbol) async {
    final uri = Uri.parse(
      'https://query1.finance.yahoo.com/v8/finance/chart/${Uri.encodeComponent(symbol)}?interval=1d&range=5d',
    );
    try {
      final resp = await http.get(uri).timeout(const Duration(seconds: 8));
      if (resp.statusCode != 200) return const QuoteData(symbol: '', name: '', price: null, previous: null);
      final map = jsonDecode(resp.body) as Map<String, dynamic>;
      final result = ((map['chart'] as Map<String, dynamic>)['result'] as List).first as Map<String, dynamic>;
      final meta = result['meta'] as Map<String, dynamic>;
      return QuoteData(
        symbol: symbol,
        name: (meta['symbol'] ?? symbol).toString(),
        price: (meta['regularMarketPrice'] as num?)?.toDouble(),
        previous: (meta['previousClose'] as num?)?.toDouble(),
      );
    } catch (_) {
      return QuoteData(symbol: symbol, name: symbol, price: null, previous: null);
    }
  }

  Future<WeatherNow> _getWeather(double lat, double lon) async {
    final uri = Uri.parse(
      'https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation&timezone=America/Sao_Paulo',
    );
    try {
      final resp = await http.get(uri).timeout(const Duration(seconds: 8));
      if (resp.statusCode != 200) return const WeatherNow.error();
      final map = jsonDecode(resp.body) as Map<String, dynamic>;
      final c = map['current'] as Map<String, dynamic>?;
      if (c == null) return const WeatherNow.error();
      return WeatherNow(
        temp: (c['temperature_2m'] as num?)?.toDouble(),
        wind: (c['wind_speed_10m'] as num?)?.toDouble(),
        humidity: (c['relative_humidity_2m'] as num?)?.toInt(),
        rain: (c['precipitation'] as num?)?.toDouble(),
        hasError: false,
      );
    } catch (_) {
      return const WeatherNow.error();
    }
  }

  Future<List<DailyForecast>> _getForecast(double lat, double lon) async {
    final uri = Uri.parse(
      'https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=America/Sao_Paulo&forecast_days=6',
    );
    try {
      final resp = await http.get(uri).timeout(const Duration(seconds: 8));
      if (resp.statusCode != 200) return [];
      final map = jsonDecode(resp.body) as Map<String, dynamic>;
      final daily = map['daily'] as Map<String, dynamic>?;
      if (daily == null) return [];
      final dates = (daily['time'] as List<dynamic>? ?? []);
      final maxs = (daily['temperature_2m_max'] as List<dynamic>? ?? []);
      final mins = (daily['temperature_2m_min'] as List<dynamic>? ?? []);
      final rains = (daily['precipitation_probability_max'] as List<dynamic>? ?? []);
      final list = <DailyForecast>[];
      for (var i = 1; i < dates.length && i < 6; i++) {
        list.add(
          DailyForecast(
            day: dates[i].toString().substring(5),
            max: (maxs[i] as num?)?.toDouble() ?? 0,
            min: (mins[i] as num?)?.toDouble() ?? 0,
            rainProb: (rains[i] as num?)?.toDouble() ?? 0,
          ),
        );
      }
      return list;
    } catch (_) {
      return [];
    }
  }

  Future<List<NewsItem>> _getNews(String query) async {
    final encoded = Uri.encodeComponent(query);
    final uri = Uri.parse('https://news.google.com/rss/search?q=$encoded&hl=pt-BR&gl=BR&ceid=BR:pt-419');
    try {
      final resp = await http.get(uri).timeout(const Duration(seconds: 8));
      if (resp.statusCode != 200) return [];
      final xml = XmlDocument.parse(resp.body);
      return xml.findAllElements('item').take(4).map((e) {
        return NewsItem(
          title: e.getElement('title')?.innerText ?? 'Sem título',
          link: e.getElement('link')?.innerText ?? '',
        );
      }).toList();
    } catch (_) {
      return [];
    }
  }

  Future<List<MediaItem>> _getTmdbTrending() async {
    const token =
        'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NzhlZTAxMTg0NmZkNGEzODFlMjE5NzIxNDA3ZTcxMyIsIm5iZiI6MTc2OTI4NzY2NS41NDQsInN1YiI6IjY5NzUyZmYxMjBjYTQ5ZjZiOGFlMmYzOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.5sSTiI-dCh5kfrqAFgGRLS4Ba-X_zv0twE6KnRDjf0g';
    final headers = {'accept': 'application/json', 'Authorization': 'Bearer $token'};
    final media = <MediaItem>[];

    try {
      final m = await http
          .get(Uri.parse('https://api.themoviedb.org/3/trending/movie/week?language=pt-BR'), headers: headers)
          .timeout(const Duration(seconds: 10));
      if (m.statusCode == 200) {
        final list = ((jsonDecode(m.body) as Map<String, dynamic>)['results'] as List<dynamic>? ?? []).take(4);
        media.addAll(list.map((e) => MediaItem(title: e['title']?.toString() ?? 'Filme', subtitle: 'Filme')));
      }

      final t = await http
          .get(Uri.parse('https://api.themoviedb.org/3/trending/tv/week?language=pt-BR'), headers: headers)
          .timeout(const Duration(seconds: 10));
      if (t.statusCode == 200) {
        final list = ((jsonDecode(t.body) as Map<String, dynamic>)['results'] as List<dynamic>? ?? []).take(4);
        media.addAll(list.map((e) => MediaItem(title: e['name']?.toString() ?? 'Série', subtitle: 'Série')));
      }
    } catch (_) {
      return [];
    }

    return media;
  }

  void _reload() => setState(() => _future = _loadDashboard());

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard Completo'),
        actions: [IconButton(onPressed: _reload, icon: const Icon(Icons.refresh))],
      ),
      body: FutureBuilder<DashboardBundle>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          final data = snapshot.data;
          if (data == null) return const Center(child: Text('Falha ao carregar'));

          return ListView(
            padding: const EdgeInsets.all(14),
            children: [
              Section('💰 Minha Carteira', child: PortfolioSection(br: data.brKpi, us: data.usKpi)),
              Section('🌤️ Clima agora (Quirinópolis e Coruripe)', child: WeatherRow(a: data.weatherQ, b: data.weatherC)),
              Section('📈 Ações BR em Destaque', child: QuotesGrid(items: carteiraBr.keys.take(6).map((s) => data.quotes[s]).whereType<QuoteData>().toList(), unit: 'R\$')),
              Section('🇺🇸 Top Posições EUA', child: QuotesGrid(items: topUs.map((s) => data.quotes[s]).whereType<QuoteData>().toList(), unit: 'US\$')),
              Section('🌾 Commodities & Ativos', child: QuotesGrid(items: ['USDBRL=X', 'BTC-USD', 'GC=F', 'CL=F', 'ZS=F', 'ZC=F'].map((s) => data.quotes[s]).whereType<QuoteData>().toList(), unit: 'US\$')),
              Section('🚜 Agro & Insumos', child: NewsColumns(left: data.newsAgro, right: data.newsDef)),
              Section('🤖 IA & Tech', child: NewsList(items: data.newsIa)),
              Section('🎬 Filmes & Séries', child: MediaList(items: data.media)),
              Section('📰 Notícias da Região', child: NewsColumns(left: data.newsAl, right: data.newsGo)),
              Section('🌤️ Previsão 5 dias · Quirinópolis', child: ForecastRow(items: data.forecastQ)),
              Section('🌊 Previsão 5 dias · Coruripe', child: ForecastRow(items: data.forecastC)),
            ],
          );
        },
      ),
    );
  }
}

class DashboardBundle {
  const DashboardBundle({
    required this.quotes,
    required this.brKpi,
    required this.usKpi,
    required this.weatherQ,
    required this.weatherC,
    required this.forecastQ,
    required this.forecastC,
    required this.newsAgro,
    required this.newsDef,
    required this.newsIa,
    required this.newsAl,
    required this.newsGo,
    required this.media,
    required this.usd,
  });

  final Map<String, QuoteData> quotes;
  final PortfolioKpi brKpi;
  final PortfolioKpi usKpi;
  final WeatherNow weatherQ;
  final WeatherNow weatherC;
  final List<DailyForecast> forecastQ;
  final List<DailyForecast> forecastC;
  final List<NewsItem> newsAgro;
  final List<NewsItem> newsDef;
  final List<NewsItem> newsIa;
  final List<NewsItem> newsAl;
  final List<NewsItem> newsGo;
  final List<MediaItem> media;
  final double usd;
}

class QuoteData {
  const QuoteData({required this.symbol, required this.name, required this.price, required this.previous});
  final String symbol;
  final String name;
  final double? price;
  final double? previous;

  double get pct {
    if (price == null || previous == null || previous == 0) return 0;
    return ((price! - previous!) / previous!) * 100;
  }
}

class PortfolioKpi {
  const PortfolioKpi({required this.variacaoDia, required this.patrimonio, required this.lucro});
  final double variacaoDia;
  final double patrimonio;
  final double lucro;
}

class WeatherNow {
  const WeatherNow({required this.temp, required this.wind, required this.humidity, required this.rain, required this.hasError});
  const WeatherNow.error()
      : temp = null,
        wind = null,
        humidity = null,
        rain = null,
        hasError = true;

  final double? temp;
  final double? wind;
  final int? humidity;
  final double? rain;
  final bool hasError;
}

class DailyForecast {
  const DailyForecast({required this.day, required this.max, required this.min, required this.rainProb});
  final String day;
  final double max;
  final double min;
  final double rainProb;
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

class Section extends StatelessWidget {
  const Section(this.title, {required this.child, super.key});
  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: 8),
        child,
      ]),
    );
  }
}

class PortfolioSection extends StatelessWidget {
  const PortfolioSection({required this.br, required this.us, super.key});
  final PortfolioKpi br;
  final PortfolioKpi us;

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      crossAxisSpacing: 10,
      mainAxisSpacing: 10,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      children: [
        _kpi('Patrimônio BR', 'R\$ ${br.patrimonio.toStringAsFixed(0)}'),
        _kpi('Variação BR Hoje', 'R\$ ${br.variacaoDia.toStringAsFixed(2)}'),
        _kpi('Patrimônio EUA (R\$)', 'R\$ ${us.patrimonio.toStringAsFixed(0)}'),
        _kpi('Lucro EUA (R\$)', 'R\$ ${us.lucro.toStringAsFixed(2)}'),
      ],
    );
  }

  Widget _kpi(String label, String value) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: const TextStyle(color: Colors.white70)),
          const Spacer(),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        ]),
      ),
    );
  }
}

class WeatherRow extends StatelessWidget {
  const WeatherRow({required this.a, required this.b, super.key});
  final WeatherNow a;
  final WeatherNow b;

  @override
  Widget build(BuildContext context) {
    return Row(children: [Expanded(child: _card('Quirinópolis', a)), const SizedBox(width: 10), Expanded(child: _card('Coruripe', b))]);
  }

  Widget _card(String city, WeatherNow w) {
    if (w.hasError) return Card(child: Padding(padding: const EdgeInsets.all(12), child: Text('$city: sem dados')));
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(city, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text('Temp: ${w.temp?.toStringAsFixed(1) ?? '--'}°C'),
          Text('Umidade: ${w.humidity ?? '--'}%'),
          Text('Vento: ${w.wind?.toStringAsFixed(1) ?? '--'} km/h'),
          Text('Chuva: ${w.rain?.toStringAsFixed(1) ?? '--'} mm'),
        ]),
      ),
    );
  }
}

class QuotesGrid extends StatelessWidget {
  const QuotesGrid({required this.items, required this.unit, super.key});
  final List<QuoteData> items;
  final String unit;

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      itemCount: items.length,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, mainAxisSpacing: 10, crossAxisSpacing: 10, childAspectRatio: 1.3),
      itemBuilder: (_, i) {
        final q = items[i];
        final pct = q.pct;
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(q.symbol, style: const TextStyle(fontWeight: FontWeight.bold)),
              const Spacer(),
              Text('$unit ${(q.price ?? 0).toStringAsFixed(2)}'),
              Text('${pct >= 0 ? '+' : ''}${pct.toStringAsFixed(2)}%', style: TextStyle(color: pct >= 0 ? Colors.greenAccent : Colors.redAccent)),
            ]),
          ),
        );
      },
    );
  }
}

class NewsColumns extends StatelessWidget {
  const NewsColumns({required this.left, required this.right, super.key});
  final List<NewsItem> left;
  final List<NewsItem> right;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: NewsList(items: left)),
        const SizedBox(width: 10),
        Expanded(child: NewsList(items: right)),
      ],
    );
  }
}

class NewsList extends StatelessWidget {
  const NewsList({required this.items, super.key});
  final List<NewsItem> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) return const Card(child: Padding(padding: EdgeInsets.all(12), child: Text('Sem notícias')));
    return Column(children: items.map((n) => Card(child: ListTile(dense: true, title: Text(n.title, maxLines: 2, overflow: TextOverflow.ellipsis), subtitle: Text(n.link, maxLines: 1, overflow: TextOverflow.ellipsis)))).toList());
  }
}

class MediaList extends StatelessWidget {
  const MediaList({required this.items, super.key});
  final List<MediaItem> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) return const Card(child: Padding(padding: EdgeInsets.all(12), child: Text('Sem mídia no momento')));
    return SizedBox(
      height: 150,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) => Container(
          width: 190,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.08), borderRadius: BorderRadius.circular(12), border: Border.all(color: Colors.white24)),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [Text(items[i].title, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.bold)), const SizedBox(height: 6), Text(items[i].subtitle)]),
        ),
      ),
    );
  }
}

class ForecastRow extends StatelessWidget {
  const ForecastRow({required this.items, super.key});
  final List<DailyForecast> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) return const Card(child: Padding(padding: EdgeInsets.all(12), child: Text('Sem previsão')));
    return Row(
      children: items
          .take(5)
          .map((f) => Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(8),
                    child: Column(
                      children: [
                        Text(f.day),
                        const SizedBox(height: 6),
                        Text('↑ ${f.max.toStringAsFixed(0)}°'),
                        Text('↓ ${f.min.toStringAsFixed(0)}°'),
                        Text('💧 ${f.rainProb.toStringAsFixed(0)}%'),
                      ],
                    ),
                  ),
                ),
              ))
          .toList(),
    );
  }
}
