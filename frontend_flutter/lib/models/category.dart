class Category {
  final int id;
  final String name;
  final int? user;
  final String description;
  final bool isIncome;
  final String color;
  final DateTime createdAt;

  Category({
    required this.id,
    required this.name,
    this.user,
    required this.description,
    required this.isIncome,
    required this.color,
    required this.createdAt,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] as int,
      name: json['name'] as String,
      user: json['user'] as int?,
      description: json['description'] as String? ?? '',
      isIncome: json['is_income'] as bool? ?? false,
      color: json['color'] as String? ?? '#9E9E9E', // Default grey color
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'user': user,
      'description': description,
      'is_income': isIncome,
      'color': color,
    };
  }
}
