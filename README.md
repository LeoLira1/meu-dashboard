# meu-dashboard

Este repositório agora tem duas versões do dashboard:

- `streamlit_app.py`: versão web original em Streamlit.
- `flutter_dashboard_app/`: clone visual inicial em Flutter para mobile.

## Flutter app (novo)

O app Flutter já está preparado com layout inspirado no dashboard atual (cards, notícias, mídia e resumo).

### Rodar localmente

1. Instale o Flutter SDK.
2. Entre na pasta do app:

```bash
cd flutter_dashboard_app
```

3. Gere as pastas de plataforma (primeira vez):

```bash
flutter create --platforms android .
```

4. Instale dependências e rode:

```bash
flutter pub get
flutter run
```

## Baixar APK no GitHub Release

Foi adicionado o workflow `.github/workflows/flutter-release.yml` que:


1. dispara quando você publica uma Release no GitHub;
2. gera o APK release do Flutter;
3. anexa o `app-release.apk` na própria Release.

> Observação: este workflow **não** builda em todo `push`; ele roda em `Release publicada` ou manualmente por `Run workflow`.

### Como usar

1. Faça push da branch com esse setup para o GitHub.
2. Crie uma Release (tag, por exemplo `v1.0.0`).
3. Aguarde o GitHub Actions finalizar.
4. Baixe o `app-release.apk` na seção de assets da Release.

Também é possível disparar manualmente via **Actions > Flutter Release APK > Run workflow**.
