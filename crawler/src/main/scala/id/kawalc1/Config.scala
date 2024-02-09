package id.kawalc1

import com.typesafe.config.ConfigFactory

object Config {
  private val config = ConfigFactory.load()

  object Application {
    val secret: String     = config.getString("app.secret")
    val kawalC1Url: String = "http://slim-kawal-c1-bot.dahsy.at:8002"
    //    val kawalC1Url: String = "http://43.252.136.101:8001"
    //    val kawalC1Url: String = "http://localhost:8000"
    val kawalC1UrlLocal: String            = "http://localhost:8000"
    val kawalC1AlternativeUrlLocal: String = "http://localhost:8010"
  }
}
