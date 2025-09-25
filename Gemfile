source 'https://rubygems.org'

# GitHub Pages公式推奨設定
gem 'github-pages', group: :jekyll_plugins

# プラグインは_config.ymlのpluginsセクションで管理
# jekyll-redirect-fromはgithub-pagesに含まれているため不要

# ローカル開発用（Ruby 3.0+で必要）
gem 'webrick', '~> 1.7'

# ローカル開発用パフォーマンス向上（GitHub Pagesでは非対応のため開発環境のみ）
group :development do
  gem 'jekyll-cache'
end
