import 'package:flutter/material.dart';
import 'pages/splash_screen.dart';
import 'pages/login_page.dart';
import 'pages/student/student_home_page.dart';
import 'pages/student/student_profile_page.dart';
import 'pages/teacher/teacher_home_page.dart';
import 'pages/admin/admin_home_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Face Recognition Attendance',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const SplashScreen(),
      routes: {
        '/login': (context) => const LoginPage(),
        '/student-home': (context) => const StudentHomePage(),
        '/student-profile': (context) => const StudentProfilePage(),
        '/teacher-home': (context) => const TeacherHomePage(),
        '/admin-home': (context) => const AdminHomePage(),
      },
    );
  }
}
