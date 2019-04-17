package id.kawalc1

import com.typesafe.config.ConfigFactory

object Config {
  private val config = ConfigFactory.load()

  object Application {
    val secret: String = config.getString("app.secret")
  }
}
