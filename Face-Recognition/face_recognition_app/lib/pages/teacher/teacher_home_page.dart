import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../services/auth_service.dart';
import '../../constants/api_constants.dart';
import '../../widgets/custom_loading.dart';
import '../login_page.dart';
import 'teacher_students_page.dart';
import 'teacher_attendance_page.dart';

class TeacherHomePage extends StatefulWidget {
  const TeacherHomePage({super.key});

  @override
  State<TeacherHomePage> createState() => _TeacherHomePageState();
}

class _TeacherHomePageState extends State<TeacherHomePage> {
  final _authService = AuthService();
  bool _isLoading = true;
  Map<String, dynamic>? _userInfo;
  List<dynamic> _myClasses = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final sessionId = await _authService.getSessionId();
      if (sessionId == null) {
        _logout();
        return;
      }

      // Get user info
      final userResponse = await http.get(
        Uri.parse('${ApiConstants.baseUrl}/auth/me'),
        headers: {'session-id': sessionId},
      );

      if (userResponse.statusCode == 200) {
        _userInfo = json.decode(userResponse.body);
      }

      // Get my classes
      final classesResponse = await http.get(
        Uri.parse('${ApiConstants.baseUrl}/teacher/my-classes'),
        headers: {'session-id': sessionId},
      );

