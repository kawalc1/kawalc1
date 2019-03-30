package kawalc1

import io.gatling.core.Predef._
import io.gatling.core.feeder.SourceFeederBuilder
import io.gatling.core.structure.ScenarioBuilder
import io.gatling.http.Predef._
import io.gatling.http.protocol.HttpProtocolBuilder
import io.gatling.http.request.builder.HttpRequestBuilder

import scala.concurrent.duration._

class KawalPemiluSimulation extends Simulation {
  val rps = 4000

  val csvFeeder: SourceFeederBuilder[String] = csv("main_kelurahan.csv").circular

  val httpProtocol: HttpProtocolBuilder = http
    .baseUrl("https://kawal-c1.appspot.com/api/c") // Here is the root for all relative URLs
    .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8") // Here are the common headers
    .acceptEncodingHeader("gzip, deflate")
    .acceptLanguageHeader("en-US,en;q=0.5")
    .userAgentHeader(s"Gatling-$rps")


  val tpsRequest: HttpRequestBuilder =
    http("")
      .get("/${id}")

  val alignScenario: ScenarioBuilder =
    scenario("Fetch tps").feed(csvFeeder)
      .exec(tpsRequest)

  setUp(
    alignScenario.inject(constantUsersPerSec(400) during (2 minutes)).throttle(
      reachRps(rps).in(1 minute),
      holdFor(2 minutes),
    ).protocols(httpProtocol))
}
