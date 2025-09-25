source 'https://rubygems.org'

# Specify Ruby version for compatibility
ruby '>= 3.0'

# GitHub Pages
gem 'github-pages', group: :jekyll_plugins

# Ruby compatibility
gem 'csv'
gem 'base64'  # Ruby 3.4+ compatibility

# GitHub Pages に含まれるプラグインは個別指定不要
# _config.yml の plugins 設定で有効化

# 開発・テスト用ツール
group :development, :test do
  gem 'html-proofer'
  gem 'nokogiri'
  gem 'webrick'  # Ruby 3.x でのローカル開発用
end

# プラットフォーム固有（Windows用）
platforms :mingw, :x64_mingw, :mswin do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Windows でのファイル監視
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]

# JRuby での HTTP パーサー
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]
