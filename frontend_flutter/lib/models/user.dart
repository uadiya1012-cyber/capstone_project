class User {
  final int id;
  final String username;
  final String email;
  final String role;
  final String? phoneNumber;
  final String? avatar;
  final String currency;
  final double dailyLimit;
  final double monthlySavingsGoal;

  User({
    required this.id,
    required this.username,
    required this.email,
    required this.role,
    this.phoneNumber,
    this.avatar,
    required this.currency,
    required this.dailyLimit,
    required this.monthlySavingsGoal,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      username: json['username'] as String,
      email: json['email'] as String,
      role: json['role'] as String? ?? 'USER',
      phoneNumber: json['phone_number'] as String?,
      avatar: json['avatar'] as String?,
      currency: json['currency'] as String? ?? '₮',
      dailyLimit: double.tryParse(json['daily_limit']?.toString() ?? '') ?? 0.0,
      monthlySavingsGoal: double.tryParse(json['monthly_savings_goal']?.toString() ?? '') ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'role': role,
      'phone_number': phoneNumber,
      'avatar': avatar,
      'currency': currency,
      'daily_limit': dailyLimit,
      'monthly_savings_goal': monthlySavingsGoal,
    };
  }
}
