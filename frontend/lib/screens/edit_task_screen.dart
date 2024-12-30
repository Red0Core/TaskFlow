import 'package:flutter/material.dart';
import 'package:frontend/tasks.dart';
import 'dart:async';

class EditTaskScreen extends StatefulWidget {
  final Task task;

  const EditTaskScreen({required this.task, super.key});

  @override
  EditTaskScreenState createState() => EditTaskScreenState();
}

class EditTaskScreenState extends State<EditTaskScreen> {
  late TextEditingController _titleController;
  late TextEditingController _descriptionController;

  Timer? _debounce;

  @override
  void initState() {
    super.initState();
    _titleController = TextEditingController(text: widget.task.title);
    _descriptionController = TextEditingController(text: widget.task.description);
  }

  Future<void> _saveTask({String? newTitle, String? newDescription}) async {
    try {
      await widget.task.update(
        newTitle: newTitle ?? widget.task.title,
        newDescription: newDescription ?? widget.task.description,
      );
      // Уведомление об успешном сохранении убрано
    } catch (e) {
      // Показываем уведомление только при ошибке
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка при сохранении изменений: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _debounce?.cancel(); // Отменяем таймер, если он активен
    _titleController.dispose();
    _descriptionController.dispose();
    _saveTask();
    super.dispose();
  }

  void _onChangedDebounced(String? newTitle, String? newDescription) {
    // Отменяем предыдущий таймер
    if (_debounce?.isActive ?? false) {
      _debounce?.cancel();
    }

    // Устанавливаем новый таймер
    _debounce = Timer(const Duration(milliseconds: 500), () {
      _saveTask(newTitle: newTitle, newDescription: newDescription);
    });
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Редактировать задачу')),
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
              onChanged: (value) {
                _onChangedDebounced(value, widget.task.description);
              },
              
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
                textAlignVertical: TextAlignVertical.top,
                onChanged: (value) {
                  _onChangedDebounced(widget.task.title, value);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
