import 'package:flutter/material.dart';
import 'package:frontend/api/auth_api.dart';
import 'package:frontend/api/tasks_api.dart';
import 'package:frontend/tasks.dart';
import 'add_task_screen.dart';
import 'edit_task_screen.dart';


class TaskListScreen extends StatefulWidget {
  final TasksApi tasksApi;
  final AuthApi authApi;
  const TaskListScreen({required this.tasksApi, required this.authApi, super.key});
  
  @override
  TaskListScreenState createState() => TaskListScreenState();
}

class TaskListScreenState extends State<TaskListScreen> {
  List<Task> tasks = []; // Инициализируем пустой список
  bool isLoading = false; // Флаг загрузки данных

  @override
  void initState() {
    super.initState();
    loadTasks(); // Загружаем данные при инициализации
  }

  Future<void> logoutDialog(BuildContext context) async {
    final shouldLogout = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Выход'),
        content: const Text('Вы уверены, что хотите выйти?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Отмена'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Выход'),
          ),
        ],
      ),
    );

    if (shouldLogout ?? false) {
      await widget.authApi.logout();
      // Возвращаем пользователя на экран логина
      if (!context.mounted) return;
      Navigator.pushReplacementNamed(context, '/login');
    }
  }

  Future<void> loadTasks() async {
    setState(() {
      isLoading = true;
    });

    try {
      final fetchedTasks = await Task.fetchAll(widget.tasksApi);
      setState(() {
        tasks = fetchedTasks; // Обновляем список задач
      });
    } catch (e) {
      // Обработка ошибки
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка при загрузке задач: $e')),
      );
    } finally {
      setState(() {
        isLoading = false; // Завершаем загрузку
      });
    }
  }

  void refreshTask(Task updatedTask) {
    setState(() {
      final index = tasks.indexWhere((task) => task.id == updatedTask.id);
      if (index != -1) {
        tasks[index] = updatedTask; // Локальное обновление задачи
      }
    });
  }

  void deleteTask(BuildContext context, Task task) {
    final originalTasks = List<Task>.from(tasks); // Копируем текущий список задач

    // Локальное удаление
    setState(() {
      tasks.remove(task);
    });

    // Асинхронное удаление на сервере
    task.delete().catchError((error) {
      // Если ошибка, восстанавливаем список
      setState(() {
        tasks = originalTasks;
      });

      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка при удалении задачи: $error')),
      );
    });
  }


  void toggleTaskCompletion(Task task) {
    final originalIsCompleted = task.isCompleted;

    // Локальное обновление состояния
    setState(() {
      task.isCompleted = !task.isCompleted;
    });

    // Асинхронное обновление на сервере
    task.update(newIsCompleted: task.isCompleted).catchError((error) {
      // Если ошибка, возвращаем старое состояние
      setState(() {
        task.isCompleted = originalIsCompleted;
      });
    
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка при обновлении задачи: $error')),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Список задач'),
          actions: [
            IconButton(
              icon: const Icon(Icons.logout),
              onPressed: () => logoutDialog(context),
            ),
          ],
        ),
        body: isLoading
            ? const Center(child: CircularProgressIndicator()) // Показать индикатор загрузки
            : tasks.isEmpty
                ? const Center(child: Text('Нет задач')) // Показать сообщение, если задач нет
                : ListView.builder(
                    itemCount: tasks.length,
                    itemBuilder: (context, index) {
                      final task = tasks[index];
                      return Card(
                        elevation: 4,
                        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12), // Скругление углов
                        ),
                        child: ListTile(
                          key: ValueKey(task.id),
                          title: Text(
                            task.title,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                          subtitle: Text(
                            task.description,
                            maxLines: 2, // Ограничиваем количество строк
                            overflow: TextOverflow.ellipsis, // Добавляем многоточие, если текст длинный
                            style: const TextStyle(fontSize: 14, color: Colors.grey), // Опционально: уменьшаем шрифт для описания
                          ),
                          trailing: Container(
                            constraints: const BoxConstraints(maxWidth: 120),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Checkbox(
                                  value: task.isCompleted,
                                  onChanged: (bool? value) {
                                      toggleTaskCompletion(task); // Локальное обновление
                                    },
                                ),
                                IconButton(
                                  icon: const Icon(Icons.delete, color: Colors.red),
                                  onPressed: () async {
                                    final confirm = await showDialog<bool>(
                                      context: context,
                                      builder: (context) => AlertDialog(
                                        title: const Text('Удалить задачу?'),
                                        content: const Text('Вы уверены, что хотите удалить задачу?'),
                                        actions: [
                                          TextButton(
                                            onPressed: () => Navigator.pop(context, false),
                                            child: const Text('Отмена'),
                                          ),
                                          TextButton(
                                            onPressed: () => Navigator.pop(context, true),
                                            child: const Text('Удалить'),
                                          ),
                                        ],
                                      ),
                                    );
                                    if (confirm ?? false) {
                                      if (!context.mounted) return;
                                      deleteTask(context, task);
                                    }
                                  },
                                )
                              ],
                            ),
                          ),
                          onTap: () async {
                            await Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => EditTaskScreen(task: task),
                              ),
                            );
      
                            // Локально обновляем интерфейс, так как `task` уже изменён
                            setState(() {});
                          },
                        ),
                      );
                    },
                  ),
        floatingActionButton: FloatingActionButton(
          child: const Icon(Icons.add),
           onPressed: () async {
            final newTask = await Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => AddTaskScreen(tasksApi: widget.tasksApi),
              ),
            );
      
            if (newTask != null) {
              setState(() {
                tasks.add(newTask); // Локальное добавление новой задачи
              });
            }
          },
        ),
      ),
    );
  }
}
