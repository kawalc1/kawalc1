package kawalc1

import io.gatling.core.Predef._
import io.gatling.core.structure.ScenarioBuilder
import io.gatling.http.Predef._
import io.gatling.http.protocol.HttpProtocolBuilder
import io.gatling.http.request.builder.HttpRequestBuilder

import scala.concurrent.duration._

class KawalC1Simulation extends Simulation {
  val rps = 20

  val httpProtocol: HttpProtocolBuilder = http
    .baseUrl("https://kawalc1.appspot.com") // Here is the root for all relative URLs
    .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8") // Here are the common headers
    .acceptEncodingHeader("gzip, deflate")
    .acceptLanguageHeader("en-US,en;q=0.5")
    .userAgentHeader(s"Gatling-$rps")


  val digitizeRequest: HttpRequestBuilder =
    http("digitize_1")
      .get("/download/1/13/3.JPG")

  val alignScenario: ScenarioBuilder =
    scenario("Digitizing image")
      .exec(digitizeRequest)

  setUp(
    alignScenario.inject(constantUsersPerSec(100) during (30 minutes)).throttle(
      reachRps(rps).in(1 second),
      holdFor(1 minutes),
    ).protocols(httpProtocol))
}
