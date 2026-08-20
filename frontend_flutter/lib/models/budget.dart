import 'category.dart';

class BudgetAllocation {
  final int id;
  final int budgetId;
  final int categoryId;
  final Category? categoryDetails;
  final double amount;

  BudgetAllocation({
    required this.id,
    required this.budgetId,
    required this.categoryId,
    this.categoryDetails,
    required this.amount,
  });

  factory BudgetAllocation.fromJson(Map<String, dynamic> json) {
    return BudgetAllocation(
      id: json['id'] as int,
      budgetId: json['budget'] as int,
      categoryId: json['category'] as int,
      categoryDetails: json['category_details'] != null
          ? Category.fromJson(json['category_details'] as Map<String, dynamic>)
          : null,
      amount: double.tryParse(json['amount']?.toString() ?? '') ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'budget': budgetId,
      'category': categoryId,
      'amount': amount,
    };
  }
}

class Budget {
  final int id;
  final int user;
  final String name;
  final double totalAmount;
  final DateTime startDate;
  final DateTime endDate;
  final String notes;
  final int? categoryId;
  final Category? categoryDetails;
  final DateTime createdAt;
  final List<BudgetAllocation> allocations;

  Budget({
    required this.id,
    required this.user,
    required this.name,
    required this.totalAmount,
    required this.startDate,
    required this.endDate,
    required this.notes,
    this.categoryId,
    this.categoryDetails,
    required this.createdAt,
    required this.allocations,
  });

  factory Budget.fromJson(Map<String, dynamic> json) {
    var allocList = json['allocations'] as List? ?? [];
    List<BudgetAllocation> allocationObjs = allocList
        .map((a) => BudgetAllocation.fromJson(a as Map<String, dynamic>))
        .toList();

    return Budget(
      id: json['id'] as int,
      user: json['user'] as int,
      name: json['name'] as String,
      totalAmount: double.tryParse(json['total_amount']?.toString() ?? '') ?? 0.0,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      notes: json['notes'] as String? ?? '',
      categoryId: json['category'] as int?,
      categoryDetails: json['category_details'] != null
          ? Category.fromJson(json['category_details'] as Map<String, dynamic>)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      allocations: allocationObjs,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user': user,
      'name': name,
      'total_amount': totalAmount,
      'start_date': startDate.toIso8601String().split('T')[0],
      'end_date': endDate.toIso8601String().split('T')[0],
      'notes': notes,
      'category': categoryId,
    };
  }
}
