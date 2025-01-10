import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/api/api_client.dart';
import 'package:frontend/api/auth_api.dart';
import 'package:frontend/api/tasks_api.dart';
import 'package:frontend/tasks.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  late ApiClient apiClient;
  late AuthApi authApi;
  late TasksApi tasksApi;

  WidgetsFlutterBinding.ensureInitialized();
  
  group("Task integration tests", () {
    setUp(() async {
      // Настройка реального клиента
      apiClient = ApiClient(baseUrl: 'http://127.0.0.1:8000/api');
      authApi = AuthApi(apiClient);

      // Очистка SharedPreferences перед каждым тестом
      SharedPreferences.setMockInitialValues({});

      // Логинимся или регистрируемся и логинимся
      try {
        await authApi.login('testuser', 'password123');
      } on AuthenticationException {
        await authApi.register('testuser', 'password123');
        await authApi.login('testuser', 'password123');
      }

      tasksApi = TasksApi(apiClient);
    });

    test('Create a task', () async {
      final task = await Task.create('Test Task', 'Test Description', tasksApi);
      // Проверяем, что задача создана
        expect(task.id, isNotNull);
        expect(task.title, equals('Test Task'));
        expect(task.description, equals('Test Description'));
        expect(task.isCompleted, isFalse);
    });

    test('Update a task', () async {
      final task = await Task.create('Initial Task', 'Initial Description', tasksApi);

      // Обновляем задачу
      await task.update(newTitle: 'Updated Task', newDescription: 'Updated Description');

      // Проверяем, что задача обновлена
      final tasks = await Task.fetchAll(tasksApi);
      final updatedTask = tasks.firstWhere((t) => t.id == task.id);

      expect(updatedTask.title, equals('Updated Task'));
      expect(updatedTask.description, equals('Updated Description'));
    });

    test('Delete a task', () async {
      final task = await Task.create('Task to Delete', 'Description', tasksApi);

      // Удаляем задачу
      await task.delete();

      // Проверяем, что задача удалена
      final tasks = await Task.fetchAll(tasksApi);
      expect(tasks.any((t) => t.id == task.id), isFalse);
    });

     test('Fetch all tasks', () async {
      // Удаляем все задачи
      for (final task in await Task.fetchAll(tasksApi)) {
        await task.delete();
      } 

      await Task.create('Task 1', 'Description 1', tasksApi);
      await Task.create('Task 2', 'Description 2', tasksApi);

      // Получаем все задачи
      final tasks = await Task.fetchAll(tasksApi);

      // Проверяем количество задач
      expect(tasks.length, equals(2));
      expect(tasks[0].title, equals('Task 1'));
      expect(tasks[1].title, equals('Task 2'));
    });
  });
}