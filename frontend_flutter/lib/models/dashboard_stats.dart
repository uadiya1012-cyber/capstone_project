class DashboardStats {
  final List<double> monthlyData;
  final List<String> catLabels;
  final List<double> catValues;
  final List<String> budgetLabels;
  final List<double> budgetAllocated;
  final List<double> budgetSpent;
  final double thisMonthTotal;
  final double prevMonthTotal;
  final double monthChangePercent;
  final List<String> top5Labels;
  final List<double> top5Values;
  final double dailyAvg;
  final int totalTxCount;

  DashboardStats({
    required this.monthlyData,
    required this.catLabels,
    required this.catValues,
    required this.budgetLabels,
    required this.budgetAllocated,
    required this.budgetSpent,
    required this.thisMonthTotal,
    required this.prevMonthTotal,
    required this.monthChangePercent,
    required this.top5Labels,
    required this.top5Values,
    required this.dailyAvg,
    required this.totalTxCount,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      monthlyData: (json['monthly_data'] as List? ?? [])
          .map((v) => double.tryParse(v.toString()) ?? 0.0)
          .toList(),
      catLabels: (json['cat_labels'] as List? ?? [])
          .map((v) => v.toString())
          .toList(),
      catValues: (json['cat_values'] as List? ?? [])
          .map((v) => double.tryParse(v.toString()) ?? 0.0)
          .toList(),
      budgetLabels: (json['budget_labels'] as List? ?? [])
          .map((v) => v.toString())
          .toList(),
      budgetAllocated: (json['budget_allocated'] as List? ?? [])
          .map((v) => double.tryParse(v.toString()) ?? 0.0)
          .toList(),
      budgetSpent: (json['budget_spent'] as List? ?? [])
          .map((v) => double.tryParse(v.toString()) ?? 0.0)
          .toList(),
      thisMonthTotal: double.tryParse(json['this_month_total']?.toString() ?? '') ?? 0.0,
      prevMonthTotal: double.tryParse(json['prev_month_total']?.toString() ?? '') ?? 0.0,
      monthChangePercent: double.tryParse(json['month_change_percent']?.toString() ?? '') ?? 0.0,
      top5Labels: (json['top5_labels'] as List? ?? [])
          .map((v) => v.toString())
          .toList(),
      top5Values: (json['top5_values'] as List? ?? [])
          .map((v) => double.tryParse(v.toString()) ?? 0.0)
          .toList(),
      dailyAvg: double.tryParse(json['daily_avg']?.toString() ?? '') ?? 0.0,
      totalTxCount: json['total_tx_count'] as int? ?? 0,
    );
  }
}
