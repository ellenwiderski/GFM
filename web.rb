class App < Sinatra::Base
  configure :production do
    Sequel.connect ENV['HEROKU_POSTGRESQL_MAROON_URL']
  end

  configure :development do
    Sequel.connect ENV['LOCAL_DATABASE_URL']
  end
end