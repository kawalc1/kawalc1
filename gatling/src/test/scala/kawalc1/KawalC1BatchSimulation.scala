package kawalc1

import io.gatling.core.Predef._
import io.gatling.core.feeder.SourceFeederBuilder
import io.gatling.core.structure.ScenarioBuilder
import io.gatling.http.Predef._
import io.gatling.http.protocol.HttpProtocolBuilder
import io.gatling.http.request.builder.HttpRequestBuilder

import scala.concurrent.duration._

class KawalC1BatchSimulation extends Simulation {
  val rps = 1

  val csvFeeder: SourceFeederBuilder[String] = csv("align_results_201904222135.csv").queue

  val httpProtocol: HttpProtocolBuilder = http
    .baseUrls("http://slim-kawal-c1-bot.dahsy.at:8001/download/") // Here is the root for all relative URLs
    .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8") // Here are the common headers
    .acceptEncodingHeader("gzip, deflate")
    .acceptLanguageHeader("en-US,en;q=0.5")
    .userAgentHeader(s"Gatling-$rps")

  val parameters = "=s1280?storeFiles=true&baseUrl=http://lh3.googleusercontent.com&configFile=digit_config_ppwp_scan_halaman_2_2019.json,digit_config_ppwp_scan_halaman_1_2019.json&featureAlgorithm=akaze"

  def digitizeRequest = exec(http("digitize_1")
    .get("${kelurahan}/${tps}/${photo}" + parameters)
    .check( bodyString.saveAs( "RESPONSE_DATA" ) ))
  .exec( session => {
    println(session("RESPONSE_DATA").as[String])
    session
  })

      val alignScenario: ScenarioBuilder =
    scenario("Digitizing image").feed(csvFeeder)
      .exec(digitizeRequest)

  setUp(
    alignScenario.inject(constantUsersPerSec(30) during (30 minutes)).throttle(
      reachRps(rps).in(2 minutes),
      holdFor(10 minutes),
    ).protocols(httpProtocol))
}
