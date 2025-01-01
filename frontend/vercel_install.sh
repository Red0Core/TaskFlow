#!/bin/bash

# Установка Flutter SDK, если его нет
if [ ! -d "flutter" ]; then
  git clone https://github.com/flutter/flutter.git;
else
  cd flutter && git pull && cd ..;
fi

# Проверяем и обновляем Flutter
flutter/bin/flutter doctor
flutter/bin/flutter clean
flutter/bin/flutter upgrade
flutter/bin/flutter create . --platforms web
flutter/bin/flutter config --enable-web

# Установка зависимостей
flutter/bin/flutter pub get