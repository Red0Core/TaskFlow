import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/api/api_client.dart';
import 'package:frontend/api/auth_api.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  late ApiClient apiClient;
  late AuthApi authApi;

  setUp(() {
    // Настройка реального клиента
    apiClient = ApiClient(baseUrl: 'http://127.0.0.1:8000');
    authApi = AuthApi(apiClient);

    // Очистка SharedPreferences перед каждым тестом
    SharedPreferences.setMockInitialValues({});
  });

  test('Успешный логин сохраняет токены', () async {
    // Выполняем реальный запрос к вашему API
    await authApi.login('testuser', 'password123');

    final prefs = await SharedPreferences.getInstance();
    final accessToken = prefs.getString('access_token');
    final refreshToken = prefs.getString('refresh_token');

    expect(accessToken, isNotNull, reason: 'Access token должен быть сохранён');
    expect(refreshToken, isNotNull, reason: 'Refresh token должен быть сохранён');

    log.info('Access Token: $accessToken');
    log.info('Refresh Token: $refreshToken');
  });

  test('Логин с неверными данными возвращает ошибку', () async {
    // Проверяем, что неверный логин вызывает исключение
    expect(
      () async => await authApi.login('testuser', 'wrongpassword'),
      throwsException,
    );
  });
}
