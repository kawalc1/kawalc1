package id.kawalc1

import com.typesafe.config.ConfigFactory

object Config {
  private val config = ConfigFactory.load()

  object Application {
    val secret: String = config.getString("app.secret")
    val kawalC1Url: String = "https://kawalc1.appspot.com"
    val kawalC1UrlLocal: String = "http://localhost:8000"
  }
}