      if (classesResponse.statusCode == 200) {
        _myClasses = json.decode(classesResponse.body);
      }
    } catch (e) {
      // ignore: avoid_print
      print('Error loading data: $e');
    }

    setState(() {
      _isLoading = false;
    });
  }

  Future<void> _logout() async {
    await _authService.logout();
    if (mounted) {
      Navigator.of(
        context,
      ).pushReplacement(MaterialPageRoute(builder: (_) => const LoginPage()));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFEAF4FB),
      appBar: AppBar(
        title: const Text('Giáo viên'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadData),
          IconButton(icon: const Icon(Icons.logout), onPressed: _logout),
        ],
      ),
      body: _isLoading
          ? const CustomLoading()
          : RefreshIndicator(
              onRefresh: _loadData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header - User Info
                    Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(20.0),
                        child: Row(
                          children: [
                            CircleAvatar(
                              radius: 40,
                              backgroundColor: Colors.green.shade100,
                              child: Icon(
                                Icons.school,
                                size: 45,
                                color: Colors.green.shade700,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    _userInfo?['full_name'] ?? 'Giáo viên',
                                    style: const TextStyle(
                                      fontSize: 22,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    'Mã GV: ${_userInfo?['teacher_code'] ?? ''}',
                                    style: TextStyle(
                                      fontSize: 16,
                                      color: Colors.grey.shade700,
                                    ),
                                  ),
                                  if (_userInfo?['department'] != null)
                                    Text(
                                      'Khoa: ${_userInfo?['department']}',
                                      style: TextStyle(
                                        fontSize: 14,
                                        color: Colors.grey.shade600,
                                      ),
                                    ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // My Classes
                    Text(
                      'Lớp học của tôi',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue.shade900,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _myClasses.isEmpty
                        ? Card(
                            elevation: 2,
                            child: Padding(
                              padding: const EdgeInsets.all(24.0),
                              child: Center(
                                child: Text(
                                  'Chưa có lớp học nào',
                                  style: TextStyle(
                                    color: Colors.grey.shade600,
                                    fontSize: 16,
                                  ),
                                ),
                              ),
                            ),
                          )
                        : Column(
                            children: _myClasses.map((classItem) {
                              final schedules =
                                  classItem['schedules'] as List? ?? [];
                              return Card(
                                margin: const EdgeInsets.only(bottom: 12),
                                elevation: 3,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: ExpansionTile(
                                  leading: CircleAvatar(
                                    backgroundColor: Colors.blue.shade100,
                                    child: Icon(
                                      Icons.class_,
                                      color: Colors.blue.shade700,
                                    ),
                                  ),
                                  title: Text(
                                    classItem['class_name'] ?? '',
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Mã lớp: ${classItem['class_code'] ?? ''}',
                                      ),
                                      Text(
                                        'Môn: ${classItem['subject_name'] ?? ''}',
                                      ),
                                      Text(
                                        'Số SV: ${classItem['student_count'] ?? 0}',
                                      ),
                                    ],
                                  ),
                                  children: [
                                    if (schedules.isEmpty)
                                      const Padding(
                                        padding: EdgeInsets.all(16.0),
                                        child: Text('Chưa có lịch học'),
                                      )
                                    else
                                      ...schedules.map((schedule) {
                                        final dayNames = [
                                          '',
                                          'Thứ 2',
                                          'Thứ 3',
                                          'Thứ 4',
                                          'Thứ 5',
                                          'Thứ 6',
                                          'Thứ 7',
                                          'CN',
                                        ];
                                        final dayName =
                                            dayNames[schedule['day_of_week'] ??
                                                0];
                                        return ListTile(
                                          leading: Icon(
                                            Icons.calendar_today,
                                            color: Colors.blue.shade600,
                                          ),
                                          title: Text(
                                            '$dayName: ${schedule['start_time']} - ${schedule['end_time']}',
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                          subtitle: Text(
                                            'Phòng: ${schedule['room']} - ${schedule['mode']?.toUpperCase()}',
                                          ),
                                          trailing: Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 10,
                                              vertical: 6,
                                            ),
                                            decoration: BoxDecoration(
                                              color:
                                                  schedule['mode'] == 'online'
                                                  ? Colors.green.shade100
                                                  : Colors.blue.shade100,
                                              borderRadius:
                                                  BorderRadius.circular(8),
                                            ),
                                            child: Text(
                                              schedule['mode'] == 'online'
                                                  ? 'ONLINE'
                                                  : 'OFFLINE',
                                              style: TextStyle(
                                                color:
                                                    schedule['mode'] == 'online'
                                                    ? Colors.green.shade700
                                                    : Colors.blue.shade700,
                                                fontWeight: FontWeight.bold,
                                                fontSize: 11,
                                              ),
                                            ),
                                          ),
                                        );
                                      }),
                                    Padding(
                                      padding: const EdgeInsets.all(8.0),
                                      child: Row(
                                        mainAxisAlignment:
                                            MainAxisAlignment.spaceEvenly,
                                        children: [
                                          ElevatedButton.icon(
                                            onPressed: () async {
                                              try {
                                                final classId =
                                                    classItem['class_id'] is int
                                                    ? classItem['class_id']
                                                    : int.parse(
                                                        classItem['class_id']
                                                            .toString(),
                                                      );
                                                await Navigator.push(
                                                  context,
                                                  MaterialPageRoute(
                                                    builder: (_) =>
                                                        TeacherStudentsPage(
                                                          classId: classId,
                                                          className:
                                                              classItem['class_name'] ??
                                                              '',
                                                        ),
                                                  ),
                                                );
                                              } catch (e) {
                                                if (mounted) {
                                                  ScaffoldMessenger.of(
                                                    context,
                                                  ).showSnackBar(
                                                    SnackBar(
                                                      content: Text('Lỗi: $e'),
                                                    ),
                                                  );
                                                }
                                              }
                                            },
                                            icon: const Icon(Icons.people),
                                            label: const Text('Danh sách SV'),
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor:
                                                  Colors.blue.shade700,
                                              foregroundColor: Colors.white,
                                            ),
                                          ),
                                          ElevatedButton.icon(
                                            onPressed: () async {
                                              try {
                                                final classId =
                                                    classItem['class_id'] is int
                                                    ? classItem['class_id']
                                                    : int.parse(
                                                        classItem['class_id']
                                                            .toString(),
                                                      );
                                                await Navigator.push(
                                                  context,
                                                  MaterialPageRoute(
                                                    builder: (_) =>
                                                        TeacherAttendancePage(
                                                          classId: classId,
                                                          className:
                                                              classItem['class_name'] ??
                                                              '',
                                                          schedules: schedules,
                                                        ),
                                                  ),
                                                );
                                              } catch (e) {
                                                if (mounted) {
                                                  ScaffoldMessenger.of(
                                                    context,
                                                  ).showSnackBar(
                                                    SnackBar(
                                                      content: Text('Lỗi: $e'),
                                                    ),
                                                  );
                                                }
                                              }
                                            },
                                            icon: const Icon(
                                              Icons.check_circle,
                                            ),
                                            label: const Text('Điểm danh'),
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor:
                                                  Colors.green.shade700,
                                              foregroundColor: Colors.white,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            }).toList(),
                          ),
                  ],
                ),
              ),
            ),
    );
  }
}
