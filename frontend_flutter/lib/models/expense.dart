import 'category.dart';

class Expense {
  final int id;
  final int user;
  final double amount;
  final int? categoryId;
  final Category? categoryDetails;
  final DateTime date;
  final String description;
  final String? receipt;
  final int? budgetId;
  final bool isRecurring;
  final String recurringInterval;
  final DateTime? nextRecurrenceDate;
  final DateTime createdAt;

  Expense({
    required this.id,
    required this.user,
    required this.amount,
    this.categoryId,
    this.categoryDetails,
    required this.date,
    required this.description,
    this.receipt,
    this.budgetId,
    required this.isRecurring,
    required this.recurringInterval,
    this.nextRecurrenceDate,
    required this.createdAt,
  });

  factory Expense.fromJson(Map<String, dynamic> json) {
    return Expense(
      id: json['id'] as int,
      user: json['user'] as int,
      amount: double.tryParse(json['amount']?.toString() ?? '') ?? 0.0,
      categoryId: json['category'] as int?,
      categoryDetails: json['category_details'] != null
          ? Category.fromJson(json['category_details'] as Map<String, dynamic>)
          : null,
      date: DateTime.parse(json['date'] as String),
      description: json['description'] as String? ?? '',
      receipt: json['receipt'] as String?,
      budgetId: json['budget'] as int?,
      isRecurring: json['is_recurring'] as bool? ?? false,
      recurringInterval: json['recurring_interval'] as String? ?? '',
      nextRecurrenceDate: json['next_recurrence_date'] != null
          ? DateTime.parse(json['next_recurrence_date'] as String)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'amount': amount,
      'category': categoryId,
      'date': date.toIso8601String().split('T')[0],
      'description': description,
      'budget': budgetId,
      'is_recurring': isRecurring,
      'recurring_interval': recurringInterval,
    };
  }
}
