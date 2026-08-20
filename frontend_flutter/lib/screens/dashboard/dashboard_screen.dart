import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../services/api_service.dart';
import '../../models/dashboard_stats.dart';
import '../../widgets/responsive_layout.dart';
import 'package:intl/intl.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _isLoading = true;
  DashboardStats? _stats;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchStats();
  }

  Future<void> _fetchStats() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final stats = await ApiService.getDashboardStats();
      setState(() {
        _stats = stats;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Мэдээлэл авахад алдаа гарлаа: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currencyFormat = NumberFormat.currency(locale: 'mn_MN', symbol: '₮', decimalDigits: 0);

    return ResponsiveLayout(
      currentIndex: 0,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Хянах самбар'),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _fetchStats,
            ),
          ],
        ),
        body: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _errorMessage != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _fetchStats,
                          child: const Text('Дахин оролдох'),
                        ),
                      ],
                    ),
                  )
                : _stats == null
                    ? const Center(child: Text('Мэдээлэл олдсонгүй'))
                    : RefreshIndicator(
                        onRefresh: _fetchStats,
                        child: SingleChildScrollView(
                          padding: const EdgeInsets.all(20.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Top Summary Cards
                              _buildSummaryRow(currencyFormat),
                              const SizedBox(height: 28),

                              // Charts Section
                              LayoutBuilder(
                                builder: (context, constraints) {
                                  if (constraints.maxWidth >= 700) {
                                    return Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Expanded(flex: 3, child: _buildCategoryBreakdownCard(theme, currencyFormat)),
                                        const SizedBox(width: 20),
                                        Expanded(flex: 4, child: _buildMonthlyTrendCard(theme, currencyFormat)),
                                      ],
                                    );
                                  } else {
                                    return Column(
                                      children: [
                                        _buildCategoryBreakdownCard(theme, currencyFormat),
                                        const SizedBox(height: 20),
                                        _buildMonthlyTrendCard(theme, currencyFormat),
                                      ],
                                    );
                                  }
                                },
                              ),
                              const SizedBox(height: 28),

                              // Quick Actions & Summary
                              _buildQuickActions(theme),
                            ],
                          ),
                        ),
                      ),
      ),
    );
  }

  Widget _buildSummaryRow(NumberFormat format) {
    if (_stats == null) return const SizedBox();
    
    final changeColor = _stats!.monthChangePercent > 0 ? Colors.red : Colors.green;
    final changeSign = _stats!.monthChangePercent > 0 ? '+' : '';

    return LayoutBuilder(
      builder: (context, constraints) {
        final crossAxisCount = constraints.maxWidth >= 600 ? 3 : 1;
        return GridView.count(
          crossAxisCount: crossAxisCount,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          shrinkWrap: true,
          childAspectRatio: crossAxisCount == 3 ? 1.8 : 2.5,
          physics: const NeverScrollableScrollPhysics(),
          children: [
            _buildStatCard(
              'Энэ сарын нийт зарлага',
              format.format(_stats!.thisMonthTotal),
              trailing: Text(
                '$changeSign${_stats!.monthChangePercent}% өмнөх сараас',
                style: TextStyle(color: changeColor, fontSize: 12, fontWeight: FontWeight.bold),
              ),
              icon: Icons.trending_up,
              color: Colors.blue.shade50,
              iconColor: Colors.blue,
            ),
            _buildStatCard(
              'Өдрийн дундаж зарцуулалт',
              format.format(_stats!.dailyAvg),
              icon: Icons.date_range,
              color: Colors.orange.shade50,
              iconColor: Colors.orange,
            ),
            _buildStatCard(
              'Нийт гүйлгээний тоо',
              '${_stats!.totalTxCount} удаа',
              icon: Icons.account_balance_wallet_outlined,
              color: Colors.green.shade50,
              iconColor: Colors.green,
            ),
          ],
        );
      },
    );
  }

  Widget _buildStatCard(String title, String value, {Widget? trailing, required IconData icon, required Color color, required Color iconColor}) {
    final theme = Theme.of(context);
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: iconColor, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(title, style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey[600])),
                  const SizedBox(height: 4),
                  Text(value, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                  if (trailing != null) ...[
                    const SizedBox(height: 4),
                    trailing,
                  ],
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildCategoryBreakdownCard(ThemeData theme, NumberFormat format) {
    if (_stats == null || _stats!.catLabels.isEmpty) return const SizedBox();

    final List<PieChartSectionData> sections = [];
    final colors = [Colors.blue, Colors.green, Colors.orange, Colors.purple, Colors.red, Colors.grey];

    for (int i = 0; i < _stats!.catLabels.length; i++) {
      sections.add(PieChartSectionData(
        value: _stats!.catValues[i],
        title: '',
        radius: 40,
        color: colors[i % colors.length],
      ));
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Топ зарлагын ангилалууд', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            Row(
              children: [
                SizedBox(
                  height: 120,
                  width: 120,
                  child: PieChart(
                    PieChartData(
                      sections: sections,
                      sectionsSpace: 2,
                      centerSpaceRadius: 30,
                    ),
                  ),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: Column(
                    children: List.generate(_stats!.catLabels.length, (i) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4.0),
                        child: Row(
                          children: [
                            Container(
                              width: 12,
                              height: 12,
                              decoration: BoxDecoration(
                                color: colors[i % colors.length],
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _stats!.catLabels[i],
                                style: const TextStyle(fontSize: 12),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Text(
                              format.format(_stats!.catValues[i]),
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      );
                    }),
                  ),
                )
              ],
            )
          ],
        ),
      ),
    );
  }

  Widget _buildMonthlyTrendCard(ThemeData theme, NumberFormat format) {
    if (_stats == null || _stats!.monthlyData.isEmpty) return const SizedBox();

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Энэ оны зардлын чиг хандлага (Сар бүрээр)', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            SizedBox(
              height: 130,
              child: BarChart(
                BarChartData(
                  barGroups: List.generate(_stats!.monthlyData.length, (index) {
                    return BarChartGroupData(
                      x: index,
                      barRods: [
                        BarChartRodData(
                          toY: _stats!.monthlyData[index],
                          color: theme.colorScheme.primary,
                          width: 12,
                          borderRadius: BorderRadius.circular(4),
                        )
                      ],
                    );
                  }),
                  gridData: const FlGridData(show: false),
                  borderData: FlBorderData(show: false),
                  titlesData: FlTitlesData(
                    leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (double value, TitleMeta meta) {
                          const style = TextStyle(fontSize: 9, color: Colors.grey);
                          final monthIndex = value.toInt();
                          if (monthIndex >= 0 && monthIndex < 12) {
                            return SideTitleWidget(
                              axisSide: meta.axisSide,
                              child: Text('${monthIndex + 1} сар', style: style),
                            );
                          }
                          return Container();
                        },
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Хурдан үйлдлүүд', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        Row(
          children: [
            ElevatedButton.icon(
              onPressed: () => Navigator.pushNamed(context, '/expenses/create'),
              icon: const Icon(Icons.add),
              label: const Text('Зардал нэмэх'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            const SizedBox(width: 16),
            OutlinedButton.icon(
              onPressed: () => Navigator.pushNamed(context, '/budgets'),
              icon: const Icon(Icons.pie_chart),
              label: const Text('Төсөв тохируулах'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
          ],
        )
      ],
    );
  }
}
