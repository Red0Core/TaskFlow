import 'package:flutter/material.dart';
import 'package:frontend/api/api_client.dart';
import 'package:frontend/api/auth_api.dart';
import 'package:frontend/api/tasks_api.dart';
import 'screens/task_list_screen.dart';

void main() async {
  final apiClient = ApiClient();
  final authApi = AuthApi(apiClient);
  await authApi.login("redcore", "password");
  runApp(TaskApp(tasksApi: TasksApi(apiClient)));
}

class TaskApp extends StatelessWidget {
  final TasksApi tasksApi;

  const TaskApp({required this.tasksApi, super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Task Manager',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: TaskListScreen(tasksApi: tasksApi),
    );
  }
}
