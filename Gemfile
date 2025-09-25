source 'https://rubygems.org'

# Jekyll と GitHub Pages
gem 'jekyll', '~> 4.3'
gem 'github-pages', group: :jekyll_plugins

# 必須プラグイン
group :jekyll_plugins do
  gem 'jekyll-feed'
  gem 'jekyll-sitemap'
  gem 'jekyll-seo-tag'
  gem 'jekyll-relative-links'
  gem 'jekyll-optional-front-matter'
  gem 'jekyll-redirect-from'
  gem 'jekyll-default-layout'
end

# 開発・テスト用ツール
group :development, :test do
  gem 'html-proofer'
  gem 'nokogiri'
end

# プラットフォーム固有
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Windows でのファイル監視
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]

# JRuby での HTTP パーサー
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]
