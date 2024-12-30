import 'package:flutter/material.dart';
import '../api/tasks_api.dart';
import 'package:frontend/tasks.dart';

class AddTaskScreen extends StatelessWidget {
  final TasksApi tasksApi;

  AddTaskScreen({required this.tasksApi, super.key});

  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();

  void _saveTask(BuildContext context) async {
    final title = _titleController.text.trim();
    final description = _descriptionController.text.trim();

    if (title.isEmpty || description.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Заполните все поля')));
      return;
    }

    try {
      final newTask = await Task.create(title, description, tasksApi);
      if (!context.mounted) return;
      Navigator.pop(context, newTask); // Возвращаем созданную задачу
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Ошибка: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Добавить задачу')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Название',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: _titleController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Введите название задачи',
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Описание',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Введите описание задачи',
                  alignLabelWithHint: true,
                ),
                maxLines: null, // Позволяет тексту занимать больше строк
                expands: true, // Растягивает текстовое поле
                textAlignVertical: TextAlignVertical.top
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: ElevatedButton(
                onPressed: () => _saveTask(context),
                child: const Text('Сохранить'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
