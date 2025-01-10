import 'package:dio/dio.dart';
import 'package:logging/logging.dart';
import 'package:shared_preferences/shared_preferences.dart';

final log = Logger("ApiClient");

class ApiClient {
  final Dio _dio;
  int retryCount = 0;
  static const maxRetries = 3;

  final SharedPreferencesAsync prefs;
  
  ApiClient(SharedPreferencesAsync sharedPreferences, {String baseUrl = "http://localhost:8000/api"})
      : _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 3),
        )),
        prefs = sharedPreferences
  {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        // Логика перед отправкой запроса
        log.info('Запрос: ${options.method} ${options.path} ${options.headers}');
        return handler.next(options);
      },
      onError: (error, handler) async {
        log.info('Запрос: ${error.requestOptions.method} ${error.requestOptions.path} ${error.requestOptions.headers}');
        // Логика обработки ошибок
        if (error.response?.statusCode == 401) {
          if (retryCount >= maxRetries) {
            log.severe('Достигнут лимит повторных попыток. Прекращение.');
            return handler.reject(error); // Прерываем обработку
          }
          retryCount++;

          log.warning('Токен истёк. идет процесс обновления...');
          final success = await refreshAccessToken();
          if (success) {
            log.info("Старый ${error.requestOptions.headers['Authorization']} : Новый ${_dio.options.headers['Authorization']}");
            error.requestOptions.headers['Authorization'] = _dio.options.headers['Authorization'];
            log.info("Заменилось? ${error.requestOptions.headers['Authorization'] != _dio.options.headers['Authorization']}");
            final retryResponse = await _dio.request(
              error.requestOptions.path,
              options: Options(
                method: error.requestOptions.method,
                headers: error.requestOptions.headers,
              ),
              data: error.requestOptions.data,
              queryParameters: error.requestOptions.queryParameters,
            );
            retryCount = 0;
            return handler.resolve(retryResponse);
          } else {
            log.severe('Не удалось обновить токен.');

            retryCount = 0;
            return handler.reject(error);
          }
        }
        return handler.next(error);
      },
      onResponse: (response, handler) {
        // Логика обработки ответа
        log.fine('Ответ: ${response.statusCode}');
        return handler.next(response);
      },
    ));
  }

  Dio get client => _dio;

  void addToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
    log.info('Access token установлен');
  }

  void removeToken() {
    _dio.options.headers.remove('Authorization');
    log.info('Access token очищен');
  }

  Future<bool> refreshAccessToken() async {
    try {
      final refreshToken = await prefs.getString('refresh_token');
      if (refreshToken == null) {
        log.severe('Refresh token отсутствует');
        return false;
      }

      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      final String newAccessToken = response.data['access_token'];
      addToken(newAccessToken);
      await prefs.setString('access_token', newAccessToken);
      log.info('Access token успешно обновлён $newAccessToken');
      return true;
    } catch (e) {
      log.severe('Ошибка обновления access_token: $e');
      return false;
    }
  }
}
